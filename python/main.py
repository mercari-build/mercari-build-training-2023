import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, HTTPException
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

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items") #POST /itemsのエンドポイントはnameという情報を受け取る
def add_item(name: str = Form(None), category: str = Form(None), image: UploadFile = Form(None)): #add_itemを定義する
    if name is None:
        print("Error!")
        
    logger.info(f"Receive item: {name}, {category}") #[nameの値]と[categoryの値]をログに出力する
    logger.info(f"Can Read Image: {image}") #[imageの値]をログに出力する
    data = image.file.read() #変数「image」に格納された画像ファイルの内容を読み込み、変数「data」に代入する
    hashed = hashlib.sha256(data).hexdigest() #dataをhashedする
    item = {"name": name, "category": category, "image": hashed} #nameとcategoryというパラメーターを持つdictionaryを作成する
    
    #with open(f"{hashed}.jpg", "w") as fp: #hashedで指定された名前で.jpgファイルを作成し、そのファイルにデータを保存する
        #json.dump(data, fp)

    with open(f"items.json","r") as fp: #items.jsonを全てloadする
        all_items = json.loads(fp.read())
    
    item_id = len(all_items["items"]) + 1 #idをall_itemsのデータ数に+1した数と定義する
    logger.info(f"check: {len(all_items)}")
    logger.info(f"check: {all_items}")
    item = {"name": name, "category": category, "image": hashed, "id": item_id} #itemの一番最後にidを追加する

    all_items["items"].append(item) #all_itemsのitemsキーにitemを追加する
    
    with open("items.json","w") as fp: #items.jsonファイルに書き込む
        json.dump(all_items, fp)
       
    return {"message": f"item received: {name}, {category}"}

@app.get("/items")
def get_item(): #登録された商品一覧を取得する
    with open("item.json", "r") as fp: #items.jsonを全てloadする 
        all_items = json.loads(fp.read())
    return all_items #読み取ったitems.jsonを返す

@app.get("/items/{item_id}")
def get_item_id(item_id: int):
    with open("items.json", "r") as fp: #items.jsonを全てloadする 
        items_data = json.loads(fp.read())
    for item in items_data['items']: #json内のアイテムを取得する
        if item['id'] == item_id: #アイテム内のidとitem_idが一致した場合に、
            return item  #ループを抜けて、itemを返す

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