from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json, os, shutil, uuid
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# ---------------- CORS ----------------
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

# ---------------- DB ----------------
def load_items():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE) as f:
        return json.load(f)

def save_items(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- IMAGE VECTOR ----------------
def image_to_vector(path):
    img = Image.open(path).resize((64,64))
    arr = np.array(img).flatten()
    return arr / 255.0

# ---------------- DUPLICATE CHECK ----------------
def is_duplicate(new_vec, items, threshold=0.95):
    for item in items:
        vec = np.array(item["vector"]).reshape(1,-1)
        score = cosine_similarity(new_vec.reshape(1,-1), vec)[0][0]
        if score > threshold:
            return item, score
    return None, None

# ---------------- DESIGN ID ----------------
def generate_design_id(items):
    if not items:
        return "DESIGN001"
    last = items[-1]["design_id"]
    num = int(last.replace("DESIGN",""))
    return f"DESIGN{num+1:03d}"

# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"status":"Phase 12 Running 🚀"}

# ---------------- BULK ADD ----------------
@app.post("/add-bulk")
async def add_bulk(
    file: UploadFile = File(...),
    name: str = Form(...),
    quantity: int = Form(...),
    barcodes: str = Form(...)
):
    items = load_items()

    # save temp image
    temp_path = "temp.jpg"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    vec = image_to_vector(temp_path)

    # check duplicate design
    existing, score = is_duplicate(vec, items)

    barcode_list = barcodes.split(",")

    # -------- EXISTING DESIGN --------
    if existing:
        existing["quantity"] += len(barcode_list)
        existing["tag_series"].extend(barcode_list)

        save_items(items)

        return {
            "msg": "Added to existing design",
            "design_id": existing["design_id"],
            "total_qty": existing["quantity"]
        }

    # -------- NEW DESIGN --------
    design_id = generate_design_id(items)

    sys_id = str(uuid.uuid4())[:8]
    path = f"{UPLOAD_DIR}/{sys_id}.jpg"

    shutil.copy(temp_path, path)

    new_item = {
        "id": sys_id,
        "design_id": design_id,
        "name": name,
        "image": path,
        "quantity": len(barcode_list),
        "tag_series": barcode_list,
        "vector": vec.tolist()
    }

    items.append(new_item)
    save_items(items)

    return {
        "msg": "New design added",
        "design_id": design_id,
        "qty": len(barcode_list)
    }

# ---------------- SEARCH ----------------
@app.post("/search")
async def search(file: UploadFile = File(...)):
    items = load_items()

    if not items:
        return {"error":"No items"}

    temp = "temp.jpg"
    with open(temp,"wb") as f:
        f.write(await file.read())

    query_vec = image_to_vector(temp).reshape(1,-1)

    best=None
    best_score=-1

    for item in items:
        vec = np.array(item["vector"]).reshape(1,-1)
        score = cosine_similarity(query_vec,vec)[0][0]

        if score>best_score:
            best_score=score
            best=item

    return {
        "design": best["design_id"],
        "name": best["name"],
        "qty": best["quantity"],
        "similarity": round(float(best_score),2)
    }

# ---------------- SELL ----------------
@app.post("/sell-item")
def sell_item(tag_no: str = Form(...)):
    items = load_items()

    for item in items:
        if tag_no in item["tag_series"]:

            if item["quantity"] <= 0:
                return {"error":"Out of stock"}

            item["quantity"] -= 1
            item["tag_series"].remove(tag_no)

            save_items(items)

            return {
                "msg":"Sold",
                "remaining":item["quantity"]
            }

    return {"error":"Tag not found"}
