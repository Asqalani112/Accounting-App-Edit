frappe.ui.form.on('Item', {
  is_service: function(frm) {
    toggle_fields(frm);
  },
  refresh: function(frm) {
    toggle_fields(frm);
  },
  onload: function(frm){
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

function toggle_fields(frm) {
  const is_service = frm.doc.is_service;

  frm.set_df_property('default_warehouse', 'hidden', is_service === 1);
  frm.set_df_property('valuation_rate', 'hidden', is_service === 1);
  frm.set_df_property('expense_account', 'hidden', is_service !== 1);
}
