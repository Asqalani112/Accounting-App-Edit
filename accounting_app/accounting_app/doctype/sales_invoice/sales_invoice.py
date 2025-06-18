# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime
from ...utils.account_controller import AccountController
from ...utils.stock_controller import StockController






class SalesInvoice(Document, AccountController, StockController):
	def on_submit(self):

		inventory_account = frappe.get_doc("Account", "Account-0081")
		expense_account = frappe.get_doc("Account", "Account-0080")

		#get valution rate
		for item in self.items:

			if not self.default_warehouse:
				frappe.throw(f"Please set Warehouse for item {item.item}")

			data = frappe.db.sql("""
		               SELECT
		                   SUM(qty) AS total_qty,
		                   SUM(stock_value) AS total_value
		               FROM `tabStock Ledger Entry`
		               WHERE
		                   item = %s AND
		                   warehouse = %s AND
		                   docstatus = 1

		           """, (item.item, self.default_warehouse), as_dict=True)[0]

			total_qty = data.total_qty or 0
			total_value = data.total_value or 0

			valuation_rate = total_value / total_qty if total_qty else 0


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


		entries.append({
			"posting_date": self.posting_date,
			"due_date": self.payment_due_date,
			"account": inventory_account.name,
			"debit_amount": 0,
			"credit_amount": self.total_qty * valuation_rate,
			"voucher_type": "Sales Invoice",
			"voucher_number": self.name
		})

		entries.append({
			"posting_date": self.posting_date,
			"due_date": self.payment_due_date,
			"account": expense_account.name,
			"debit_amount": self.total_qty * valuation_rate,
			"credit_amount": 0,
			"voucher_type": "Sales Invoice",
			"voucher_number": self.name
		})

		self.make_gl_entries(entries)
		stock_entries = []

		for item in self.items:
			stock_entries.append({
				"posting_date": self.posting_date,
				"posting_time": nowtime(),
				"item": item.item,
				"warehouse": self.default_warehouse,
				"qty": -item.qty,
				"valuation_rate": valuation_rate,
				"voucher_type": "Sales Invoice",
				"voucher_no": self.name,
				"is_cancelled": 0
			})
		self.make_stock_ledger_entries(stock_entries)

	def on_cancel(self):
		self.make_reverse_gl_entries("Sales Invoice", self.name)
		self.make_reverse_stock_ledger_entries("Sales Invoice", self.name)

	def validate(self):
		# حساب amount لكل عنصر
		for item in self.items:
			item.amount = (item.qty or 0) * (item.rate or 0)

		# حساب الإجماليات
		self.total_qty = sum([item.qty or 0 for item in self.items])
		self.total_amount = sum([item.amount or 0 for item in self.items])

