from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import (
    login_user, login_required, logout_user, current_user
)
from datetime import datetime
import os

from config import Config
from holycity.extensions import db, login_manager, migrate, csrf
from models import User

def create_app():
    """Application Factory utama Holycity Portal."""
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates"
    )
    app.config.from_object(Config)

    # konfigurasi tambahan untuk kestabilan CSRF
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_TIME_LIMIT"] = None

    if app.config.get("FLASK_ENV") == "development":
        app.debug = True

    os.makedirs("uploads", exist_ok=True)

    # --- Inisialisasi ekstensi ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- Admin default ---
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", role="admin")
            admin.set_password("1234")
            db.session.add(admin)
            db.session.commit()
            print("✅  Admin default dibuat: admin / 1234")

    # --- IMPORT BLUEPRINT ---
    from routes.absensi import absensi_bp
    from routes.hrd import hrd_bp
    from routes.accounting import accounting_bp
    from blueprints.marketing import marketing_bp
    from routes.produksi import produksi_bp
    from routes.pembelian import pembelian_bp
    from routes.gudang import gudang_bp
    from routes.pengiriman import pengiriman_bp  # ✅ Import Pengiriman

    # --- REGISTER BLUEPRINT ---
    app.register_blueprint(absensi_bp)
    app.register_blueprint(hrd_bp)
    app.register_blueprint(accounting_bp)
    app.register_blueprint(marketing_bp)
    app.register_blueprint(produksi_bp)
    app.register_blueprint(pembelian_bp)
    app.register_blueprint(gudang_bp)
    app.register_blueprint(pengiriman_bp)  # ✅ Register Pengiriman

    # --- Routes utama ---
    @app.route("/")
    @login_required
    def home():
        return render_template("home_reception.html", user=current_user)

    @app.route("/dashboard")
    @login_required
    def dashboard_redirect():
        if current_user.role == "employee":
            return redirect(url_for("absensi.absensi_page"))
        elif current_user.role in ("admin", "hrd"):
            return redirect(url_for("hrd.dashboard"))
        return redirect(url_for("home"))

    # --- Login / Logout ---
    @csrf.exempt
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f"Selamat datang, {user.username}!", "success")
                return redirect(url_for("home"))
            flash("⚠️  Login gagal. Periksa username atau password.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Anda sudah logout.", "info")
        return redirect(url_for("login"))

    # --- Context Processor ---
    @app.context_processor
    def inject_now():
        return {
            "now": datetime.now,
            "current_year": datetime.now().year,
            "user": current_user if current_user.is_authenticated else None,
        }

    return app