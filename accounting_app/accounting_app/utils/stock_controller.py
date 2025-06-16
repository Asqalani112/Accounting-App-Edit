import frappe
from frappe.utils import nowtime


class StockController:
    def make_stock_ledger_entries(self, entries: list):
        for entry in entries:
            sle = frappe.new_doc("Stock Ledger Entry")
            sle.posting_date = entry.get("posting_date")
            sle.posting_time = entry.get("posting_time")
            sle.item = entry.get("item")
            sle.warehouse = entry.get("warehouse")
            sle.qty = entry.get("qty")
            sle.valuation_rate = entry.get("valuation_rate")
            sle.stock_value = sle.qty * sle.valuation_rate
            sle.voucher_type = entry.get("voucher_type")
            sle.voucher_no = entry.get("voucher_no")
            sle.is_cancelled = entry.get("is_cancelled", 0)
            sle.insert()
            sle.submit()


    def make_reverse_stock_ledger_entries(self, voucher_type, voucher_no):
        original_entries = frappe.get_all(
            "Stock Ledger Entry",
            filters = {
                "voucher_type" : voucher_type,
                "voucher_no" : voucher_no,
                "is_cancelled": 0
            },
            fields = [
                "item", "warehouse", "qty", "valuation_rate", "posting_date", "posting_time"
            ]
        )
        for entry in original_entries:
            reverse = frappe.new_doc("Stock Ledger Entry")
            reverse.item = entry.item
            reverse.warehouse = entry.warehouse
            reverse.qty = -entry.qty #عكسنا القيم
            reverse.valuation_rate = entry.valuation_rate
            reverse.stock_value = reverse.qty * reverse.valuation_rate
            reverse.posting_date = frappe.utils.today()
            reverse.posting_time = nowtime()
            reverse.voucher_type = voucher_type
            reverse.voucher_no = voucher_no
            reverse.is_cancelled = 1
            reverse.insert()

