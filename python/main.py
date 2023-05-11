import os
import logging
import pathlib
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
logger.setLevel(logging.DEBUG)
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get("FRONT_URL", "http://localhost:3000") ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def get_items():
    conn = sqlite3.connect("../db/mercari.sqlite3")
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT items.id, items.name, category.name as category, items.image_filename
            FROM items
            JOIN category ON items.category_id = category.id
            """)
        rows = cur.fetchall()
        items = []
        for row in rows:
            item = {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "image_filename": row["image_filename"]
            }
            items.append(item)
        if len(items) == 0:
            return {"message": "Items not found"}
        return {"items": items}
    except:
        raise HTTPException(status_code=500, detail="Failed to search items from the database")
    finally:
        conn.close()

@app.get("/search")
def search_items(keyword: str):
    conn = sqlite3.connect("../db/mercari.sqlite3")
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT items.id, items.name, category.name as category, items.image_filename
            FROM items
            JOIN category ON items.category_id = category.id
            WHERE items.name LIKE ?
            """, ('%' + keyword + '%',))
        rows = cur.fetchall()
        items = []
        for row in rows:
            item = {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "image_filename": row["image_filename"]
            }
            items.append(item)
        if len(items) == 0:
            return {"message": "Item not found"}
        return {"items": items}
    except:
        raise HTTPException(status_code=500, detail="Failed to search items from the database")
    finally:
        conn.close()

@app.get("/image/{image_filename}")
def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")
    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item: {name} category: {category} image: {image.filename}")
    # Save image
    content_image = await image.read()
    hash_object = hashlib.sha256(content_image)
    image_filename = hash_object.hexdigest() + ".jpg"
    path_image_file = "images/"+ image_filename
    with open(path_image_file , "wb") as f:
        f.write(content_image)

    # Save in database
    conn = sqlite3.connect("../db/mercari.sqlite3")
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM category WHERE name=?", (category,))
        result = cur.fetchone()
        if result:
            category_id = result[0]
        # If category doesn't exist, insert a data
        else:
            cur.execute("INSERT INTO category (name) VALUES (?)", (category,))
            category_id = cur.lastrowid
        cur.execute("INSERT INTO items (name, category_id, image_filename) VALUES (?, ?, ?)", (name, category_id, image_filename))
        conn.commit()
    except:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to add item to the database")
    finally:
        conn.close()
    logger.debug(f"received item: {name} category: {category}")
    return {"message": "Succeed to add item"}
