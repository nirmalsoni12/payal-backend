from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"
}

@app.post("/search")
async def search(file: UploadFile = File(...)):
    contents = await file.read()

    response = requests.post(API_URL, headers=HEADERS, data=contents)

    try:
        result = response.json()[0]["generated_text"]
    except:
        result = "AI failed to understand image"

    return {
        "result": result
    }
