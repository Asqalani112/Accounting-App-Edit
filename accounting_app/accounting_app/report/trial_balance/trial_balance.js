frappe.query_reports["Trial Balance"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "account_type",
            "label": "Account Type",
            "fieldtype": "Select",
            "options": "All\nReceivable\nPayable\nCash\nBank\nIncome\nExpense",
            "default": "All"
        }
    ]
}
