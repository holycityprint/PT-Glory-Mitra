from flask import Blueprint, render_template, request, make_response, redirect, url_for, flash
from weasyprint import HTML
from models import db, MarketingProspect, MarketingLead, MarketingProject, MarketingFollowUp
from datetime import datetime

# =====================================================
# === INISIALISASI BLUEPRINT MARKETING ===============
# =====================================================
marketing_bp = Blueprint(
    'marketing',
    __name__,
    template_folder='../templates',
    url_prefix='/marketing'
)

# =====================================================
# === DASHBOARD MARKETING =============================
# =====================================================
@marketing_bp.route('/')
def marketing_dashboard():
    """Dashboard utama marketing"""
    return render_template(
        'marketing/dashboard.html',
        title="Dashboard Marketing"
    )


# =====================================================
# === DATA LEADS / PROSPEK ============================
# =====================================================
@marketing_bp.route('/leads')
def marketing_leads():
    """Daftar prospek dan leads marketing"""
    try:
        prospects = MarketingProspect.query.order_by(MarketingProspect.created_at.desc()).all()
    except Exception:
        prospects = MarketingProspect.query.order_by(MarketingProspect.id.desc()).all()

    try:
        leads = MarketingLead.query.order_by(MarketingLead.created_at.desc()).all()
    except Exception:
        leads = MarketingLead.query.order_by(MarketingLead.id.desc()).all()

    return render_template(
        'marketing/leads.html',
        title="Data Leads",
        prospects=prospects,
        leads=leads
    )


# =====================================================
# === CAMPAIGNS =======================================
# =====================================================
@marketing_bp.route('/campaigns')
def marketing_campaigns():
    """Halaman kampanye promosi"""
    return render_template(
        'marketing/campaigns.html',
        title="Campaign Promosi"
    )


# =====================================================
# === CLIENTS / CUSTOMER ==============================
# =====================================================
@marketing_bp.route('/clients')
def marketing_clients():
    """Daftar pelanggan atau klien"""
    return render_template(
        'marketing/clients.html',
        title="Customer / Client List"
    )


# =====================================================
# === TARGETS & PERFORMANCE ===========================
# =====================================================
@marketing_bp.route('/targets')
def marketing_targets():
    """Target dan performa tim marketing"""
    try:
        projects = MarketingProject.query.order_by(MarketingProject.created_at.desc()).all()
    except Exception:
        projects = MarketingProject.query.order_by(MarketingProject.id.desc()).all()

    try:
        followups = MarketingFollowUp.query.order_by(MarketingFollowUp.date.desc()).all()
    except Exception:
        followups = MarketingFollowUp.query.order_by(MarketingFollowUp.id.desc()).all()

    return render_template(
        'marketing/targets.html',
        title="Target & Kinerja Tim",
        projects=projects,
        followups=followups
    )


# =====================================================
# === SURAT PENAWARAN (FORM + PDF) ====================
# =====================================================
@marketing_bp.route('/offer-letter', methods=['GET', 'POST'])
def marketing_offer_letter():
    """Form input + generate PDF surat penawaran profesional"""
    if request.method == 'POST':
        company_name = request.form.get("company_name") or "Perusahaan Tanpa Nama"
        company_address = request.form.get("company_address") or "-"
        products_text = request.form.get("products") or ""
        products = [p.strip() for p in products_text.splitlines() if p.strip()]

        html_content = render_template(
            'marketing/offer_letter.html',
            title="Surat Penawaran",
            company_name=company_name,
            company_address=company_address,
            products=products,
            as_pdf=True,
        )

        try:
            pdf = HTML(string=html_content, base_url=request.root_url).write_pdf()
            resp = make_response(pdf)
            resp.headers["Content-Type"] = "application/pdf"
            resp.headers["Content-Disposition"] = f'inline; filename=surat_penawaran_{company_name}.pdf'
            return resp
        except Exception as e:
            print("ERROR saat generate PDF:", e)
            flash("Gagal membuat PDF — periksa logo atau isian.", "danger")
            return redirect(url_for('marketing.marketing_offer_letter'))

    # GET → tampilkan form input
    return render_template(
        'marketing/offer_letter.html',
        title="Surat Penawaran",
        as_pdf=False
    )


# =====================================================
# === FUNGSI TAMBAHAN UNTUK INPUT / CRUD DATA =========
# =====================================================
@marketing_bp.route('/add_prospect', methods=['POST'])
def add_prospect():
    """Tambah data prospek baru"""
    name = request.form.get('client_name')
    company = request.form.get('company')
    contact = request.form.get('contact')
    email = request.form.get('email')
    source = request.form.get('source')

    if not name:
        flash("Nama prospek wajib diisi!", "danger")
        return redirect(url_for('marketing.marketing_leads'))

    new_data = MarketingProspect(
        client_name=name,
        company=company,
        contact=contact,
        email=email,
        source=source
    )
    db.session.add(new_data)
    db.session.commit()
    flash("Prospek baru berhasil ditambahkan!", "success")
    return redirect(url_for('marketing.marketing_leads'))


@marketing_bp.route('/add_lead', methods=['POST'])
def add_lead():
    """Tambah lead baru"""
    lead = MarketingLead(
        prospect_id=request.form.get('prospect_id'),
        product_interest=request.form.get('product_interest'),
        estimated_value=request.form.get('estimated_value'),
        stage=request.form.get('stage'),
        notes=request.form.get('notes')
    )
    db.session.add(lead)
    db.session.commit()
    flash("Lead baru berhasil ditambahkan!", "success")
    return redirect(url_for('marketing.marketing_leads'))


@marketing_bp.route('/add_project', methods=['POST'])
def add_project():
    """Tambah proyek baru"""
    project = MarketingProject(
        lead_id=request.form.get('lead_id'),
        project_name=request.form.get('project_name'),
        start_date=request.form.get('start_date'),
        end_date=request.form.get('end_date'),
        status=request.form.get('status'),
        budget=request.form.get('budget'),
        remarks=request.form.get('remarks')
    )
    db.session.add(project)
    db.session.commit()
    flash("Project baru berhasil ditambahkan!", "success")
    return redirect(url_for('marketing.marketing_targets'))


@marketing_bp.route('/add_followup', methods=['POST'])
def add_followup():
    """Tambah follow-up baru"""
    followup = MarketingFollowUp(
        project_id=request.form.get('project_id'),
        contact_person=request.form.get('contact_person'),
        method=request.form.get('method'),
        result=request.form.get('result')
    )
    db.session.add(followup)
    db.session.commit()
    flash("Follow-up berhasil ditambahkan!", "success")
    return redirect(url_for('marketing.marketing_targets'))