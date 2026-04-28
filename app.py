from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json, uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "db.json"
USERS_FILE = "users.json"

# ---------- helpers ----------
def load_db():
    try:
        return json.load(open(DB_FILE))
    except:
        return []

def save_db(data):
    json.dump(data, open(DB_FILE, "w"))

def load_users():
    try:
        return json.load(open(USERS_FILE))
    except:
        return [{"username":"admin","password":"1234@4321"}]

# ---------- LOGIN ----------
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    for u in load_users():
        if u["username"] == username and u["password"] == password:
            return {"success": True}
    return {"success": False}

# ---------- ADD ITEM ----------
@app.post("/add-item")
async def add_item(
    file: UploadFile = File(...),
    name: str = Form(...),
    barcodes: str = Form(...),
    weights: str = Form(...)
):
    db = load_db()

    item_id = str(uuid.uuid4())

    new_item = {
        "id": item_id,
        "name": name,
        "barcodes": barcodes.split(","),
        "weights": json.loads(weights),
        "quantity": len(barcodes.split(",")),
        "image": file.filename
    }

    db.append(new_item)
    save_db(db)

    return {"id": item_id}

# ---------- SEARCH ----------
@app.post("/search")
async def search(file: UploadFile = File(...)):
    db = load_db()

    if db:
        return {"item": db[0], "type": "demo-match"}
    return {"error": "no data"}

# ---------- SALE ----------
@app.post("/sale")
def sale(tag: str = Form(...)):
    db = load_db()

    for item in db:
        if tag in item["barcodes"]:
            item["barcodes"].remove(tag)
            item["quantity"] -= 1
            save_db(db)
            return {"msg": "Sold"}

    return {"error": "Tag not found"}
