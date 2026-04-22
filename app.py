from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS fix (VERY IMPORTANT)
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

@app.post("/search")
async def search(file: UploadFile = File(...)):
    contents = await file.read()

    # TEST LOGIC (Phase 3)
    return {
        "filename": file.filename,
        "size": len(contents),
        "message": "File received successfully ✅"
    }
