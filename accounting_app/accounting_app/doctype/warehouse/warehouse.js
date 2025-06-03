// Copyright (c) 2025, asqalani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse', {
	onload:function(frm){
	    frm.set_query('inventory_account', () =>{
	        return{
	            filters: {

	                account_type: 'Inventory',
                    is_group: 0

	            }
	        }

	})

	}
});
