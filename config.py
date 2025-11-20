import os
from dotenv import load_dotenv

# Membaca file .env
load_dotenv()

# --- PERBAIKAN PATH DATABASE ---
# Kita tentukan lokasi project secara absolut
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")

    # 1. Coba ambil dari Environment (untuk Render Postgres)
    # 2. Jika tidak ada, gunakan SQLite dengan ABSOLUTE PATH
    #    (Ini penting agar Gunicorn tidak salah lokasi file)
    db_uri = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")
    
    if not db_uri:
        db_path = os.path.join(BASE_DIR, 'company.db')
        db_uri = f"sqlite:///{db_path}"
        print(f">>> ℹ️ Menggunakan Database Lokal: {db_uri}")

    # Fix untuk Render Postgres (jika nanti dipakai)
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_uri
    
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true"
    )

    FLASK_ENV = os.getenv("FLASK_ENV", "development")