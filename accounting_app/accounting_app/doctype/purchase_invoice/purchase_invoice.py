# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime
from ...utils.account_controller import AccountController
from ...utils.stock_controller import StockController





class PurchaseInvoice(Document, AccountController, StockController):
    def on_submit(self):
        entries = [
            {
                "posting_date": self.posting_date,
                "due_date": self.payment_due_date,
                "party": None,
                "account": self.expense_account,  # أو أي حساب مصروف مستخدم
                "debit_amount": self.total_amount,
                "credit_amount": 0,
                "voucher_type": "Purchase Invoice",
                "voucher_number": self.name
            },
            {
                "posting_date": self.posting_date,
                "due_date": self.payment_due_date,
                "party": self.supplier,
                "account": self.credit_to,  # حساب المورد (payable)
                "debit_amount": 0,
                "credit_amount": self.total_amount,
                "voucher_type": "Purchase Invoice",
                "voucher_number": self.name
            }
        ]
        self.make_gl_entries(entries)

        stock_entries = []
        valuation_rate = self.total_amount / self.total_qty if self.total_qty else 0
        for item in self.items:

            if not self.default_warehouse:
                frappe.throw(f"Please set Warehouse for item {item.item}")

            stock_entries.append({
                "posting_date": self.posting_date,
                "posting_time": nowtime(),
                "item": item.item,
                "warehouse": self.default_warehouse,
                "qty": item.qty,
                "valuation_rate": valuation_rate,
                "voucher_type": "Purchase Invoice",
                "voucher_no": self.name,
                "is_cancelled": 0
            })
        self.make_stock_ledger_entries(stock_entries)
        for item in self.items:

            if not self.default_warehouse:
                frappe.throw(f"Please set Warehouse for item {item.item}")

            inventory_account = frappe.db.get_value("Warehouse", self.default_warehouse, "inventory_account")
            if not inventory_account:
                frappe.throw(f"No inventory account linked to warehouse {self.default_warehouse}")

            amount = item.qty * item.rate

            self.make_gl_entries([
                {
                    "posting_date": self.posting_date,
                    "account": inventory_account,
                    "debit_amount": amount,
                    "credit_amount": 0,
                    "voucher_type": "Purchase Invoice",
                    "voucher_number": self.name
                }
            ])


    def on_cancel(self):
        self.make_reverse_gl_entries("Purchase Invoice", self.name)
        self.make_reverse_stock_ledger_entries("Purchase Invoice", self.name)

    def validate(self):
        # حساب amount لكل عنصر في الفاتورة
        for item in self.items:
            item.amount = (item.qty or 0) * (item.rate or 0)

        # حساب الإجماليات
        self.total_qty = sum([item.qty or 0 for item in self.items])
        self.total_amount = sum([item.amount or 0 for item in self.items])

