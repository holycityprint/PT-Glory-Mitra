# services/accounting_service.py
from datetime import datetime
from sqlalchemy import func, case
from holycity.extensions import db
from models import Transaction

def get_summary():
    """Hitung saldo, pendapatan, pengeluaran bulan berjalan."""
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    income = (db.session.query(func.sum(Transaction.amount))
              .filter(Transaction.category == "income",
                      Transaction.date >= month_start)
              .scalar() or 0.0)
    expense = (db.session.query(func.sum(Transaction.amount))
               .filter(Transaction.category == "expense",
                       Transaction.date >= month_start)
               .scalar() or 0.0)
    balance = (db.session.query(func.sum(
                    case((Transaction.category == "income", Transaction.amount),
                         else_=-Transaction.amount)))
               .scalar() or 0.0)

    return {"income": income, "expense": expense, "balance": balance}


def get_mutations(mode):
    """Ambil daftar mutasi keuangan berdasarkan mode waktu."""
    today = datetime.utcnow().date()
    query = Transaction.query

    if mode == "daily":
        query = query.filter(func.date(Transaction.date) == today)
    elif mode == "monthly":
        query = query.filter(func.extract("month", Transaction.date) == today.month,
                             func.extract("year", Transaction.date) == today.year)
    elif mode == "yearly":
        query = query.filter(func.extract("year", Transaction.date) == today.year)

    return query.order_by(Transaction.date.desc()).all()


def add_transaction(data, filename=None):
    """Tambah transaksi baru ke database."""
    txn = Transaction(
        date=datetime.utcnow().date(),
        category=data.get("category"),
        description=data.get("description"),
        source=data.get("source"),
        account=data.get("account"),
        amount=float(data.get("amount", 0)),
        receipt=filename,
    )
    db.session.add(txn)
    db.session.commit()
    return txn