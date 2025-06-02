# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ...utils.account_controller import AccountController






class SalesInvoice(Document, AccountController):
	def on_submit(self):
		entries = []

		# Debit: Customer
		entries.append({
			"posting_date": self.posting_date,
			"due_date": self.payment_due_date,
			"party": self.customer,
			"account": self.debit_to,
			"debit_amount": self.total_amount,
			"credit_amount": 0,
			"voucher_type": "Sales Invoice",
			"voucher_number": self.name
		})

		# Credit: Income Account
		entries.append({
			"posting_date": self.posting_date,
			"due_date": self.payment_due_date,
			"account": self.income_account,
			"debit_amount": 0,
			"credit_amount": self.total_amount,
			"voucher_type": "Sales Invoice",
			"voucher_number": self.name
		})

		self.make_gl_entries(entries)

	def on_cancel(self):
		self.make_reverse_gl_entries("Sales Invoice", self.name)

	def validate(self):
		# حساب amount لكل عنصر
		for item in self.items:
			item.amount = (item.qty or 0) * (item.rate or 0)

		# حساب الإجماليات
		self.total_qty = sum([item.qty or 0 for item in self.items])
		self.total_amount = sum([item.amount or 0 for item in self.items])

