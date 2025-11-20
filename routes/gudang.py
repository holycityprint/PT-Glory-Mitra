from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from holycity.extensions import db, csrf
from models import WarehouseItem

gudang_bp = Blueprint("gudang", __name__, url_prefix="/gudang")

@gudang_bp.route("/")
@login_required
def index():
    # Ambil filter lokasi dari parameter URL (default: Gudang Utama)
    lokasi = request.args.get("lokasi", "Gudang Utama")
    
    # Ambil data sesuai lokasi
    items = WarehouseItem.query.filter_by(lokasi_gudang=lokasi).order_by(WarehouseItem.nama_item.asc()).all()
    
    return render_template("gudang/index.html", items=items, active_lokasi=lokasi)

# ✅ FITUR DISTRIBUSI (TRANSFER ANTAR GUDANG / JUAL PUTUS)
@csrf.exempt
@gudang_bp.route("/distribusi", methods=["POST"])
@login_required
def distribusi():
    item_id = request.form.get("item_id")
    tujuan = request.form.get("tujuan") # 'Gudang Episode', 'Gudang Cargo', atau 'Jual Putus'
    jumlah = float(request.form.get("jumlah", 0))
    
    item_asal = WarehouseItem.query.get_or_404(item_id)
    
    if item_asal.stok < jumlah:
        flash(f"Gagal! Stok tidak cukup. Sisa: {item_asal.stok}", "danger")
        return redirect(url_for("gudang.index", lokasi=item_asal.lokasi_gudang))

    # 1. Kurangi Stok Asal
    item_asal.stok -= jumlah
    
    # 2. Proses Tujuan
    if tujuan == "Jual Putus":
        # Stok hilang dari sistem (Terjual)
        flash(f"Berhasil menjual putus {jumlah} {item_asal.satuan} {item_asal.nama_item}.", "success")
        
    else:
        # Transfer ke Gudang Lain
        # Cek apakah barang ini sudah ada di gudang tujuan?
        item_tujuan = WarehouseItem.query.filter_by(
            nama_item=item_asal.nama_item, 
            lokasi_gudang=tujuan
        ).first()
        
        if item_tujuan:
            # Jika sudah ada, tambah stoknya
            item_tujuan.stok += jumlah
            item_tujuan.last_updated = datetime.utcnow()
        else:
            # Jika belum ada, buat baru di gudang tujuan
            baru = WarehouseItem(
                nama_item=item_asal.nama_item,
                kategori=item_asal.kategori,
                stok=jumlah,
                satuan=item_asal.satuan,
                lokasi_gudang=tujuan,
                lokasi_rak="Pindahan",
                last_updated=datetime.utcnow()
            )
            db.session.add(baru)
            
        flash(f"Berhasil memindahkan {jumlah} {item_asal.satuan} ke {tujuan}.", "success")

    db.session.commit()
    return redirect(url_for("gudang.index", lokasi=item_asal.lokasi_gudang))