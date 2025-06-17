# Copyright (c) 2025, asqalani and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime
from ...utils.account_controller import AccountController
from ...utils.stock_controller import StockController





class PurchaseInvoice(Document, AccountController, StockController):
    def on_submit(self):
        for item in self.items:
            inventory_account = frappe.db.get_value("Warehouse", item.warehouse, "inventory_account")
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
            },

            {
                "posting_date": self.posting_date,
                "due_date": self.payment_due_date,
                "party": None,
                "account": inventory_account,  # حساب المخزون (inventory)
                "debit_amount": self.total_amount,
                "credit_amount": 0,
                "voucher_type": "Purchase Invoice",
                "voucher_number": self.name
            },
            {
                "posting_date": self.posting_date,
                "due_date": self.payment_due_date,
                "party": self.supplier,
                "account": self.credit_to,  # عملنا credit بقيمة البضاعة من المورد (payable)
                "debit_amount": 0,
                "credit_amount": self.total_amount,
                "voucher_type": "Purchase Invoice",
                "voucher_number": self.name
            }
        ]
        self.make_gl_entries(entries)

        stock_entries = []

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
                    warehouse = %s 
                    
            """, (item.item, self.default_warehouse), as_dict=True)[0]

            total_qty = data.total_qty or 0
            total_value = data.total_value or 0

            valuation_rate = total_value / total_qty if total_qty else 0

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

