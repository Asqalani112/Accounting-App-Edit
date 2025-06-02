// Copyright (c) 2025, asqalani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoice', {
	onload: function(frm) {
    frm.set_query('supplier', () => {
      return {
        filters: {
          party_type: 'supplier'
        }
      };
    });
    frm.set_query('credit_to', () =>{
        return{
            filters: {
            account_type: 'Payable',
            is_group: 0
            }
        }
    });
    frm.set_query('expense_account', () =>{
        return{
            filters: {
            account_type: 'Expense',
            is_group: 0
            }
        }
    });

  }
});
frappe.ui.form.on('Purchase Invoice', {
  items_on_form_rendered: function(frm) {
    update_totals(frm);
  },
  validate: function(frm) {
    update_totals(frm); // تأكيد آخر قبل الحفظ
  }
});

frappe.ui.form.on('Purchase Invoice Item', {
  qty: function(frm, cdt, cdn) {
    calculate_amount(cdt, cdn);
    update_totals(frm);
  },
  rate: function(frm, cdt, cdn) {
    calculate_amount(cdt, cdn);
    update_totals(frm);
  }
});

function calculate_amount(cdt, cdn) {
  let row = locals[cdt][cdn];
  let amount = (row.qty || 0) * (row.rate || 0);
  frappe.model.set_value(cdt, cdn, 'amount', amount);
}

function update_totals(frm) {
  let total_qty = 0;
  let total_amount = 0;

  (frm.doc.items || []).forEach(row => {
    total_qty += row.qty || 0;
    total_amount += row.amount || 0;
  });

  frm.set_value('total_qty', total_qty);
  frm.set_value('total_amount', total_amount);
}
