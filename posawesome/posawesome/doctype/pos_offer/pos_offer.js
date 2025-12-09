// Copyright (c) 2021, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Offer', {
	setup: function (frm) {
		set_filters(frm);
		controllers(frm);
	},
	refresh: function (frm) {
		controllers(frm);
	},
	onload: function (frm) {
		set_filters(frm);
		controllers(frm);
	},
	validate: function (frm) {
		if (frm.doc.apply_on === 'Transaction') {
			if (!frm.doc.min_amt > 0) {
				frappe.throw("Min Amount most be more then zero");
			}
		}
		if (frm.doc.offer === 'Give Product') {
			if (!frm.doc.given_qty > 0) {
				frappe.throw("Given Quantity most be more then zero");
			}
		}
		if (frm.doc.offer === 'Loyalty Point') {
			if (!frm.doc.loyalty_points > 0) {
				frappe.throw("Loyalty Points most be more then zero");
			}
		}
		if (frm.doc.apply_type === 'Item Group' && frm.doc.offer === 'Give Product' && !frm.doc.replace_item && !frm.doc.replace_cheapest_item) {
			frm.set_value('auto', 0);
		}
	},
	apply_on: function (frm) {
		controllers(frm);
	},
	offer: function (frm) {
		controllers(frm);
	},
	apply_type: function (frm) {
		controllers(frm);
	},
	discount_type: function (frm) {
		controllers(frm);
	},
	replace_item: function (frm) {
		controllers(frm);
	},
	replace_cheapest_item: function (frm) {
		controllers(frm);
	},
});


const controllers = (frm) => {
	frm.toggle_display('item', frm.doc.apply_on === 'Item Code');
	frm.toggle_reqd('item', frm.doc.apply_on === 'Item Code');

	frm.toggle_display('item_group', frm.doc.apply_on === 'Item Group');
	frm.toggle_reqd('item_group', frm.doc.apply_on === 'Item Group');

	frm.toggle_display('custom_from_itemcode', frm.doc.apply_on === 'Item Group');
	frm.toggle_reqd('custom_from_itemcode', frm.doc.apply_on === 'Item Group');

	frm.toggle_display('custom_to_itemcode', frm.doc.apply_on === 'Item Group');
	frm.toggle_reqd('custom_to_itemcode', frm.doc.apply_on === 'Item Group');

	frm.toggle_display('custom_items', frm.doc.apply_on === 'Item Group');
	frm.toggle_reqd('custom_items', frm.doc.apply_on === 'Item Group');	

	frm.toggle_display('get_items', frm.doc.apply_on === 'Item Group');

	frm.toggle_display('brand', frm.doc.apply_on === 'Brand');
	frm.toggle_reqd('brand', frm.doc.apply_on === 'Brand');

	frm.toggle_reqd('min_amt', frm.doc.apply_on === 'Transaction');

	frm.toggle_display('apply_for_section', frm.doc.offer === 'Give Product');
	frm.toggle_reqd('apply_type', frm.doc.offer === 'Give Product');

	frm.toggle_display('replace_item', frm.doc.apply_on === 'Item Code' && frm.doc.offer === 'Give Product' && frm.doc.apply_type === 'Item Code');
	frm.toggle_display('replace_cheapest_item', frm.doc.apply_on === 'Item Group' && frm.doc.offer === 'Give Product' && frm.doc.apply_type === 'Item Group');

	frm.toggle_display('apply_item_code', frm.doc.apply_type === 'Item Code' && !frm.doc.replace_item);
	frm.toggle_reqd('apply_item_code', frm.doc.apply_type === 'Item Code' && !frm.doc.replace_item);

	frm.toggle_display('apply_item_group', frm.doc.apply_type === 'Item Group' && !frm.doc.replace_cheapest_item);
	frm.toggle_reqd('apply_item_group', frm.doc.apply_type === 'Item Group' && !frm.doc.replace_cheapest_item);

	frm.toggle_display('less_then', frm.doc.apply_type === 'Item Group' && !frm.doc.replace_cheapest_item);

	frm.toggle_display('product_discount_scheme_section', frm.doc.offer === 'Give Product');
	frm.toggle_display('given_qty', frm.doc.offer === 'Give Product');
	frm.toggle_reqd('given_qty', frm.doc.offer === 'Give Product');

	frm.toggle_display('price_discount_scheme_section', frm.doc.offer !== 'Loyalty Point');
	frm.toggle_display('discount_type', frm.doc.offer !== 'Loyalty Point');
	frm.toggle_reqd('discount_type', frm.doc.offer !== 'Loyalty Point');

	frm.toggle_display('rate', frm.doc.discount_type === 'Rate');
	frm.toggle_reqd('rate', frm.doc.discount_type === 'Rate');

	frm.toggle_display('discount_amount', frm.doc.discount_type === 'Discount Amount');
	frm.toggle_reqd('discount_amount', frm.doc.discount_type === 'Discount Amount');

	frm.toggle_display('discount_percentage', frm.doc.discount_type === 'Discount Percentage');
	frm.toggle_reqd('discount_percentage', frm.doc.discount_type === 'Discount Percentage');

	frm.toggle_display('loyalty_point_scheme_section', frm.doc.offer === 'Loyalty Point');
	frm.toggle_display('loyalty_program', frm.doc.offer === 'Loyalty Point');
	frm.toggle_reqd('loyalty_program', frm.doc.offer === 'Loyalty Point');

	frm.toggle_display('loyalty_points', frm.doc.offer === 'Loyalty Point');
	frm.toggle_reqd('loyalty_points', frm.doc.offer === 'Loyalty Point');

	if (frm.doc.offer === 'Grand Total') {
		frm.set_df_property('discount_type', 'options', ['Discount Percentage','Discount Amount']);
	} else {
		frm.set_df_property('discount_type', 'options', ['', 'Rate', 'Discount Percentage', 'Discount Amount']);
	}

	if (frm.doc.apply_on === 'Transaction') {
		frm.set_df_property('offer', 'options', ['', 'Give Product', 'Grand Total', 'Loyalty Point']);
	} else {
		frm.set_df_property('offer', 'options', ['', 'Item Price', 'Give Product', 'Grand Total', 'Loyalty Point']);
	}

	if (frm.doc.apply_type === 'Item Group' && frm.doc.offer === 'Give Product' && !frm.doc.replace_item && !frm.doc.replace_cheapest_item) {
		frm.set_value('auto', 0);
	}
	if (frm.doc.apply_on !== 'Item Code' || frm.doc.offer !== 'Give Product' || frm.doc.apply_type !== 'Item Code') {
		frm.set_value('replace_item', 0);
	}
	if (frm.doc.apply_on !== 'Item Group' || frm.doc.offer !== 'Give Product' || frm.doc.apply_type !== 'Item Group') {
		frm.set_value('replace_cheapest_item', 0);
	}




};
 frappe.ui.form.on('POS Offer', {
    get_items(frm) {
        show_items_in_range(frm);
    }
});


const set_filters = (frm) => {
	frm.set_query('pos_profile', function () {
		return {
			filters: {
				'company': frm.doc.company,
			}
		};
	});
	frm.set_query('warehouse', function () {
		return {
			filters: {
				'company': frm.doc.company,
				'is_group': 0,
			}
		};
	});
	frm.set_query('loyalty_program', function () {
		return {
			filters: {
				'company': frm.doc.company,
			}
		};
	});
	frm.set_query('item_group', function () {
		return {
			filters: {
				'is_group': 0,
			}
		};
	});
	frm.set_query('apply_item_group', function () {
		return {
			filters: {
				'is_group': 0,
			}
		};
	});
	frm.set_query("custom_from_itemcode", function() {
    	return {
    	    query: "erpnext.controllers.queries.item_query",
    	    filters: {
    	        item_group: frm.doc.item_group
    	    }
    	};
	});
	frm.set_query("custom_to_itemcode", function() {
    	return {
    	    query: "erpnext.controllers.queries.item_query",
    	    filters: {
    	        item_group: frm.doc.item_group
    	    }
    	};
	});
};

function show_items_in_range(frm) {

    if (!frm.doc.item_group || !frm.doc.custom_from_itemcode || !frm.doc.custom_to_itemcode) {
        frappe.msgprint("Please select Item Group, From Item Code, and To Item Code.");
        return;
    }

    let from_code = cint(frm.doc.custom_from_itemcode);
    let to_code = cint(frm.doc.custom_to_itemcode);

    if (from_code > to_code) {
        frappe.msgprint("From Item Code cannot be greater than To Item Code.");
        return;
    }

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Item",
            fields: ["name", "item_group", "item_code","item_name"],
            filters: {
                item_group: frm.doc.item_group
            },
            limit_page_length: 2000
        },
        callback: function(r) {

            frm.clear_table("custom_items");

            (r.message || []).forEach(item => {
                let code = cint(item.item_code);

                if (code >= from_code && code <= to_code) {
                    let row = frm.add_child("custom_items");
                    row.item_code = item.item_code;
                    row.item_group = item.item_group;
					row.item_name = item.item_name;
                }
            });

            frm.refresh_field("custom_items");

            frappe.msgprint("Items loaded successfully.");
        }
    });
}