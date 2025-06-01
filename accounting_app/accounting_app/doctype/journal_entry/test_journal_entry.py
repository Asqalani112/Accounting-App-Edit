import frappe
from frappe.tests.utils import FrappeTestCase

class TestJournalEntry(FrappeTestCase):

    def setUp(self):
        self.debit_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "1100",
            "account_name": "Cash Account",
            "account_type": "Cash"
        }).insert(ignore_permissions=True)

        self.credit_account = frappe.get_doc({
            "doctype": "Account",
            "account_number": "2000",
            "account_name": "Liability Account",
            "account_type": "Expense"
        }).insert(ignore_permissions=True)

    def test_journal_entry_balancing(self):
        journal = frappe.get_doc({
            "doctype": "Journal Entry",
            "naming_series":"JE-",
            "posting_date": "2025-05-28",
            "accounting_entries": [
                {"account": self.debit_account.name, "debit": 300, "credit": 0},
                {"account": self.credit_account.name, "debit": 0, "credit": 300}
            ]
        })
        journal.insert(ignore_permissions=True)
        journal.submit()
        frappe.db.commit()

        # Check GL Entries created
        gl_entries = frappe.get_all("GL Entry", filters={
            "voucher_type": "Journal Entry",
            "voucher_number": journal.name
        }, fields=["account", "debit_amount", "credit_amount", "posting_date"])

        self.assertEqual(len(gl_entries), 2)

        total_debit = sum([e.debit_amount for e in gl_entries])
        total_credit = sum([e.credit_amount for e in gl_entries])

        self.assertEqual(total_debit, 300)
        self.assertEqual(total_credit, 300)
