# routes/hrd/employee.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from datetime import datetime
from models import db, Employee
from . import hrd_bp


# ==========================
# 🔹 Daftar Karyawan
# ==========================
@hrd_bp.route("/employees")
@login_required
def employee_list():
    """Halaman utama Data Karyawan"""
    if current_user.role not in ("hrd", "admin"):
        return "Akses ditolak", 403

    employees = Employee.query.order_by(Employee.name.asc()).all()
    return render_template(
        "hrd/employee_list.html",
        user=current_user,
        employees=employees,
    )


# ==========================
# 🔹 Tambah Karyawan
# ==========================
@hrd_bp.route("/employee/add", methods=["POST"])
@login_required
def employee_add():
    """Proses form tambah karyawan (endpoint cocok dengan template!)"""
    if current_user.role not in ("admin", "hrd"):
        abort(403)

    name = request.form.get("name")
    dept = request.form.get("department")
    pos = request.form.get("position")
    join_date = request.form.get("join_date")
    salary = request.form.get("salary")

    if not name:
        flash("Nama karyawan harus diisi.", "warning")
        return redirect(url_for("hrd.employee_list"))

    new_emp = Employee(
        name=name,
        department=dept,
        position=pos,
        join_date=datetime.strptime(join_date, "%Y-%m-%d") if join_date else None,
        salary=float(salary) if salary else 0.0,
    )
    db.session.add(new_emp)
    db.session.commit()
    flash(f"Karyawan '{name}' berhasil ditambahkan.", "success")
    return redirect(url_for("hrd.employee_list"))


# ==========================
# 🔹 Update Karyawan
# ==========================
@hrd_bp.route("/employee/update/<int:emp_id>", methods=["POST"])
@login_required
def employee_update(emp_id):
    """Perbarui data karyawan"""
    if current_user.role not in ("admin", "hrd"):
        abort(403)

    emp = Employee.query.get_or_404(emp_id)
    emp.department = request.form.get("department", emp.department)
    emp.position = request.form.get("position", emp.position)
    join_date = request.form.get("join_date")
    salary = request.form.get("salary")

    if join_date:
        emp.join_date = datetime.strptime(join_date, "%Y-%m-%d")
    if salary:
        emp.salary = float(salary)

    db.session.commit()
    flash(f"Data karyawan '{emp.name}' diperbarui.", "success")
    return redirect(url_for("hrd.employee_list"))


# ==========================
# 🔹 Hapus Karyawan
# ==========================
@hrd_bp.route("/employee/delete/<int:emp_id>", methods=["POST"])
@login_required
def employee_delete(emp_id):
    """Hapus data karyawan"""
    if current_user.role not in ("admin", "hrd"):
        abort(403)

    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash(f"Karyawan '{emp.name}' telah dihapus.", "info")
    return redirect(url_for("hrd.employee_list"))