import os
from holycity import create_app, db  # Pastikan db diimport dari package utama
from models import User  # Penting: Import model supaya create_all ngenalin tabelnya
from werkzeug.security import generate_password_hash

app = create_app()

# --- BAGIAN AUTO SETUP (TANPA TRY-EXCEPT) ---
# Kita hapus try-except supaya kalau error, deploy langsung gagal (biar ketahuan)
with app.app_context():
    print(">>> 🛠️  SEDANG MEMBUAT DATABASE SQLITE...")
    
    # Cek lokasi database (untuk debugging)
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f">>> 📂 Lokasi Database: {db_path}")

    # 1. BUAT TABEL
    # Ini akan membuat semua tabel berdasarkan model yang sudah diimport
    db.create_all()
    print(">>> ✅ Tabel berhasil dibuat (create_all sukses).")

    # 2. BUAT ADMIN
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print(">>> 👤 Admin tidak ditemukan. Membuat admin baru...")
        new_admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin',
            employee_id='ADM001'  # Pastikan field ini sesuai dengan models.py kamu
        )
        db.session.add(new_admin)
        db.session.commit()
        print(">>> 🎉 Admin berhasil dibuat!")
    else:
        print(">>> 👌 Admin sudah ada.")
# -------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)