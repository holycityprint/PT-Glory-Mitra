from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, make_response
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from weasyprint import HTML
import os
from datetime import datetime

from services.accounting_service import (
    get_summary, get_mutations, add_transaction
)
from models import Transaction

accounting_bp = Blueprint(
    "accounting",
    __name__,
    url_prefix="/accounting",
    template_folder="../templates/accounting"
)

UPLOAD_FOLDER = os.path.join("static", "uploads", "accounting")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================
# DASHBOARD
# ============================================
@accounting_bp.route("/")
@login_required
def dashboard():
    if current_user.role not in ("admin", "hrd"):
        return "Akses ditolak", 403

    summary = get_summary()
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template(
        "accounting/dashboard.html",
        user=current_user,
        summary=summary,
        transactions=transactions
    )


# ============================================
# TAMBAH TRANSAKSI
# ============================================
@accounting_bp.route("/add", methods=["POST"])
@login_required
def add_txn():
    if current_user.role not in ("admin", "hrd"):
        return "Akses ditolak", 403

    category = request.form.get("category")
    amount = request.form.get("amount")

    if not (category and amount):
        flash("Kategori dan jumlah wajib diisi!", "warning")
        return redirect(url_for("accounting.dashboard"))

    file = request.files.get("receipt")
    filename = None

    if file and file.filename:
        safe_name = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{safe_name}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    add_transaction(request.form, filename)
    flash("Transaksi berhasil ditambahkan.", "success")
    return redirect(url_for("accounting.dashboard"))


# ============================================
# MUTASI KEUANGAN
# ============================================
@accounting_bp.route("/mutasi", methods=["GET", "POST"])
@login_required
def mutasi():
    if current_user.role not in ("admin", "hrd"):
        return "Akses ditolak", 403

    mode = request.form.get("mode", "all")
    mutations = get_mutations(mode)
    return render_template(
        "accounting/mutasi.html",
        user=current_user,
        mutations=mutations,
        selected_mode=mode
    )


# ============================================
# EXPORT PDF
# ============================================
@accounting_bp.route("/mutasi/pdf/<mode>")
@login_required
def export_mutasi_pdf(mode):
    if current_user.role not in ("admin", "hrd"):
        return "Akses ditolak", 403

    mutations = get_mutations(mode)
    today = datetime.utcnow().date()
    html = render_template(
        "accounting/mutasi_pdf.html",
        mutations=mutations,
        mode=mode,
        today=today
    )
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=mutasi_{mode}.pdf"
    return response