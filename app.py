import os
from holycity import create_app, db
from models import User  # Wajib import ini biar tabel Users dikenali
from werkzeug.security import generate_password_hash

app = create_app()

# ==============================================================================
#  BAGIAN INI AKAN DIJALANKAN OLEH GUNICORN SAAT SERVER NYALA (SETIAP DEPLOY)
# ==============================================================================
with app.app_context():
    print(">>> [RENDER STARTUP] 🛠️  Memulai Pengecekan Database...")
    
    try:
        # 1. BUAT TABEL
        # Perintah ini akan membuat file company.db dan tabel-tabelnya
        db.create_all()
        print(">>> [RENDER STARTUP] ✅ Tabel Database berhasil dibuat.")

        # 2. CEK & BUAT ADMIN
        # Kita cek apakah tabel users sudah bisa diakses
        existing_admin = User.query.filter_by(username='admin').first()
        
        if not existing_admin:
            print(">>> [RENDER STARTUP] 👤 Admin belum ada. Membuat baru...")
            new_admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin',
                employee_id=1  # Pastikan ini integer/sesuai model kamu
            )
            db.session.add(new_admin)
            db.session.commit()
            print(">>> [RENDER STARTUP] 🎉 Admin berhasil dibuat! (User: admin, Pass: admin123)")
        else:
            print(">>> [RENDER STARTUP] 👌 Admin sudah tersedia.")

    except Exception as e:
        print(f">>> [RENDER STARTUP] ❌ ERROR FATAL SAAT BIKIN DB: {e}")
# ==============================================================================


# Bagian ini hanya jalan kalau kamu run di laptop (python app.py)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)