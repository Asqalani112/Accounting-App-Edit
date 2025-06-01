# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ...utils.gl_entry import make_gl_entries
from ...utils.gl_entry import make_reverse_gl_entries



def on_submit(doc, method):

	entries = []

	# Debit: Customer
	entries.append({
		"posting_date": doc.posting_date,
		"due_date": doc.payment_due_date,
		"party": doc.customer,
		"account": doc.debit_to,
		"debit_amount": doc.total_amount,
		"credit_amount": 0,
		"voucher_type": "Sales Invoice",
		"voucher_number": doc.name
	})

	# Credit: Income Account
	entries.append({
		"posting_date": doc.posting_date,
		"due_date": doc.payment_due_date,
		"account": doc.income_account,
		"debit_amount": 0,
		"credit_amount": doc.total_amount,
		"voucher_type": "Sales Invoice",
		"voucher_number": doc.name
	})

	make_gl_entries(entries)

def on_cancel(doc, method):
	make_reverse_gl_entries("Sales Invoice", doc.name)


class SalesInvoice(Document):
	def validate(self):
		# حساب amount لكل عنصر
		for item in self.items:
			item.amount = (item.qty or 0) * (item.rate or 0)

		# حساب الإجماليات
		self.total_qty = sum([item.qty or 0 for item in self.items])
		self.total_amount = sum([item.amount or 0 for item in self.items])

