# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ...utils.account_controller import AccountController





class PaymentEntry(Document, AccountController):
    def on_submit(self):
        if self.payment_type == "Receive":
            # استلام من زبون
            entries = [
                {
                    "posting_date": self.posting_date,
                    "party": None,
                    "account": self.account_paid_to,  # البنك
                    "debit_amount": self.amount,
                    "credit_amount": 0,
                    "voucher_type": "Payment Entry",
                    "voucher_number": self.name
                },
                {
                    "posting_date": self.posting_date,
                    "party": self.party,
                    "account": self.account_paid_from,  # العميل (receivable)
                    "debit_amount": 0,
                    "credit_amount": self.amount,
                    "voucher_type": "Payment Entry",
                    "voucher_number": self.name
                }
            ]

        elif self.payment_type == "Pay":
            # دفع لمورد
            entries = [
                {
                    "posting_date": self.posting_date,
                    "party": self.party,
                    "account": self.account_paid_from,  # المورد (payable)
                    "debit_amount": self.amount,
                    "credit_amount": 0,
                    "voucher_type": "Payment Entry",
                    "voucher_number": self.name
                },
                {
                    "posting_date": self.posting_date,
                    "party": None,
                    "account": self.account_paid_to,  # البنك
                    "debit_amount": 0,
                    "credit_amount": self.amount,
                    "voucher_type": "Payment Entry",
                    "voucher_number": self.name
                }
            ]

        self.make_gl_entries(entries)

    def on_cancel(self):
        self.make_reverse_gl_entries("Payment Entry", self.name)
