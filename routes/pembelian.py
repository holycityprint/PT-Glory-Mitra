from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from holycity.extensions import db, csrf
from models import MaterialPurchase, WarehouseItem 

pembelian_bp = Blueprint("pembelian", __name__, url_prefix="/pembelian")

@pembelian_bp.route("/")
@login_required
def index():
    purchases = MaterialPurchase.query.order_by(MaterialPurchase.tanggal_beli.desc()).all()
    return render_template("pembelian/index.html", purchases=purchases)

@csrf.exempt
@pembelian_bp.route("/tambah", methods=["GET", "POST"])
@login_required
def tambah():
    if request.method == "POST":
        nama_bahan = request.form.get("nama_bahan").strip()
        # Pakai title() agar "Kain Katun" dan "kain katun" dianggap sama
        nama_bahan_clean = nama_bahan.title() 
        
        nama_toko = request.form.get("nama_toko")
        jumlah = float(request.form.get("jumlah", 0))
        satuan = request.form.get("satuan")
        harga_satuan = float(request.form.get("harga_satuan", 0))
        total_harga = jumlah * harga_satuan
        keterangan = request.form.get("keterangan")
        
        # ✅ Ambil Lokasi Gudang dari Form (Default: Gudang Utama)
        lokasi_tujuan = request.form.get("lokasi_tujuan", "Gudang Utama")

        # 1. Simpan Riwayat Pembelian
        beli = MaterialPurchase(
            nama_bahan=nama_bahan_clean,
            nama_toko=nama_toko,
            jumlah=jumlah,
            satuan=satuan,
            harga_satuan=harga_satuan,
            total_harga=total_harga,
            keterangan=keterangan,
            tanggal_beli=datetime.utcnow()
        )
        db.session.add(beli)

        # 2. OTOMATIS UPDATE GUDANG (SESUAI LOKASI)
        stok_item = WarehouseItem.query.filter_by(
            nama_item=nama_bahan_clean,
            lokasi_gudang=lokasi_tujuan # ✅ Cek barang di gudang spesifik
        ).first()
        
        if stok_item:
            # Jika barang sudah ada di gudang tersebut, tambah stoknya
            stok_item.stok += jumlah
            stok_item.last_updated = datetime.utcnow()
            flash(f"Stok '{nama_bahan_clean}' berhasil ditambahkan ke {lokasi_tujuan} (+{jumlah} {satuan})", "success")
        else:
            # Jika barang baru di gudang tersebut, buat data stok baru
            item_baru = WarehouseItem(
                nama_item=nama_bahan_clean,
                kategori="Bahan Baku",
                stok=jumlah,
                satuan=satuan,
                lokasi_gudang=lokasi_tujuan, # ✅ Set lokasi gudang
                last_updated=datetime.utcnow()
            )
            db.session.add(item_baru)
            flash(f"Item baru '{nama_bahan_clean}' ditambahkan ke {lokasi_tujuan}.", "success")

        db.session.commit()
        return redirect(url_for("pembelian.index"))

    return render_template("pembelian/tambah.html")