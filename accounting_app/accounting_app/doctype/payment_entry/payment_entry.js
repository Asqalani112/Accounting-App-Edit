frappe.ui.form.on('Payment Entry', {
  onload: function(frm) {
    frm.set_query("party", function() {
      return {
        filters: {
          party_type: frm.doc.party_type
        }
      };
    });
  }
});
