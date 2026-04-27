from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import json, os, shutil, uuid
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

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

# ---------------- DUPLICATE ----------------
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

# ---------------- BULK ADD WITH BARCODE DATA ----------------
@app.post("/add-bulk")
async def add_bulk(
    file: UploadFile = File(...),
    name: str = Form(...),
    quantity: int = Form(...),
    barcodes: str = Form(...),
    weights: str = Form(...)  # 🔥 JSON string
):
    items = load_items()

    temp = "temp.jpg"
    with open(temp,"wb") as f:
        f.write(await file.read())

    vec = image_to_vector(temp)
    existing, _ = is_duplicate(vec, items)

    barcode_list = barcodes.split(",")
    weight_data = json.loads(weights)

    # EXISTING
    if existing:
        existing["quantity"] += len(barcode_list)
        existing["tag_series"].extend(barcode_list)

        # add weight info
        existing.setdefault("barcode_data", {}).update(weight_data)

        save_items(items)

        return {"msg":"Added to existing","design":existing["design_id"]}

    # NEW
    design_id = generate_design_id(items)
    sys_id = str(uuid.uuid4())[:8]
    path = f"{UPLOAD_DIR}/{sys_id}.jpg"
    shutil.copy(temp, path)

    new_item = {
        "id": sys_id,
        "design_id": design_id,
        "name": name,
        "image": path,
        "quantity": len(barcode_list),
        "tag_series": barcode_list,
        "barcode_data": weight_data,
        "vector": vec.tolist()
    }

    items.append(new_item)
    save_items(items)

    return {"msg":"New design added","design":design_id}

# ---------------- BARCODE LOOKUP ----------------
@app.get("/get-barcode-info")
def get_barcode_info(code: str):
    items = load_items()

    for item in items:
        if code in item.get("tag_series", []):
            info = item.get("barcode_data", {}).get(code, {})
            return {"found":True,"data":info}

    return {"found":False}
