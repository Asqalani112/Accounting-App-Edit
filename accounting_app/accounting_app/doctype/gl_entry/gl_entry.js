frappe.ui.form.on('GL Entry', {
  onload: function(frm) {
   frm.set_query('voucher_type', () => {
  return {
    filters: {
      name: ['in', ['Sales Invoice', 'Payment Entry', 'Journal Entry', 'Purchase Invoice']]
    }
  };
});

  }
});
