# create_admin.py
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User.query.filter_by(username="admin").first()
    if admin:
        print("[INFO] Admin sudah ada:", admin.username)
    else:
        hashed = generate_password_hash("1234")
        admin = User(username="admin", password=hashed, role="admin")
        db.session.add(admin)
        db.session.commit()
        print("[SUCCESS] Akun admin berhasil dibuat -> username=admin  password=1234")