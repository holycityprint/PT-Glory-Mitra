import os
from flask import render_template
from flask_login import login_required, current_user
from datetime import date
from models import db, Employee, Attendance
from . import hrd_bp


@hrd_bp.route("/")
@login_required
def dashboard():
    """Halaman utama Dashboard HRD."""

    # hanya HRD & Admin yang boleh masuk
    if current_user.role not in ("admin", "hrd"):
        return "Akses ditolak", 403

    # ---- Logging untuk pastikan lokasi template ----
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../templates/hrd"))
    dashboard_path = os.path.join(template_dir, "dashboard.html")
    print("=== Lokasi file dashboard HRD yang dicari ===")
    print(dashboard_path)
    print("File ada?:", os.path.exists(dashboard_path))

    # ---- Ambil data sederhana untuk dashboard ----
    today = date.today()
    total_emp = Employee.query.count()
    hadir = (
        Attendance.query.filter(
            db.func.date(Attendance.timestamp) == today,
            Attendance.status == "Masuk",
        )
        .distinct(Attendance.username)
        .count()
    )
    izin = (
        Attendance.query.filter(
            db.func.date(Attendance.timestamp) == today,
            Attendance.status == "Izin",
        )
        .distinct(Attendance.username)
        .count()
    )

    # ---- Render template (pastikan struktur folder benar) ----
    # Gunakan jalur relatif ke folder 'templates'
    return render_template(
        "hrd/dashboard.html",
        user=current_user,
        total_karyawan=total_emp,
        total_hadir=hadir,
        total_izin=izin,
    )