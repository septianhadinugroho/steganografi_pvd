import os
import io
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

# Import fungsi steganografi Anda
from steg_pvd import embed_image_in_image, extract_image_from_image, embed_text_in_image, extract_text_from_image

# Muat environment variables dari file .env (untuk pengembangan lokal)
load_dotenv()

# Konfigurasi Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Periksa apakah variabel lingkungan ada
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Pastikan SUPABASE_URL dan SUPABASE_KEY ada di environment variables Anda.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "stego-images" # Ganti dengan nama bucket Anda

# Inisialisasi aplikasi FastAPI
app = FastAPI(title="Steganografi PVD API")

# Konfigurasi CORS (Cross-Origin Resource Sharing)
# Ini penting agar API bisa diakses dari frontend yang berjalan di domain lain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Atau ganti dengan domain frontend Anda, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Root Endpoint", description="Endpoint dasar untuk mengecek apakah API berjalan.")
def read_root():
    return {"message": "Selamat datang di API Steganografi PVD"}

@app.post("/embed-image/", summary="Sisipkan Gambar ke Gambar", description="Upload gambar cover dan gambar rahasia untuk disisipkan.")
async def api_embed_image(cover_image: UploadFile = File(...), secret_image: UploadFile = File(...)):
    try:
        cover = Image.open(io.BytesIO(await cover_image.read()))
        secret = Image.open(io.BytesIO(await secret_image.read()))

        # Pastikan ukuran gambar rahasia sama dengan gambar cover
        if secret.size != cover.size:
             secret = secret.resize(cover.size)

        stego_img = embed_image_in_image(cover, secret)

        # Simpan hasil ke BytesIO buffer
        buffer = io.BytesIO()
        stego_img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Upload ke Supabase Storage
        file_path = f"output/{cover_image.filename.split('.')[0]}_stego.png"
        supabase.storage.from_(BUCKET_NAME).upload(file_path, buffer.getvalue(), {"content-type": "image/png", "x-upsert": "true"})
        
        # Dapatkan URL publik
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)

        return {"stego_image_url": public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-image/", summary="Ekstrak Gambar dari Gambar", description="Upload gambar stego untuk mengekstrak gambar rahasia.")
async def api_extract_image(stego_image: UploadFile = File(...), width: int = Form(...), height: int = Form(...)):
    try:
        stego = Image.open(io.BytesIO(await stego_image.read()))
        secret_shape = (height, width, 3)
        secret_img = extract_image_from_image(stego, secret_shape)
        
        buffer = io.BytesIO()
        secret_img.save(buffer, format="PNG")
        buffer.seek(0)

        # Upload ke Supabase
        file_path = f"extracted/{stego_image.filename.split('.')[0]}_extracted.png"
        supabase.storage.from_(BUCKET_NAME).upload(file_path, buffer.getvalue(), {"content-type": "image/png", "x-upsert": "true"})
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)

        return {"extracted_image_url": public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed-text/", summary="Sisipkan Teks ke Gambar", description="Upload gambar cover dan masukkan teks rahasia.")
async def api_embed_text(cover_image: UploadFile = File(...), secret_text: str = Form(...)):
    try:
        cover = Image.open(io.BytesIO(await cover_image.read()))
        stego_img = embed_text_in_image(cover, secret_text)

        buffer = io.BytesIO()
        stego_img.save(buffer, format="PNG")
        buffer.seek(0)

        # Upload ke Supabase
        file_path = f"output/{cover_image.filename.split('.')[0]}_stego_text.png"
        supabase.storage.from_(BUCKET_NAME).upload(file_path, buffer.getvalue(), {"content-type": "image/png", "x-upsert": "true"})
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        
        return {"stego_image_url": public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-text/", summary="Ekstrak Teks dari Gambar", description="Upload gambar stego untuk mendapatkan teks rahasia.")
async def api_extract_text(stego_image: UploadFile = File(...)):
    try:
        stego = Image.open(io.BytesIO(await stego_image.read()))
        secret_text = extract_text_from_image(stego)
        return {"secret_text": secret_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))