import frappe


class StockController:
    def make_stock_ledger_entries(self, entries: list):
        for entry in entries:
            sle = frappe.new_doc("Stock Ledger Entry")
            sle.posting_date = entry.get("posting_date")
            sle.posting_time = entry.get("posting_time")
            sle.item = entry.get("item")
            sle.warehouse = entry.get("warehouse")
            sle.qty = entry.get("qty", 0)
            sle.valuation_rate = entry.get("valuation_rate", 0)
            sle.stock_value = sle.qty * sle.valuation_rate
            sle.voucher_type = entry.get("voucher_type")
            sle.voucher_no = entry.get("voucher_no")
            sle.is_cancelled = entry.get("is_cancelled", 0)
            sle.insert()

    def delete_stock_ledger_entries(self, voucher_type: str, voucher_no: str):
        sle_names = frappe.get_all(
            "Stock Ledger Entry",
            filters={
                "voucher_type": voucher_type,
                "voucher_no": voucher_no
            },
            pluck="name"
        )

        for name in sle_names:
            frappe.delete_doc("Stock Ledger Entry", name)

