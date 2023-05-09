import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import hashlib

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
    image_filename = image_hash + ".jpg"
    path = "images/" + image_filename
    with open(path, "wb") as f:
        f.write(file)

    # update json
    with open("items.json", "r") as f:
        di = json.load(f)
    if not "items" in di:
        di["items"] = []
    di["items"].append(
        {"name": name, "category": category, "image_filename": image_filename}
    )

    with open("items.json", "w") as f:
        json.dump(di, f)
    return {"message": f"item received: {name}"}


@app.get("/items")
def list_item():
    with open("items.json", "r") as f:
        di = json.load(f)
    return di


@app.get("/items/{item_id}")
def get_item(item_id: int):
    with open("items.json", "r") as f:
        di = json.load(f)
    try:
        return di["items"][item_id]
    except KeyError:
        raise HTTPException(
            status_code=404, detail="'items' key not found in items.json"
        )
    except IndexError:
        raise HTTPException(
            status_code=404, detail=f"item_id {item_id} not found in items.json"
        )


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
