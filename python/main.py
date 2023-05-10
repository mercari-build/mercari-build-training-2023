import hashlib
import json
import os
import os.path
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil

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

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    logger.info(f"Receive item: {name}")
    
    # rename image to hash
    img = image
    if os.path.isfile(img) == True:
        copy = 'copy.jpg'
        shutil.copyfile(img, copy)
        with open(copy, 'rb') as copy_f:    
            sha256 = hashlib.sha256(copy_f.read()).hexdigest()
            ext = ".jpg"
            hash_img = sha256 + ext
            os.rename(copy, f"./images/{hash_img}")
    # error handling
    else:
        logger.info("Image not found")
        hash_img = "..."

    # add log to a json file
    log = { "items" : [
            {"name" : f"{name}",
             "category": f"{category}",
             "image_filename" : f"{hash_img}"
            }]}
    
    # if json file is empty
    if os.path.getsize('items.json')== 0:
        with open('items.json', 'w') as f:
                json.dump(log, f)
    else:
        try:
            with open('items.json', 'r') as f:
                read_data = json.load(f)
                save_data = [read_data, log]
                with open('items.json', 'w') as f:
                    json.dump(save_data, f)
        # Error handling 
        except FileNotFoundError:
            with open('items.json', 'w+') as f:
                json.dump(log, f)

    return ({"message": f"item received: {name}"})

@app.get("/items")
def show_list_of_items():
    try:
        with open('items.json', 'r') as f:
            line = f.read()
            return (line)
        # 標準出力されるとき邪魔なエスケープ文字が入ってしまう
        # （print/logger.infoで出力するときはエスケープ文字は現れない）
    except FileNotFoundError:
        return ("no items")

@app.get("/items/{item_id}")
def show_detail_of_item(item_id):
    with open('items.json', 'r') as f:
        jsn = []
        jsn = json.load(f)
        # Error handling 
        if item_id.isnumeric()==False or int(item_id) < 1 or int(item_id) > len(jsn):
            return("invalid id")
        return(jsn[int(item_id) - 1])

#Optional課題、未着手
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