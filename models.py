from holycity.extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ---------- USER LOGIN ----------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="employee")
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    employee = db.relationship("Employee", back_populates="user", uselist=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ---------- DATA KARYAWAN ----------
class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    join_date = db.Column(db.Date, default=lambda: datetime.utcnow().date())
    salary = db.Column(db.Float, default=0.0)

    user = db.relationship("User", back_populates="employee", uselist=False)
    attendance_records = db.relationship(
        "Attendance", back_populates="employee", lazy="dynamic", cascade="all, delete-orphan"
    )
    performance_records = db.relationship(
        "Performance", back_populates="employee", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Employee {self.name} - {self.department or 'N/A'}>"


# ---------- DATA ABSENSI ----------
class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(25), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    photo = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    employee = db.relationship("Employee", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance {self.username} ({self.status}) @ {self.timestamp:%Y-%m-%d %H:%M:%S}>"


# ---------- PENILAIAN KINERJA ----------
class Performance(db.Model):
    __tablename__ = "performance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    period = db.Column(db.String(7))
    score = db.Column(db.Float)
    remarks = db.Column(db.Text)
    evaluator = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship("Employee", back_populates="performance_records")

    def __repr__(self):
        return f"<Performance emp={self.employee_id} {self.period}={self.score}>"


# ---------- TRANSAKSI KEUANGAN ----------
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=lambda: datetime.utcnow().date())
    category = db.Column(db.String(20))
    description = db.Column(db.String(255))
    source = db.Column(db.String(100))
    account = db.Column(db.String(100))
    amount = db.Column(db.Float)
    receipt = db.Column(db.String(255))

    def __repr__(self):
        return f"<Transaction {self.category} {self.amount}>"


# ---------- MARKETING ----------
class MarketingProspect(db.Model):
    __tablename__ = "marketing_prospects"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150))
    contact = db.Column(db.String(100))
    email = db.Column(db.String(120))
    source = db.Column(db.String(100))
    status = db.Column(db.String(50), default="Baru")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leads = db.relationship("MarketingLead", back_populates="prospect", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prospect {self.client_name} - {self.status}>"


class MarketingLead(db.Model):
    __tablename__ = "marketing_leads"

    id = db.Column(db.Integer, primary_key=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey("marketing_prospects.id"))
    product_interest = db.Column(db.String(150))
    estimated_value = db.Column(db.Float)
    stage = db.Column(db.String(50), default="Awal")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    prospect = db.relationship("MarketingProspect", back_populates="leads")
    projects = db.relationship("MarketingProject", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead {self.product_interest} ({self.stage})>"


class MarketingProject(db.Model):
    __tablename__ = "marketing_projects"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("marketing_leads.id"))
    project_name = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Perencanaan")
    budget = db.Column(db.Float)
    remarks = db.Column(db.Text)

    lead = db.relationship("MarketingLead", back_populates="projects")
    followups = db.relationship("MarketingFollowUp", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.project_name} ({self.status})>"


class MarketingFollowUp(db.Model):
    __tablename__ = "marketing_followups"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("marketing_projects.id"))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    contact_person = db.Column(db.String(100))
    method = db.Column(db.String(50))
    result = db.Column(db.Text)

    project = db.relationship("MarketingProject", back_populates="followups")

    def __repr__(self):
        return f"<FollowUp {self.project_id} via {self.method}>"


# ---------- DATA PRODUKSI ----------
class ProductionRecord(db.Model):
    __tablename__ = "production_records"

    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, default=datetime.utcnow)
    vendor_bahan = db.Column(db.String(100))
    jenis_bahan = db.Column(db.String(50))
    tahap = db.Column(db.String(50))
    kategori_ukuran = db.Column(db.String(50))
    ukuran = db.Column(db.String(20))
    metode_sablon = db.Column(db.String(50))
    keterangan = db.Column(db.Text)
    status = db.Column(db.String(20), default="proses")

    def __repr__(self):
        return f"<Produksi {self.tanggal} {self.vendor_bahan} {self.tahap}>"


# ---------- PRODUKSI ARTIKEL ----------
class ProductionArticle(db.Model):
    __tablename__ = "production_articles"

    id = db.Column(db.Integer, primary_key=True)
    nama_artikel = db.Column(db.String(150), nullable=False, unique=True)
    tanggal_dibuat = db.Column(db.DateTime, default=datetime.utcnow)
    keterangan = db.Column(db.Text)
    gambar = db.Column(db.String(255))

    steps = db.relationship("ProductionStep", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article {self.nama_artikel}>"


class ProductionStep(db.Model):
    __tablename__ = "production_steps"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("production_articles.id"))
    tahap = db.Column(db.String(50))
    kategori = db.Column(db.String(50))
    status = db.Column(db.String(20), default="proses")
    tanggal_update = db.Column(db.DateTime, default=datetime.utcnow)
    keterangan = db.Column(db.Text)

    # Kolom detail
    nama_toko = db.Column(db.String(100))
    jumlah = db.Column(db.Float)
    warna_bahan = db.Column(db.String(50))
    harga_total = db.Column(db.Float)
    metode_sablon = db.Column(db.String(50))
    ukuran_data = db.Column(db.JSON)
    ekspedisi = db.Column(db.String(100))
    harga_cutting = db.Column(db.Float)
    harga_jahit   = db.Column(db.Float)
    satuan = db.Column(db.String(20)) 
    
    # Kolom tambahan untuk data manual
    jenis_bahan = db.Column(db.String(50))
    ukuran = db.Column(db.String(20))
    
    article = db.relationship("ProductionArticle", back_populates="steps")

    def __repr__(self):
        return f"<Step {self.tahap}>"


# ---------- PEMBELIAN BAHAN ----------
class MaterialPurchase(db.Model):
    __tablename__ = 'material_purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    tanggal_beli = db.Column(db.DateTime, default=datetime.utcnow)
    nama_bahan = db.Column(db.String(100), nullable=False)
    nama_toko = db.Column(db.String(100))
    jumlah = db.Column(db.Float, default=0)
    satuan = db.Column(db.String(20))
    harga_satuan = db.Column(db.Float, default=0)
    total_harga = db.Column(db.Float, default=0)
    keterangan = db.Column(db.Text)

    def __repr__(self):
        return f"<Purchase {self.nama_bahan}>"


# ---------- GUDANG / INVENTORY ----------
class WarehouseItem(db.Model):
    __tablename__ = 'warehouse_items'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_item = db.Column(db.String(100), nullable=False, unique=True)
    kategori = db.Column(db.String(50)) # Kain, Benang, Aksesoris
    stok = db.Column(db.Float, default=0)
    satuan = db.Column(db.String(20)) # Kg, Yard, Roll
    lokasi_rak = db.Column(db.String(50))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

     # ✅ KOLOM BARU (Penyebab Error)
    lokasi_gudang = db.Column(db.String(50), default="Gudang Utama") 
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Stok {self.nama_item}: {self.stok}>"


# ---------- PENGIRIMAN / SURAT JALAN (YANG DITAMBAHKAN) ----------
class DeliveryOrder(db.Model):
    __tablename__ = 'delivery_orders'

    id = db.Column(db.Integer, primary_key=True)
    no_surat = db.Column(db.String(50), unique=True, nullable=False) # SJ/2025/XI/001
    tanggal = db.Column(db.Date, default=datetime.utcnow)
    
    nama_penerima = db.Column(db.String(150), nullable=False)
    alamat_tujuan = db.Column(db.Text, nullable=False)
    no_telp = db.Column(db.String(20))

    nama_kurir = db.Column(db.String(100))
    nopol_kendaraan = db.Column(db.String(20)) # B 1234 XYZ
    jenis_kendaraan = db.Column(db.String(50)) # Mobil Box, Motor, Truk

    list_barang = db.Column(db.Text) 
    catatan = db.Column(db.Text)
    
    status = db.Column(db.String(20), default="Dikirim")

    def __repr__(self):
        return f"<SJ {self.no_surat}>"