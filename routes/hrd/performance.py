# routes/hrd/performance.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import abort
from datetime import datetime
from models import db, Employee, Performance
from . import hrd_bp


@hrd_bp.route("/performance")
@login_required
def performance_list():
    """Tampilkan daftar penilaian kinerja."""
    if current_user.role not in ("admin", "hrd"):
        abort(403)

    records = (
        Performance.query.join(Employee)
        .add_columns(
            Employee.name,
            Performance.period,
            Performance.score,
            Performance.remarks,
            Performance.evaluator
        )
        .order_by(Performance.period.desc())
        .all()
    )
    employees = Employee.query.order_by(Employee.name.asc()).all()
    return render_template(
        "hrd/performance.html",
        user=current_user,
        records=records,
        employees=employees
    )


@hrd_bp.route("/performance/add", methods=["POST"])
@login_required
def performance_add():
    """Tambah data penilaian kinerja."""
    if current_user.role not in ("admin", "hrd"):
        abort(403)

    emp_id = request.form.get("employee_id")
    period = request.form.get("period")
    score = request.form.get("score")
    remarks = request.form.get("remarks")
    evaluator = current_user.username

    if not (emp_id and period and score):
        flash("Harap isi semua kolom wajib.", "warning")
        return redirect(url_for("hrd.performance_list"))

    perf = Performance(
        employee_id=int(emp_id),
        period=period,
        score=float(score),
        remarks=remarks,
        evaluator=evaluator
    )
    db.session.add(perf)
    db.session.commit()

    flash("Data penilaian kinerja berhasil ditambahkan.", "success")
    return redirect(url_for("hrd.performance_list"))