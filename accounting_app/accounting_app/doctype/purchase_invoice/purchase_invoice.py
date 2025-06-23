# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt
from collections import defaultdict

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime
from ...utils.account_controller import AccountController
from ...utils.stock_controller import StockController





class PurchaseInvoice(Document, AccountController, StockController):
    def on_submit(self):
        entries = []
        inventory_totals = defaultdict(float)
        stock_entries = []

        for item in self.items:

            if not self.default_warehouse:
                frappe.throw(f"Please set Warehouse for item {item.item}")

            inventory_account = frappe.db.get_value("Warehouse", item.warehouse, "inventory_account")

            valuation_rate = item.rate or 0
            valuation_amount = item.qty * valuation_rate

            # اجمع حسب (الحساب، المخزن)
            key = (inventory_account, item.warehouse)
            inventory_totals[key] += valuation_amount

            stock_entries.append({
                "posting_date": self.posting_date,
                "posting_time": nowtime(),
                "item": item.item,
                "warehouse": item.warehouse,
                "qty": item.qty,
                "valuation_rate": valuation_rate,
                "voucher_type": "Purchase Invoice",
                "voucher_no": self.name,
                "is_cancelled": 0
            })

        # GL entry: Debit Inventory لكل حساب ومخزن
        for (account, warehouse), value in inventory_totals.items():
            if value:
                entries.append({
                    "posting_date": self.posting_date,
                    "due_date": self.payment_due_date,
                    "account": account,
                    "debit_amount": value,
                    "credit_amount": 0,
                    "voucher_type": "Purchase Invoice",
                    "voucher_number": self.name
                })
         # GL entry: Credit Supplier
        entries.append({
            "posting_date": self.posting_date,
            "due_date": self.payment_due_date,
            "party": self.supplier,
            "account": self.credit_to,
            "debit_amount": 0,
            "credit_amount": self.total_amount,
            "voucher_type": "Purchase Invoice",
            "voucher_number": self.name
        })
        self.make_gl_entries(entries)
        self.make_stock_ledger_entries(stock_entries)



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

