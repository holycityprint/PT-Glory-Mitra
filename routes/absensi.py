from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.absensi_service import (
    validate_location, already_checked, save_photo,
    add_attendance, get_records_for_user
)

absensi_bp = Blueprint("absensi", __name__, template_folder="../templates")


@absensi_bp.route("/absensi", methods=["GET", "POST"])
@login_required
def absensi_page():
    if request.method == "POST" and current_user.role == "employee":
        status = request.form.get("status")
        lat_str, lon_str = request.form.get("latitude"), request.form.get("longitude")

        # validasi lokasi
        if not lat_str or not lon_str:
            flash("⚠️  Lokasi belum terdeteksi. Aktifkan GPS lalu coba lagi.", "warning")
            return redirect(url_for("absensi.absensi_page"))

        lat, lon = float(lat_str), float(lon_str)
        valid, jarak = validate_location(lat, lon)
        if not valid:
            flash(f"❌  Anda {jarak:.2f} m dari kantor (maks. 5 m).", "danger")
            return redirect(url_for("absensi.absensi_page"))

        # cek double absen
        if already_checked(current_user.username, status):
            flash(f"⚠️  Anda sudah melakukan absen {status} hari ini.", "warning")
            return redirect(url_for("absensi.absensi_page"))

        # simpan foto
        filename = save_photo(request.files.get("photo"), current_user.username)

        # tambah record absensi
        add_attendance(current_user.username, status, lat, lon, filename)
        flash("✅  Absensi berhasil direkam.", "success")
        return redirect(url_for("absensi.absensi_page"))

    # tampilkan riwayat
    records = get_records_for_user(current_user)
    return render_template("absensi.html", records=records, user=current_user)