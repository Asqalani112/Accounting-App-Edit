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
        qty = 3
        rate = 50
        amount = qty * rate
        # Create Purchase Invoice
        self.invoice = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "naming_series": "PINV-",
            "supplier": self.supplier.name,
            "posting_date": "2025-05-27",
            "payment_due_date": "2025-06-01",
            "credit_to": self.credit_account.name,
            "expense_account": self.expense_account.name,
            "items": [
                {"item": self.item.name, "qty": qty, "rate": rate}
            ]
        })
        self.invoice.insert(ignore_permissions=True)
        self.invoice.submit()
        frappe.db.commit()

        # Get GL Entries
        gl_entries = frappe.get_all("GL Entry", filters={
            "voucher_type": "Purchase Invoice",
            "voucher_number": self.invoice.name
        }, fields=["account", "debit_amount", "credit_amount", "party", "posting_date"])

        self.assertEqual(len(gl_entries), 2)

        # Check total amounts
        total_debit = sum([entry.debit_amount for entry in gl_entries])
        total_credit = sum([entry.credit_amount for entry in gl_entries])
        self.assertEqual(total_debit, amount)
        self.assertEqual(total_credit, amount)

        accounts = [entry.account for entry in gl_entries]
        self.assertIn(self.expense_account.name, accounts)
        self.assertIn(self.credit_account.name, accounts)

        # Check if party is linked to payable line
        payable_entry = next(entry for entry in gl_entries if entry.account == self.credit_account.name)
        self.assertEqual(payable_entry.party, self.supplier.name)

    def tearDown(self):
        # Delete created documents
        frappe.delete_doc("Purchase Invoice", self.invoice.name)
        frappe.db.delete("GL Entry", {"voucher_type": "Purchase Invoice", "voucher_number": self.invoice.name})
        frappe.delete_doc("Party", self.supplier.name)
        frappe.delete_doc("Account", self.credit_account.name)
        frappe.delete_doc("Account", self.expense_account.name)
        frappe.delete_doc("Item", self.item.name)


        frappe.db.commit()