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


@app.get("/")
def root():
    return {"message": "Hello, world!"}


@app.post("/items")
def add_item(
    name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)
):
    logger.info(f"Receive item: {name}, {category}, {image.filename}")

    # get hash and save image
    file = image.file.read()
    image_hash = hashlib.sha256(file).hexdigest()
    image_name = image_hash + ".jpg"
    path = "images/" + image_name
    with open(path, "wb") as f:
        f.write(file)

    con = sqlite3.connect("../db/mercari.sqlite3")
    cur = con.cursor()

    # search category id
    cur.execute("insert or ignore into category(name) values(?)", (category,))
    category_id = cur.execute(
        "select id from category where name=?", (category,)
    ).fetchone()[0]
    logger.info(f"Success to get category id: {category_id}")

    # add item
    cur.execute(
        "insert into items(name, category, image_name) values(?, ?, ?)",
        (name, category_id, image_name),
    )
    con.commit()

    return {"message": f"item received: {name}"}


@app.get("/items")
def list_item():
    con = sqlite3.connect("../db/mercari.sqlite3")
    cur = con.cursor()
    res = cur.execute("select * from items")
    con.commit()
    return res.fetchall()


@app.get("/items/{item_id}")
def get_item(item_id: int):
    con = sqlite3.connect("../db/mercari.sqlite3")
    cur = con.cursor()
    res = cur.execute(f"select * from items where id=?", (item_id,))
    con.commit()
    return res.fetchall()


@app.get("/search")
def get_items_with_keyword(keyword: str):
    logger.info(f"Search keyword: {keyword}")

    con = sqlite3.connect("../db/mercari.sqlite3")
    cur = con.cursor()
    res = cur.execute(f"select * from items where name=?", (keyword,))
    con.commit()
    return res.fetchall()


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
