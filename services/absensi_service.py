# services/absensi_service.py
from datetime import datetime, date
from math import radians, sin, cos, sqrt, atan2
from models import db, Attendance
from werkzeug.utils import secure_filename
import os

# --- konfigurasi lokasi kantor ---
OFFICE_LAT = -6.914744
OFFICE_LON = 107.609810
ALLOWED_RADIUS = 5  # meter
UPLOAD_FOLDER = os.path.join("static", "uploads", "absensi")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# === Utility ===
def distance_m(lat1, lon1, lat2, lon2):
    """Hitung jarak antar titik dalam meter."""
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# === Service utama ===
def validate_location(lat, lon):
    """Pastikan user berada dalam radius kantor."""
    jarak = distance_m(lat, lon, OFFICE_LAT, OFFICE_LON)
    return jarak <= ALLOWED_RADIUS, jarak


def already_checked(username, status):
    """Cek apakah user sudah absen status sama hari ini."""
    today = date.today()
    record = Attendance.query.filter(
        Attendance.username == username,
        db.func.date(Attendance.timestamp) == today,
        Attendance.status == status
    ).first()
    return bool(record)


def save_photo(file, username):
    """Simpan foto ke folder upload, return filename."""
    if not file or not file.filename:
        return None
    safe_name = secure_filename(file.filename)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{username}_{timestamp_str}_{safe_name}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return filename


def add_attendance(username, status, lat, lon, photo_filename=None):
    """Tambah record absensi ke database."""
    record = Attendance(
        username=username,
        status=status,
        latitude=lat,
        longitude=lon,
        photo=photo_filename,
        timestamp=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_records_for_user(user):
    """Ambil data absensi tergantung role."""
    if user.role in ("admin", "hrd"):
        return Attendance.query.order_by(Attendance.timestamp.desc()).all()
    return (Attendance.query
            .filter_by(username=user.username)
            .order_by(Attendance.timestamp.desc())
            .all())