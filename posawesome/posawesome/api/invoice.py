# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, add_days
import json
from posawesome.posawesome.doctype.pos_coupon.pos_coupon import update_coupon_code_count
from posawesome.posawesome.api.posapp import get_company_domain
from posawesome.posawesome.doctype.delivery_charges.delivery_charges import (
    get_applicable_delivery_charges,
)


def validate(doc, method):
    validate_shift(doc)
    set_patient(doc)
    auto_set_delivery_charges(doc)
    calc_delivery_charges(doc)


def before_submit(doc, method):
    update_coupon(doc, "used")


def before_cancel(doc, method):
    update_coupon(doc, "cancelled")


def before_submit(doc, method):
    # Update coupon usage count for each applied coupon
    try:
        posa_coupons = getattr(doc, "posa_coupons", []) or []
        for c in posa_coupons:
            coupon_name = c.get("coupon") if isinstance(c, dict) else getattr(c, "coupon", None)
            if coupon_name:
                try:
                    update_coupon_code_count(coupon_name, "used")
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(), "Error updating coupon count in before_submit")
    except Exception:
        pass  # Silently handle any coupon-related errors


@frappe.whitelist()
def create_draft_sales_order_from_cart(
    customer,
    company,
    items,
    delivery_date=None,
    pos_opening_shift=None,
    discount_amount=0,
    additional_discount_percentage=0,
    taxes=None,
    pos_profile=None,
    warehouse=None,
):
    """
    Creates a Draft Sales Order.
    Taxes will be added automatically by the before_save hook.
    """
    from frappe.utils import flt
    import json
    
    if isinstance(items, str):
        items_list = json.loads(items)
    else:
        items_list = items or []

    so = frappe.new_doc("Sales Order")
    so.update({
        "customer": customer,
        "company": company,
        "is_pos": 1,
        "pos_opening_shift": pos_opening_shift or None,
        "posa_pos_opening_shift": pos_opening_shift or None,
        "discount_amount": flt(discount_amount),
        "additional_discount_percentage": flt(additional_discount_percentage),
        "pos_profile": pos_profile or None,
    })

    # Add items to Sales Order
    for it in items_list:
        so.append("items", {
            "item_code": it.get("item_code"),
            "qty": flt(it.get("qty", 0)),
            "rate": flt(it.get("rate", 0)),
            "uom": it.get("uom"),
            "warehouse": it.get("warehouse") or warehouse,
            "discount_percentage": flt(it.get("discount_percentage", 0)),
            "discount_amount": flt(it.get("discount_amount", 0)),
            "item_tax_template": it.get("item_tax_template"),
            "delivery_date": it.get("posa_delivery_date") or delivery_date or None,
        })

    so.set_missing_values()
    
    # Don't add taxes here - let the before_save hook handle it
    # This ensures consistent tax handling across all SO saves

    so.flags.ignore_permissions = True
    so.flags.ignore_account_permission = True
    so.insert(ignore_permissions=True)  # insert() will trigger before_save hook

    return so.name

def update_coupon(doc, transaction_type):
    for coupon in doc.posa_coupons:
        if not coupon.applied:
            continue
        update_coupon_code_count(coupon.coupon, transaction_type)


def set_patient(doc):
    domain = get_company_domain(doc.company)
    if domain != "Healthcare":
        return
    patient_list = frappe.get_all(
        "Patient", filters={"customer": doc.customer}, page_length=1
    )
    if len(patient_list) > 0:
        doc.patient = patient_list[0].name


def auto_set_delivery_charges(doc):
    if not doc.pos_profile:
        return
    if not frappe.get_cached_value(
        "POS Profile", doc.pos_profile, "posa_auto_set_delivery_charges"
    ):
        return

    delivery_charges = get_applicable_delivery_charges(
        doc.company,
        doc.pos_profile,
        doc.customer,
        doc.shipping_address_name,
        doc.posa_delivery_charges,
        restrict=True,
    )

    if doc.posa_delivery_charges:
        if doc.posa_delivery_charges_rate:
            return
        else:
            if len(delivery_charges) > 0:
                doc.posa_delivery_charges_rate = delivery_charges[0].rate
    else:
        if len(delivery_charges) > 0:
            doc.posa_delivery_charges = delivery_charges[0].name
            doc.posa_delivery_charges_rate = delivery_charges[0].rate
        else:
            doc.posa_delivery_charges = None
            doc.posa_delivery_charges_rate = None


def calc_delivery_charges(doc):
    if not doc.pos_profile:
        return

    old_doc = None
    calculate_taxes_and_totals = False
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if not doc.posa_delivery_charges and not old_doc.posa_delivery_charges:
            return
    else:
        if not doc.posa_delivery_charges:
            return
    if not doc.posa_delivery_charges:
        doc.posa_delivery_charges_rate = 0

    charges_doc = None
    if doc.posa_delivery_charges:
        charges_doc = frappe.get_cached_doc(
            "Delivery Charges", doc.posa_delivery_charges
        )
        doc.posa_delivery_charges_rate = charges_doc.default_rate
        charges_profile = next(
            (i for i in charges_doc.profiles if i.pos_profile == doc.pos_profile), None
        )
        if charges_profile:
            doc.posa_delivery_charges_rate = charges_profile.rate

    if old_doc and old_doc.posa_delivery_charges:
        old_charges = next(
            (
                i
                for i in doc.taxes
                if i.charge_type == "Actual"
                and i.description == old_doc.posa_delivery_charges
            ),
            None,
        )
        if old_charges:
            doc.taxes.remove(old_charges)
            calculate_taxes_and_totals = True

    if doc.posa_delivery_charges:
        doc.append(
            "taxes",
            {
                "charge_type": "Actual",
                "description": doc.posa_delivery_charges,
                "tax_amount": doc.posa_delivery_charges_rate,
                "cost_center": charges_doc.cost_center,
                "account_head": charges_doc.shipping_account,
            },
        )
        calculate_taxes_and_totals = True

    if calculate_taxes_and_totals:
        doc.calculate_taxes_and_totals()


def validate_shift(doc):
    if doc.posa_pos_opening_shift and doc.pos_profile and doc.is_pos:
        # check if shift is open
        shift = frappe.get_cached_doc("POS Opening Shift", doc.posa_pos_opening_shift)
        if shift.status != "Open":
            frappe.throw(_("POS Shift {0} is not open").format(shift.name))
        # check if shift is for the same profile
        if shift.pos_profile != doc.pos_profile:
            frappe.throw(
                _("POS Opening Shift {0} is not for the same POS Profile").format(
                    shift.name
                )
            )
        # check if shift is for the same company
        if shift.company != doc.company:
            frappe.throw(
                _("POS Opening Shift {0} is not for the same company").format(
                    shift.name
                )
            )
