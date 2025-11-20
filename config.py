import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")

    # --- BAGIAN INI YANG DIUPDATE ---
    # Ambil URL dari environment variable
    db_uri = os.getenv("SQLALCHEMY_DATABASE_URI")

    # Jika tidak ada di env (artinya di local), pakai SQLite
    if not db_uri:
        db_uri = f"sqlite:///{os.path.join(BASE_DIR, 'company.db')}"
    
    # FIX KHUSUS RENDER: Ubah postgres:// menjadi postgresql://
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_uri
    # --------------------------------
    
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true"
    )

    FLASK_ENV = os.getenv("FLASK_ENV", "development")