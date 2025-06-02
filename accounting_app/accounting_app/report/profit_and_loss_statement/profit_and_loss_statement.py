import frappe
from frappe.utils import get_first_day, today

def execute(filters=None):
    if not filters:
        filters = {}

    filters.setdefault("from_date", get_first_day(today()))
    filters.setdefault("to_date", today())

    # إجلب حسابات الإيرادات والمصاريف فقط
    accounts = frappe.get_all(
        "Account",
        filters={
            "account_type": ["in", ["Income", "Expense"]],
            "is_group": 0
        },
        fields=["name", "account_type"]
    )

    data = []
    for acc in accounts:
        totals = frappe.db.sql("""
            SELECT
                SUM(gl.debit_amount) as total_debit,
                SUM(gl.credit_amount) as total_credit
            FROM `tabGL Entry` gl
            
            WHERE gl.account = %s
              AND gl.posting_date BETWEEN %s AND %s
              
        """, (acc.name, filters["from_date"], filters["to_date"]), as_dict=True)[0]

        balance = (totals.total_credit or 0) - (totals.total_debit or 0)
        data.append({
            "account": acc.name,
            "account_type": acc.account_type,
            "total_debit": totals.total_debit or 0,
            "total_credit": totals.total_credit or 0,
            "balance": balance
        })

    columns = [
        {"fieldname": "account", "label": "Account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"fieldname": "account_type", "label": "Account Type", "fieldtype": "Data", "width": 120},
        {"fieldname": "total_debit", "label": "Total Debit", "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_credit", "label": "Total Credit", "fieldtype": "Currency", "width": 120},
        {"fieldname": "balance", "label": "Balance", "fieldtype": "Currency", "width": 120},
    ]

    return columns, data
