
frappe.ui.form.on('Journal Entry', {
  validate: function(frm) {
    update_totals(frm);
    if (frm.doc.total_debit !== frm.doc.total_credit) {
      frappe.throw('Total Debit must equal Total Credit to submit.');
    }
  }
});

frappe.ui.form.on('Accounting Entries', {
  debit: function(frm, cdt, cdn) {
    update_totals(frm);
  },
  credit: function(frm, cdt, cdn) {
    update_totals(frm);
  },
  accounting_entries_remove: function(frm) {
    update_totals(frm);
  }
});

function update_totals(frm) {
  let total_debit = 0;
  let total_credit = 0;

  (frm.doc.accounting_entries || []).forEach(row => {
    total_debit += row.debit || 0;
    total_credit += row.credit || 0;
  });

  frm.set_value('total_debit', total_debit);
  frm.set_value('total_credit', total_credit);
  frm.set_value('difference', total_debit - total_credit);
}
