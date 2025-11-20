from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from holycity.extensions import db, csrf
from models import DeliveryOrder, WarehouseItem # ✅ Import WarehouseItem

pengiriman_bp = Blueprint("pengiriman", __name__, url_prefix="/pengiriman")

def generate_no_surat():
    now = datetime.now()
    bulan_romawi = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    bln = bulan_romawi[now.month - 1]
    thn = now.year
    last_order = DeliveryOrder.query.order_by(DeliveryOrder.id.desc()).first()
    if last_order:
        try:
            last_no = int(last_order.no_surat.split("/")[-1])
            new_no = last_no + 1
        except:
            new_no = 1
    else:
        new_no = 1
    return f"SJ/{thn}/{bln}/{new_no:03d}"

@pengiriman_bp.route("/")
@login_required
def index():
    orders = DeliveryOrder.query.order_by(DeliveryOrder.tanggal.desc()).all()
    return render_template("pengiriman/index.html", orders=orders)

@csrf.exempt
@pengiriman_bp.route("/buat", methods=["GET", "POST"])
@login_required
def buat_surat():
    # ✅ Ambil semua barang dari gudang untuk pilihan di form
    stok_gudang = WarehouseItem.query.order_by(WarehouseItem.nama_item.asc()).all()
    no_otomatis = generate_no_surat()
    
    if request.method == "POST":
        # Ambil Data Form
        tgl = datetime.strptime(request.form.get("tanggal"), "%Y-%m-%d")
        
        # Ambil List Barang yang dipilih (Array)
        item_ids = request.form.getlist("item_id[]")
        qtys = request.form.getlist("qty[]")
        
        # Validasi Stok & Kurangi Stok
        barang_text_list = []
        
        for i in range(len(item_ids)):
            item_id = item_ids[i]
            jumlah_kirim = float(qtys[i])
            
            # Cari barang di database
            barang = WarehouseItem.query.get(item_id)
            
            if barang:
                if barang.stok < jumlah_kirim:
                    flash(f"Gagal! Stok '{barang.nama_item}' tidak cukup. Sisa: {barang.stok}", "danger")
                    return redirect(url_for("pengiriman.buat_surat"))
                
                # ✅ LOGIKA POTONG STOK OTOMATIS
                barang.stok -= jumlah_kirim
                barang.last_updated = datetime.utcnow()
                
                # Simpan nama barang ke list text agar muncul di cetakan surat jalan
                barang_text_list.append(f"{barang.nama_item} - {jumlah_kirim} {barang.satuan}")
        
        # Gabungkan list barang jadi string (untuk disimpan di kolom list_barang)
        final_list_barang = "\n".join(barang_text_list)

        # Simpan Surat Jalan
        baru = DeliveryOrder(
            no_surat=request.form.get("no_surat"),
            tanggal=tgl,
            nama_penerima=request.form.get("nama_penerima"),
            alamat_tujuan=request.form.get("alamat_tujuan"),
            no_telp=request.form.get("no_telp"),
            nama_kurir=request.form.get("nama_kurir"),
            nopol_kendaraan=request.form.get("nopol_kendaraan"),
            jenis_kendaraan=request.form.get("jenis_kendaraan"),
            list_barang=final_list_barang, # Hasil otomatis dari pilihan
            catatan=request.form.get("catatan")
        )
        
        db.session.add(baru)
        db.session.commit()
        
        flash("Surat Jalan berhasil dibuat & Stok Gudang otomatis berkurang.", "success")
        return redirect(url_for("pengiriman.cetak", id=baru.id))

    return render_template("pengiriman/buat.html", no_otomatis=no_otomatis, today=datetime.now().date(), stok_gudang=stok_gudang)

@pengiriman_bp.route("/cetak/<int:id>")
@login_required
def cetak(id):
    order = DeliveryOrder.query.get_or_404(id)
    barang_lines = order.list_barang.split('\n') if order.list_barang else []
    return render_template("pengiriman/cetak.html", order=order, barang_lines=barang_lines)