from holycity import create_app
# Kita butuh akses ke 'db' dan 'User' untuk bikin tabel otomatis
# Asumsi: db ada di holycity.extensions atau di holycity/__init__.py
try:
    from holycity.extensions import db
except ImportError:
    from holycity import db

from models import User
from werkzeug.security import generate_password_hash

app = create_app()

# --- BAGIAN PENTING: AUTO SETUP DATABASE ---
# Kode di dalam blok ini akan dijalankan Gunicorn saat start
with app.app_context():
    try:
        print(">>> 🛠️ Memulai pengecekan Database...")
        
        # 1. Paksa Buat Semua Tabel (Solusi Masalah 'no such table')
        db.create_all()
        print(">>> ✅ Tabel Database berhasil dibuat/dicek.")

        # 2. Buat User Admin Otomatis (Supaya bisa login)
        # Cek dulu apakah admin sudah ada?
        existing_admin = User.query.filter_by(username='admin').first()
        
        if not existing_admin:
            print(">>> 👤 User admin belum ada. Membuat admin baru...")
            
            # Perhatikan: Sesuaikan field di bawah dengan models.py kamu
            # Saya lihat di log error sebelumnya ada kolom: employee_id
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin123'), # Password Login
                role='admin',
                employee_id='9999' # Isi dummy angka bebas karena kolom ini wajib
            )
            
            db.session.add(admin_user)
            db.session.commit()
            print(">>> 🎉 Admin berhasil dibuat! (User: admin, Pass: admin123)")
        else:
            print(">>> 👌 Admin sudah ada. Skip pembuatan.")
            
    except Exception as e:
        print(f">>> ⚠️ Info Database: {e}")
# -------------------------------------------

if __name__ == "__main__":
    print(">>> 🚀 Starting Holycity Portal Server ...")
    app.run(host="0.0.0.0", port=5000, debug=True)