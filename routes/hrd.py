# routes/hrd.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from holycity.extensions import db
from models import Employee

hrd_bp = Blueprint('hrd', __name__, url_prefix='/hrd')

@hrd_bp.route('/employees', methods=['GET', 'POST'])
@login_required
def employee_list():
    """Tampilkan & tambah karyawan di halaman yang sama"""
    # --- Tambah karyawan bila POST ---
    if request.method == 'POST':
        if current_user.role not in ('admin', 'hrd'):
            flash("Akses ditolak: hanya HRD/Admin yang dapat menambah karyawan.", "danger")
            return redirect(url_for('hrd.employee_list'))

        name = request.form.get('name')
        department = request.form.get('department')
        position = request.form.get('position')
        salary = float(request.form.get('salary') or 0)

        if not name or not name.strip():
            flash("Nama karyawan wajib diisi.", "warning")
            return redirect(url_for('hrd.employee_list'))

        new_emp = Employee(
            name=name.strip(),
            department=department.strip() if department else None,
            position=position.strip() if position else None,
            salary=salary,
            join_date=datetime.now()
        )
        db.session.add(new_emp)
        db.session.commit()

        flash("✅ Karyawan baru berhasil ditambahkan.", "success")
        return redirect(url_for('hrd.employee_list'))

    # --- Tampilkan halaman ---
    employees = Employee.query.order_by(Employee.id.desc()).all()
    return render_template('hrd/employee_list.html',
                           user=current_user,
                           employees=employees)