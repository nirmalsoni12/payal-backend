from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "AI Search Running"}

# ✅ Upload + Search both handle करेगा
@app.post("/search")
async def search(file: UploadFile):
    return {
        "result": f"File received: {file.filename}"
    }
