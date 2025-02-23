from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("item.html", {"request": request})

@app.post("/upload-chunk")
async def upload_chunk(
    chunkData: UploadFile = File(...),
    fileName: str = Form(...),
    offset: int = Form(...),
    fileSize: int = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, fileName)

    # Read the uploaded chunk
    chunk_data = await chunkData.read()

    # Open the file in binary mode and write the chunk at the correct position
    # with open(file_path, "r+b" if os.path.exists(file_path) else "wb") as f:
    with open(file_path, "wb") as f:
        f.seek(offset)
        f.write(chunk_data)

    # Check if all chunks have been uploaded
    file_stat = os.stat(file_path)
    if file_stat.st_size == fileSize:
        return {"message": "File upload complete"}

    return {"message": "Chunk uploaded successfully"}