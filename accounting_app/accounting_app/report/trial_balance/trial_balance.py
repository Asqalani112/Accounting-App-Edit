import frappe
from frappe.utils import get_first_day, today

def execute(filters=None):
    if not filters:
        filters = {}

    filters.setdefault("from_date", get_first_day(today()))
    filters.setdefault("to_date", today())

    conditions = "posting_date BETWEEN %(from_date)s AND %(to_date)s AND account IS NOT NULL AND account != ''"

    if filters.get("account_type") and filters["account_type"] != "All":
        conditions += " AND account IN (SELECT name FROM `tabAccount` WHERE account_type = %(account_type)s)"

    data = frappe.db.sql(f"""
        SELECT
            account,
            (SELECT account_type FROM `tabAccount` WHERE name = gl.account) AS account_type,
            SUM(debit_amount) AS total_debit,
            SUM(credit_amount) AS total_credit,
            SUM(debit_amount - credit_amount) AS balance
        FROM `tabGL Entry` gl
        WHERE {conditions}
        GROUP BY account
        ORDER BY account
    """, filters, as_dict=True)

    columns = [
        {"fieldname": "account", "label": "Account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"fieldname": "account_type", "label": "Account Type", "fieldtype": "Data", "width": 120},
        {"fieldname": "total_debit", "label": "Total Debit", "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_credit", "label": "Total Credit", "fieldtype": "Currency", "width": 120},
        {"fieldname": "balance", "label": "Balance", "fieldtype": "Currency", "width": 120}
    ]

    return columns, data
