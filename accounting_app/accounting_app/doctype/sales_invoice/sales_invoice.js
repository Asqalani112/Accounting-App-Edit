frappe.ui.form.on('Sales Invoice', {
	onload: function(frm) {
    frm.set_query('customer', () => {
      return {
        filters: {
          party_type: 'customer'
        }
      };
    });
    frm.set_query('debit_to', () =>{
        return{
            filters: {
            account_type: 'Receivable',
            is_group: 0
            }
        }
    });
    frm.set_query('income_account', () =>{
        return{
            filters: {
            account_type: 'Income',
            is_group: 0
            }
        }
    });

  }
});


frappe.ui.form.on('Sales Invoice', {
  items_on_form_rendered: function(frm) {
    update_totals(frm);
  },
  validate: function(frm) {
    update_totals(frm); // تأكيد آخر قبل الحفظ
  }
});

frappe.ui.form.on('Sales Invoice Item', {
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
