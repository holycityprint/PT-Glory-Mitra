from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from holycity.extensions import db, csrf
from models import ProductionArticle, ProductionStep, WarehouseItem 

import os
from werkzeug.utils import secure_filename

produksi_bp = Blueprint("produksi", __name__, url_prefix="/produksi")

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. Index
@produksi_bp.route("/")
@login_required
def index():
    articles = ProductionArticle.query.order_by(ProductionArticle.tanggal_dibuat.desc()).all()
    return render_template("produksi/index.html", articles=articles)

# 2. Tambah Artikel
@csrf.exempt
@produksi_bp.route("/tambah_artikel", methods=["GET", "POST"])
@login_required
def tambah_artikel():
    if request.method == "POST":
        nama = request.form.get("nama_artikel", "").strip()
        ket = request.form.get("keterangan")
        file = request.files.get("gambar")

        if not nama:
            flash("Nama artikel wajib diisi.", "danger")
            return redirect(url_for("produksi.tambah_artikel"))

        filename = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        artikel = ProductionArticle(nama_artikel=nama, keterangan=ket, gambar=filename)
        db.session.add(artikel)
        db.session.commit()

        default_steps = [
            "Pemakaian Bahan", "Cutting", "Sablon", "Jahit",
            "QC", "Buang Benang", "Steam", "Packing", "Kirim"
        ]
        for tahap in default_steps:
            step = ProductionStep(article_id=artikel.id, tahap=tahap, status="proses")
            db.session.add(step)
        db.session.commit()

        flash(f"Artikel '{nama}' berhasil dibuat.", "success")
        return redirect(url_for("produksi.detail_artikel", artikel_id=artikel.id))

    return render_template("produksi/tambah_artikel.html")

# 3. Detail
@produksi_bp.route("/<int:artikel_id>")
@login_required
def detail_artikel(artikel_id):
    article = ProductionArticle.query.get_or_404(artikel_id)
    
    steps_data = [
        {
            "id": s.id,
            "tahap": s.tahap,
            "status": s.status,
            "tanggal_update": s.tanggal_update.strftime("%Y-%m-%d"),
        }
        for s in article.steps
    ]

    return render_template(
        "produksi/detail_artikel.html",
        article=article,
        steps_data=steps_data,
    )

# 4. Edit Step (UPDATE: KAIN & KAOS POLOS SAMA-SAMA POTONG STOK)
@csrf.exempt
@produksi_bp.route("/step/<int:step_id>/edit", methods=["GET", "POST"])
@login_required
def edit_step(step_id):
    step = ProductionStep.query.get_or_404(step_id)
    
    # Ambil data stok gudang
    stok_gudang = WarehouseItem.query.order_by(WarehouseItem.nama_item.asc()).all()

    if request.method == "POST":
        step.status = request.form.get("status")
        step.keterangan = request.form.get("keterangan")
        step.tanggal_update = datetime.utcnow()

        # ========================================================
        # 🛠️ LOGIKA 1: PEMAKAIAN BAHAN (INTEGRASI PENUH)
        # ========================================================
        if step.tahap == "Pemakaian Bahan" or step.tahap == "Pembelian Bahan":
            sumber_bahan = request.form.get("sumber_bahan") 
            
            # LOGIKA UMUM UNTUK POTONG STOK (Baik Kain maupun Kaos Polos)
            if sumber_bahan in ['kain_gudang', 'kaos_gudang']:
                item_id = request.form.get("warehouse_item_id")
                qty_ambil = float(request.form.get("jumlah_ambil", 0))
                
                # Input tambahan (Warna/Ukuran)
                detail_warna = request.form.get("detail_warna") # Warna spesifik
                detail_ukuran = request.form.get("detail_ukuran") # Ukuran spesifik (opsional)

                item_gudang = WarehouseItem.query.get(item_id)
                
                if item_gudang and not step.is_posted:
                    if item_gudang.stok >= qty_ambil:
                        # ✅ POTONG STOK DI DATABASE
                        item_gudang.stok -= qty_ambil
                        item_gudang.last_updated = datetime.utcnow()
                        
                        # Simpan ke Step Produksi
                        step.jumlah = qty_ambil
                        step.satuan = item_gudang.satuan
                        step.warna_bahan = detail_warna or item_gudang.nama_item
                        step.ukuran = detail_ukuran 
                        
                        # Catat sumber di keterangan
                        jenis_sumber = "Bahan Baku" if sumber_bahan == 'kain_gudang' else "Kaos Polos"
                        info = f"[{jenis_sumber}: {item_gudang.nama_item}]"
                        step.keterangan = f"{step.keterangan or ''} {info}".strip()
                        
                        step.is_posted = True
                        flash(f"✅ Berhasil! Stok '{item_gudang.nama_item}' berkurang {qty_ambil} {item_gudang.satuan}.", "success")
                    else:
                        flash(f"❌ Gagal! Stok gudang tidak cukup. Sisa: {item_gudang.stok}", "danger")
                        return redirect(url_for("produksi.edit_step", step_id=step.id))
            
            else:
                # JAGA-JAGA: Jika user tetap ingin input manual tanpa gudang
                step.jumlah = request.form.get("jumlah")
                step.satuan = request.form.get("satuan")
                step.warna_bahan = request.form.get("warna_bahan")

        # ========================================================
        # 🛠️ LOGIKA LAIN (TIDAK BERUBAH)
        # ========================================================
        elif step.tahap in ["Cutting", "Jahit"]:
            data_jumlah = {}
            data_harga = {}
            kategori_ukuran = {
                "regular": ["S", "M", "L", "XL"],
                "big_size": ["2XL", "3XL", "4XL", "5XL"],
                "jumbo": ["6XL", "7XL"],
                "ladies": ["S", "M", "L", "XL"],
                "ladies_oversize": ["S", "M", "L", "XL"],
                "kids_4th": ["6", "8", "10", "12"],
                "ladies_junior": ["6", "8", "10", "12", "14"],
                "oversize": ["S", "M", "L", "XL"],
                "kulot": ["S", "M", "L", "XL"],
                "celana_pendek_dewasa": ["S", "M", "L", "XL"]
            }

            total_harga = 0.0
            for kategori, daftar in kategori_ukuran.items():
                data_jumlah[kategori] = {}
                data_harga[kategori] = {}
                for u in daftar:
                    jml = request.form.get(f"{kategori}_{u}")
                    if jml:
                        try:
                            jml = float(jml)
                        except ValueError:
                            jml = 0
                        data_jumlah[kategori][u] = jml

                    harga_field = (
                        f"harga_cutting_{kategori}_{u}"
                        if step.tahap == "Cutting"
                        else f"harga_jahit_{kategori}_{u}"
                    )
                    hrg = request.form.get(harga_field)
                    if hrg:
                        try:
                            hrg = float(hrg)
                        except ValueError:
                            hrg = 0
                        data_harga[kategori][u] = hrg
                        total_harga += hrg
                    else:
                        data_harga[kategori][u] = 0

            step.ukuran_data = {
                "jumlah": data_jumlah,
                "harga": data_harga
            }

            if step.tahap == "Cutting":
                step.harga_cutting = total_harga
            else:
                step.harga_jahit = total_harga

        elif step.tahap == "Sablon":
            step.metode_sablon = request.form.get("metode_sablon")

        elif step.tahap == "Kirim":
            step.ekspedisi = request.form.get("ekspedisi")
            step.jumlah = request.form.get("jumlah")

        else:
            step.jumlah = request.form.get("jumlah")

        # LOGIKA PACKING -> GUDANG BARANG JADI
        # ✅ REVISI: Pastikan masuk ke 'Gudang Utama'
        if step.tahap == "Packing" and step.status == "selesai" and not step.is_posted:
            try:
                qty_finish = float(step.jumlah or 0)
                if qty_finish > 0:
                    nama_barang_jadi = f"{step.article.nama_artikel} (Finish)"
                    
                    # Cek spesifik di Gudang Utama
                    stok_item = WarehouseItem.query.filter_by(
                        nama_item=nama_barang_jadi,
                        lokasi_gudang="Gudang Utama" 
                    ).first()
                    
                    if stok_item:
                        stok_item.stok += qty_finish
                        stok_item.last_updated = datetime.utcnow()
                    else:
                        new_item = WarehouseItem(
                            nama_item=nama_barang_jadi,
                            kategori="Barang Jadi",
                            stok=qty_finish,
                            satuan="Pcs",
                            lokasi_gudang="Gudang Utama", # Default masuk sini
                            lokasi_rak="Area Packing",
                            last_updated=datetime.utcnow()
                        )
                        db.session.add(new_item)
                    
                    step.is_posted = True
                    flash(f"✅ Otomatis menambah {qty_finish} Pcs '{nama_barang_jadi}' ke Gudang Utama!", "success")
            except ValueError:
                pass

        db.session.commit()
        flash(f"Tahap '{step.tahap}' berhasil diperbarui.", "success")
        return redirect(url_for("produksi.detail_artikel", artikel_id=step.article_id))

    return render_template("produksi/edit_step.html", step=step, stok_gudang=stok_gudang)

# 5. Hapus
@csrf.exempt
@produksi_bp.route("/<int:artikel_id>/hapus", methods=["POST"])
@login_required
def hapus_artikel(artikel_id):
    article = ProductionArticle.query.get_or_404(artikel_id)
    try:
        for step in article.steps:
            step.article_id = None
        db.session.delete(article)
        db.session.commit()
        flash("Artikel berhasil dihapus.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Gagal hapus: {e}", "danger")
    return redirect(url_for("produksi.index"))