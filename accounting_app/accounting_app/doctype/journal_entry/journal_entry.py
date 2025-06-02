# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from ...utils.account_controller import AccountController






class JournalEntry(Document, AccountController):
    def on_submit(self):
        entries = []

        for row in self.accounting_entries:
            entries.append({
                "posting_date": self.posting_date,
                "due_date": self.posting_date,
                "party": row.party,
                "account": row.account,
                "debit_amount": row.debit,
                "credit_amount": row.credit,
                "voucher_type": "Journal Entry",
                "voucher_number": self.name
            })

        self.make_gl_entries(entries)

    def on_cancel(self):
        self.make_reverse_gl_entries("Journal Entry", self.name)


    def validate(self):
        total_debit = 0
        total_credit = 0

        for entry in self.accounting_entries:
            total_debit += entry.debit or 0
            total_credit += entry.credit or 0

        self.total_debit = total_debit
        self.total_credit = total_credit
        self.difference = total_debit - total_credit

        if self.total_debit != self.total_credit:
            frappe.throw("Total Debit must equal Total Credit to submit.")

