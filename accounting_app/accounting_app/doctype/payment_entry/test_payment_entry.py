import frappe
from frappe.tests.utils import FrappeTestCase


class TestPaymentEntry(FrappeTestCase):
    def setUp(self):
        # Party (Customer)
        self.customer = frappe.get_doc({
            "doctype": "Party",
            "party_name": "Test Customer",
            "party_type": "Customer"
        }).insert(ignore_permissions=True)

        # Accounts
        self.bank_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "1010",
            "account_name": "Bank",
            "account_type": "Cash"
        }).insert(ignore_permissions=True)

        self.receivable_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "1111",
            "account_name": "Accounts Receivable",
            "account_type": "Receivable"
        }).insert(ignore_permissions=True)

    def test_payment_entry_receive_creates_gl_entries(self):
        amount = 300
        self.payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "naming_series": "PE-",
            "payment_type": "Receive",
            "posting_date": "2025-05-30",
            "party_type": "Customer",
            "party": self.customer.name,
            "account_paid_to": self.bank_account.name,
            "account_paid_from": self.receivable_account.name,
            "amount": amount
        })
        self.payment_entry.insert(ignore_permissions=True)
        self.payment_entry.submit()
        frappe.db.commit()

        gl_entries = frappe.get_all("GL Entry", filters={
            "voucher_type": "Payment Entry",
            "voucher_number": self.payment_entry.name
        }, fields=["account", "debit_amount", "credit_amount", "party"])

        self.assertEqual(len(gl_entries), 2)

        debit_entry = next(entry for entry in gl_entries if entry.debit_amount > 0)
        credit_entry = next(entry for entry in gl_entries if entry.credit_amount > 0)

        # Check values
        self.assertEqual(debit_entry.account, self.bank_account.name)
        self.assertEqual(debit_entry.debit_amount, amount)

        self.assertEqual(credit_entry.account, self.receivable_account.name)
        self.assertEqual(credit_entry.credit_amount, amount)
        self.assertEqual(credit_entry.party, self.customer.name)

    def tearDown(self):
        # Delete created documents
        frappe.delete_doc("Payment Entry", self.payment_entry.name)
        frappe.db.delete("GL Entry", {"voucher_type": "Payment Entry", "voucher_number": self.payment_entry.name})
        frappe.delete_doc("Party", self.customer.name)
        frappe.delete_doc("Account", self.bank_account.name)
        frappe.delete_doc("Account", self.receivable_account.name)



        frappe.db.commit()