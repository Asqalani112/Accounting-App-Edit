import frappe
from frappe.tests.utils import FrappeTestCase
from ...doctype.sales_invoice.sales_invoice import on_submit

class TestSalesInvoice(FrappeTestCase):

    def setUp(self):
        # Create Party (Customer)
        self.customer = frappe.get_doc({
            "doctype": "Party",
            "party_name": "Test Customer",
            "party_type": "Customer"
        }).insert(ignore_permissions=True)

        # Create Accounts
        self.debit_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "1000",
            "account_name": "Accounts Receivable",
            "account_type": "Receivable"
        }).insert(ignore_permissions=True)

        self.income_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "4000",
            "account_name": "Sales",
            "account_type": "Income"
        }).insert(ignore_permissions=True)

        # Create Item
        self.item = frappe.get_doc({
            "doctype": "Item",
            "item_code": "ITEMmmmmm-001",
            "item_name": "Test Item",
            "default_unit_of_measurement": "Box",
            "standard_selling_rate": 100
        }).insert(ignore_permissions=True)

    def test_sales_invoice_gl_entry(self):
        # Create Sales Invoice
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "naming_series": "SINV-",
            "customer": self.customer.name,
            "posting_date": "2025-05-27",
            "payment_due_date": "2025-06-01",
            "debit_to": self.debit_account.name,
            "income_account": self.income_account.name,
            "items": [
                {"item": self.item.name, "qty": 2, "rate": 100}
            ]
        })
        invoice.insert(ignore_permissions=True)
        invoice.submit()
        frappe.db.commit()

        # Get GL Entries
        gl_entries = frappe.get_all("GL Entry", filters={
            "voucher_type": "Sales Invoice",
            "voucher_number": invoice.name
        }, fields=["account", "debit_amount", "credit_amount", "party", "posting_date"])

        self.assertEqual(len(gl_entries), 2)

        # Verify totals
        total_debit = sum([entry.debit_amount for entry in gl_entries])
        total_credit = sum([entry.credit_amount for entry in gl_entries])
        self.assertEqual(total_debit, 200)
        self.assertEqual(total_credit, 200)

        accounts = [entry.account for entry in gl_entries]
        self.assertIn(self.debit_account.name, accounts)
        self.assertIn(self.income_account.name, accounts)

        # Verify party is attached to receivable line
        receivable_entry = next(e for e in gl_entries if e.account == self.debit_account.name)
        self.assertEqual(receivable_entry.party, self.customer.name)
