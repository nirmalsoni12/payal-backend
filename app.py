from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# ✅ CORS FIX (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

@app.get("/")
def home():
    return {"status": "AI Search Running"}

@app.post("/search")
async def search(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        response = requests.post(API_URL, headers=headers, data=contents)

        return {"result": response.json()}

    except Exception as e:
        return {"error": str(e)}

async function upload() {
  let file = document.getElementById("file").files[0];

  let form = new FormData();
  form.append("file", file);

  try {
    let res = await fetch(API + "/search", {
      method: "POST",
      body: form,
    });

    console.log("STATUS:", res.status);
    let text = await res.text();
    console.log("RESPONSE:", text);

    let data = JSON.parse(text);

    document.getElementById("result").innerText =
      "Prediction: " + data.result[0].label;

  } catch (err) {
    console.error("FETCH ERROR:", err);
    document.getElementById("result").innerText =
      "Error: " + err.message;
  }
}
