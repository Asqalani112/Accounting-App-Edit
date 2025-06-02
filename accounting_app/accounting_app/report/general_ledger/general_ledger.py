import frappe
from frappe.utils import get_first_day, today

def execute(filters=None):
    if not filters:
        filters = {}

    filters.setdefault("from_date", get_first_day(today()))
    filters.setdefault("to_date", today())

    data = frappe.db.sql("""
        SELECT
    gl.posting_date,
    gl.account,
    p.party_type AS party,  -- هنا بدّلنا party باسم النوع فقط
    gl.debit_amount,
    gl.credit_amount,
    gl.voucher_type,
    gl.voucher_number
FROM
    `tabGL Entry` gl
LEFT JOIN
    `tabParty` p ON gl.party = p.name
WHERE
    gl.posting_date BETWEEN %(from_date)s AND %(to_date)s
ORDER BY
    gl.posting_date ASC

    """, filters, as_dict=True)

    columns = [
        {"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "account", "label": "Account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"fieldname": "party", "label": "Party", "fieldtype": "Link", "options": "Party", "width": 130},
        {"fieldname": "debit_amount", "label": "Debit", "fieldtype": "Currency", "width": 100},
        {"fieldname": "credit_amount", "label": "Credit", "fieldtype": "Currency", "width": 100},
        {"fieldname": "voucher_type", "label": "Voucher Type", "fieldtype": "Data", "width": 120},
        {"fieldname": "voucher_number", "label": "Voucher Number", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 130}
    ]

    return columns, data
