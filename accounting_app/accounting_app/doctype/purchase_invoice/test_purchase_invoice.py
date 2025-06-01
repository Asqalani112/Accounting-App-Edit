import frappe
from frappe.tests.utils import FrappeTestCase

class TestPurchaseInvoice(FrappeTestCase):

    def setUp(self):
        # Create Party (Supplier)
        self.supplier = frappe.get_doc({
            "doctype": "Party",
            "party_name": "Test Supplier",
            "party_type": "Supplier"
        }).insert(ignore_permissions=True)

        # Create Accounts
        self.credit_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "2000",
            "account_name": "Accounts Payable",
            "account_type": "Payable"
        }).insert(ignore_permissions=True)

        self.expense_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "5000",
            "account_name": "Purchases",
            "account_type": "Expense"
        }).insert(ignore_permissions=True)

        # Create Item
        self.item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "ITEM-PI-001",
            "item_name": "Test Item PI",
            "default_unit_of_measurement": "Box",
            "standard_purchase_rate": 50
        }).insert(ignore_permissions=True)

    def test_purchase_invoice_gl_entry(self):
        # Create Purchase Invoice
        invoice = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "naming_series": "PINV-",
            "supplier": self.supplier.name,
            "posting_date": "2025-05-27",
            "payment_due_date": "2025-06-01",
            "credit_to": self.credit_account.name,
            "expense_account": self.expense_account.name,
            "items": [
                {"item": self.item.name, "qty": 3, "rate": 50}
            ]
        })
        invoice.insert(ignore_permissions=True)
        invoice.submit()
        frappe.db.commit()

        # Get GL Entries
        gl_entries = frappe.get_all("GL Entry", filters={
            "voucher_type": "Purchase Invoice",
            "voucher_number": invoice.name
        }, fields=["account", "debit_amount", "credit_amount", "party", "posting_date"])

        self.assertEqual(len(gl_entries), 2)

        # Check total amounts
        total_debit = sum([entry.debit_amount for entry in gl_entries])
        total_credit = sum([entry.credit_amount for entry in gl_entries])
        self.assertEqual(total_debit, 150)
        self.assertEqual(total_credit, 150)

        accounts = [entry.account for entry in gl_entries]
        self.assertIn(self.expense_account.name, accounts)
        self.assertIn(self.credit_account.name, accounts)

        # Check if party is linked to payable line
        payable_entry = next(e for e in gl_entries if e.account == self.credit_account.name)
        self.assertEqual(payable_entry.party, self.supplier.name)
