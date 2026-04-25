from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import shutil
import uuid
import random

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "items.json"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load DB
def load_items():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Save DB
def save_items(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 🟢 HOME
@app.get("/")
def home():
    return {"status": "Jewellery AI System Running 🔥"}

# 🟢 ADD ITEM (ADMIN)
@app.post("/add-item")
async def add_item(
    file: UploadFile = File(...),
    tag_no: str = Form(...),
    name: str = Form(...),
    quantity: int = Form(...)
):
    items = load_items()

    # unique system id
    sys_id = str(uuid.uuid4())[:8]

    # save image
    file_path = f"{UPLOAD_DIR}/{sys_id}.jpg"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_item = {
        "id": sys_id,
        "tag_no": tag_no,
        "name": name,
        "image": file_path,
        "quantity": quantity
    }

    items.append(new_item)
    save_items(items)

    return {"msg": "Item added", "item": new_item}

# 🟢 SEARCH ITEM (CUSTOMER)
@app.post("/search")
async def search(file: UploadFile = File(...)):
    items = load_items()

    if not items:
        return {"error": "No items in database"}

    # TEMP: random match (Phase 7)
    item = random.choice(items)

    return {
        "match": item
    }
