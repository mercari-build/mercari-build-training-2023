import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
logger.setLevel(logging.DEBUG)
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
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
    try:
        with open("items.json", "r") as f:
            data = json.load(f)
            items = data.get("items", [])
        return {"items": items}
    except:
        return {"message": "Items not registered"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
        with open("items.json", "r") as f:
            data = json.load(f)
            items = data.get("items", [])
            found_items = [item for item in items if item.get("id") == item_id]
            if found_items:
                item = found_items[0]
                return {
                    "name": item.get("name"),
                    "category": item.get("category"),
                    "image_filename": item.get("image_filename")
                }
            else:
                return {
                    {"message": "Item not found"}
                }
    except:
        return {"message": "Items not registered"}

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

    # Save in json
    new_item = {"name": name, "category": category, "image_filename": image_filename}
    try:
        with open("items.json", "r") as f:
            data = json.load(f)
            items = data.get("items", [])
            new_item["id"] = len(items)
            items.append(new_item)
    #If "items.json" file doesn't exist, items load only new_item
    except FileNotFoundError:
        new_item["id"] = 0
        items = [new_item]

    with open("items.json", "w") as f:
        json.dump({"items": items}, f)

    return {"message": f"received item:{name} category:{category}"}