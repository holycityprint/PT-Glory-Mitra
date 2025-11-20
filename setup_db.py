from holycity import create_app, db
# PENTING: Import semua model agar SQLAlchemy tahu tabel apa saja yang harus dibuat
from models import User, Employee, Attendance, Performance, Transaction, MarketingProspect, MarketingLead, MarketingProject, MarketingFollowUp, ProductionRecord, ProductionArticle, ProductionStep, MaterialPurchase, WarehouseItem, DeliveryOrder
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print(">>> [SETUP] 🛠️  Memulai inisialisasi Database...")
    
    # 1. Hapus database lama (Opsional, biar fresh) & Buat Baru
    # db.drop_all()  <-- Jangan aktifkan kalau tidak mau data hilang
    db.create_all()
    print(">>> [SETUP] ✅ Tabel-tabel berhasil dibuat!")

    # 2. Buat Data Dummy Employee (Karena User butuh Employee ID)
    # Cek dulu biar gak duplikat
    if not Employee.query.first():
        dummy_emp = Employee(
            name="Administrator",
            department="IT",
            position="Super Admin",
            join_date=None
        )
        db.session.add(dummy_emp)
        db.session.commit()
        print(">>> [SETUP] 👤 Dummy Employee berhasil dibuat.")
        emp_id = dummy_emp.id
    else:
        emp_id = Employee.query.first().id

    # 3. Buat User Admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        new_admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin',
            employee_id=emp_id 
        )
        db.session.add(new_admin)
        db.session.commit()
        print(">>> [SETUP] 🎉 User 'admin' berhasil dibuat!")
    else:
        print(">>> [SETUP] 👌 User 'admin' sudah ada.")

    print(">>> [SETUP] ✅ SELESAI. Database siap digunakan.")