import os
import logging
import pathlib
import json
import hashlib
import uuid
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

#import json
with open("items.json") as f:
    items = json.load(f)
items_list = items["items"]

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
async def add_item(name: str = Form(...),
                category: str = Form(...),
                image: UploadFile = File(...)):
    image_bytes = await image.read() # turn the image into a buffer-like object
    image_hashed = hashlib.sha256(image_bytes).hexdigest()  # hash the image
    new_image_name = image_hashed + ".jpg"
    with open(f"./images/{new_image_name}", "wb") as f:
        f.write(image_bytes)  # write the hashed image to a file
    
    id = str(uuid.uuid4()) # generate an id to the new item

    new_item = {
            "id": id,
            "name" : name,
            "category" : category,
            "image" : new_image_name
            }

    items_list.append(new_item)
    #items.append(new_item)
    with open("items.json", "w") as f:
        json.dump(items, f)
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}

@app.get("/items")
def listed_items():
    return items

@app.get("/items/{id}")
def item_details(id: str):
    for item in items_list:
        if item["id"] == id:
            return item

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