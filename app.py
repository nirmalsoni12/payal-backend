from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Home route
@app.get("/")
def home():
    return {"status": "AI Search Running"}

# ✅ SEARCH route (IMPORTANT)
@app.post("/search")
async def search(file: UploadFile):
    return {"result": "done"}
