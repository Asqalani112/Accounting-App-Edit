import frappe


def execute(filters=None):
    from frappe.utils import flt, get_first_day, today

    if not filters:
        filters = {}

    filters.setdefault("from_date", get_first_day(today()))
    filters.setdefault("to_date", today())

    # Get child accounts with parent account type = Asset or Liability
    accounts = frappe.db.sql("""
        SELECT 
            child.name, 
            child.opening_balance,
            parent.account_type AS parent_type,
            child.account_type AS child_type
        FROM `tabAccount` child
        LEFT JOIN `tabAccount` parent ON child.parent_account = parent.name
        WHERE child.is_group = 0 
        AND parent.account_type IN ("Assets", "Liability")
    """, as_dict=True)

    data = []
    for acc in accounts:
        # Get debit/credit totals from GL Entry
        totals = frappe.db.sql("""
            SELECT
                SUM(debit_amount) as total_debit,
                SUM(credit_amount) as total_credit
            FROM `tabGL Entry`
            WHERE account = %s AND posting_date BETWEEN %s AND %s
        """, (acc.name, filters["from_date"], filters["to_date"]), as_dict=True)[0]

        balance = (acc.opening_balance or 0) + (totals.total_debit or 0) - (totals.total_credit or 0)

        data.append({
            "account": acc.name,
            "account_type": f"{acc.parent_type} ({acc.child_type})",
            "opening_balance": acc.opening_balance or 0,
            "total_debit": totals.total_debit or 0,
            "total_credit": totals.total_credit or 0,
            "balance": balance
        })

    columns = [
        {"fieldname": "account", "label": "Account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"fieldname": "account_type", "label": "Account Type", "fieldtype": "Data", "width": 120},
        {"fieldname": "opening_balance", "label": "Opening Balance", "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_debit", "label": "Total Debit", "fieldtype": "Currency", "width": 120},
        {"fieldname": "total_credit", "label": "Total Credit", "fieldtype": "Currency", "width": 120},
        {"fieldname": "balance", "label": "Balance", "fieldtype": "Currency", "width": 120},
    ]

    return columns, data
