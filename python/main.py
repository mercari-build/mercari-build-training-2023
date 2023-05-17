import os
import json
import logging
import pathlib
import hashlib
from fastapi import FastAPI, Form, HTTPException, UploadFile, Depends, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
# items_filename = images = pathlib.Path(__file__).parent.resolve() / "items.json"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

def save_items(name, category, image_filename):
    with open('items.json', 'r') as f:
        data = json.load(f)
    with open("items.json", "w") as f:
        data["items"].append({"name": name, "category": category, "image_filename": image_filename})
        json.dump(data, f)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item: {name}")
    logger.info(f"Receive item: {category}")
    logger.info(f"Receive item: {image}")
    image = images / image.filename
    with open(image, "rb") as im:
        image_hash = hashlib.sha256(im.read()).hexdigest()
    image_filename = str(image_hash) + ".jpg"
    save_items(name, category, image_filename)
    return {"message": f"item received: {name}, {category}, {image}"}

@app.get("/items")
def show_item():
    with open("items.json", "r") as f:
        data = json.load(f)
    return data

@app.get("/items/{item_id}")
def item_id(item_id: int):
    with open("items.json", "r") as f:
        data = json.load(f)
    return data["items"][item_id-1]

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