import frappe


def make_gl_entries(entries: list):
    for entry in entries:
        gl = frappe.new_doc("GL Entry")
        gl.posting_date = entry.get("posting_date")
        gl.due_date = entry.get("due_date")
        gl.party = entry.get("party")
        gl.account = entry.get("account")
        gl.debit_amount = entry.get("debit_amount", 0)
        gl.credit_amount = entry.get("credit_amount", 0)
        gl.voucher_type = entry.get("voucher_type")
        gl.voucher_number = entry.get("voucher_number")
        gl.insert()

def make_reverse_gl_entries(voucher_type, voucher_number):
    original_entries = frappe.get_all("GL Entry",
        filters={"voucher_type": voucher_type, "voucher_number": voucher_number},
        fields=["posting_date", "due_date", "party", "account", "debit_amount", "credit_amount"]
    )

    for entry in original_entries:
        reversed_entry = frappe.new_doc("GL Entry")
        reversed_entry.posting_date = frappe.utils.nowdate()
        reversed_entry.due_date = entry.due_date
        reversed_entry.party = entry.party
        reversed_entry.account = entry.account
        reversed_entry.debit_amount = entry.credit_amount   # عكس القيم
        reversed_entry.credit_amount = entry.debit_amount
        reversed_entry.voucher_type = voucher_type
        reversed_entry.voucher_number = voucher_number
        reversed_entry.is_cancelled = 1
        reversed_entry.insert()
