"""
File : holycity/extensions.py
Berisi semua objek ekstensi Flask yang digunakan di seluruh aplikasi.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# --- Inisialisasi objek ekstensi ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()  # ✅ tambahkan ini agar bisa di‑import

# --- Pengaturan login manager ---
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
login_manager.login_message = "Silakan login terlebih dahulu untuk mengakses halaman ini."