# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ...utils.gl_entry import make_gl_entries
from ...utils.gl_entry import make_reverse_gl_entries





def on_submit(doc, method):
    if doc.payment_type == "Receive":
        # استلام من زبون
        entries = [
            {
                "posting_date": doc.posting_date,
                "party": None,
                "account": doc.account_paid_to,  # البنك
                "debit_amount": doc.amount,
                "credit_amount": 0,
                "voucher_type": "Payment Entry",
                "voucher_number": doc.name
            },
            {
                "posting_date": doc.posting_date,
                "party": doc.party,
                "account": doc.account_paid_from,  # العميل (receivable)
                "debit_amount": 0,
                "credit_amount": doc.amount,
                "voucher_type": "Payment Entry",
                "voucher_number": doc.name
            }
        ]

    elif doc.payment_type == "Pay":
        # دفع لمورد
        entries = [
            {
                "posting_date": doc.posting_date,
                "party": doc.party,
                "account": doc.account_paid_from,  # المورد (payable)
                "debit_amount": doc.amount,
                "credit_amount": 0,
                "voucher_type": "Payment Entry",
                "voucher_number": doc.name
            },
            {
                "posting_date": doc.posting_date,
                "party": None,
                "account": doc.account_paid_to,  # البنك
                "debit_amount": 0,
                "credit_amount": doc.amount,
                "voucher_type": "Payment Entry",
                "voucher_number": doc.name
            }
        ]



    make_gl_entries(entries)

def on_cancel(doc, method):
    make_reverse_gl_entries("Payment Entry", doc.name)


class PaymentEntry(Document):
	pass
