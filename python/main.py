import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import sqlite3

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
sqlite_path = "../db/mercari.sqlite3"


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@app.get("/")
def root():
    return {"message": "Hello, world!"}

def get_hash_save_image(image: UploadFile):
    file = image.file.read()
    image_hash = hashlib.sha256(file).hexdigest()
    path = images / (image_hash + ".jpg")
    with open(path.resolve(), "wb") as f:
        f.write(file)
    return path

@app.post("/items")
def add_item(
    name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)
):
    logger.info(f"Receive item: {name}, {category}, {image.filename}")

    path = get_hash_save_image(image)

    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()

    # search category id
    cur.execute("insert or ignore into category(name) values(?)", (category,))
    con.commit()
    category_id = cur.execute(
        "select id from category where name=?", (category,)
    ).fetchone()[0]
    logger.info(f"Success to get category id: {category_id}")

    # add item
    cur.execute(
        "insert into items(name, category, image_name) values(?, ?, ?)",
        (name, category_id, path.name),
    )
    con.commit()
    con.close()

    return {"message": f"item received: {name}"}


select_command = """
    select
        items.id,
        items.name,
        category.name as category,
        items.image_name as image_filename
    from items
    left outer join category
    on items.category=category.id
    """


@app.get("/items")
def list_item():
    con = sqlite3.connect(sqlite_path)
    con.row_factory = dict_factory
    cur = con.cursor()
    res = cur.execute(select_command).fetchall()
    con.close()
    return {"items": res}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    con = sqlite3.connect(sqlite_path)
    con.row_factory = dict_factory
    cur = con.cursor()
    res = cur.execute(select_command + "where items.id=?", (item_id,)).fetchone()
    con.close()

    if res is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return res


@app.get("/search")
def get_items_with_keyword(keyword: str):
    logger.info(f"Search keyword: {keyword}")

    con = sqlite3.connect(sqlite_path)
    con.row_factory = dict_factory
    cur = con.cursor()
    res = cur.execute(select_command + "where items.name=?", (keyword,)).fetchall()
    con.close()
    return {"items": res}


@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
