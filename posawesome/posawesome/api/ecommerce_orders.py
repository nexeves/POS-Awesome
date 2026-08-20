# -*- coding: utf-8 -*-
# Copyright (c) 2026, Al Rasam and contributors
# For license information, please see license.txt
"""POS-facing API for Ecommerce Sales Orders.

Orders placed from the Al Rasam storefront land as `Ecommerce Sales Order`
documents (the `alrasam` app). This module lets a cashier see the ones that
belong to their branch, tell at a glance which are already invoiced, and pull
one into the POS cart so payment is collected through the normal Payments
screen — producing a submitted Sales Invoice that is linked back to the order
and counted in the open shift.

The `alrasam` app is an optional peer: every entry point degrades to an empty
result when the Ecommerce Sales Order doctype is not installed, and the mapper
is imported lazily inside the one function that needs it.
"""

from __future__ import unicode_literals

import json

import frappe
from frappe import _

ESO_DOCTYPE = "Ecommerce Sales Order"

# An order closed by staff is not work waiting for a cashier, whatever its
# billed percentage says.
CLOSED_BILLING_STATUS = "Closed"

LIST_FIELDS = [
    "name",
    "customer",
    "customer_name",
    "contact_phone",
    "transaction_date",
    "delivery_date",
    "grand_total",
    "currency",
    "ecommerce_status",
    "billing_status",
    "per_billed",
    "per_delivered",
    "set_warehouse",
    "company",
    "creation",
]


def _ecommerce_installed():
    return bool(frappe.db.exists("DocType", ESO_DOCTYPE))


def _parse_profile(pos_profile):
    """POS Profile arrives as a JSON string of the whole doc — the convention
    already used by get_items / get_customer_names in api/posapp.py."""
    if isinstance(pos_profile, str):
        return json.loads(pos_profile)
    return pos_profile or {}


def _scope_filters(profile):
    """Restrict to submitted, non-cancelled orders for this terminal's branch.

    `set_warehouse` is stamped by the storefront's `place_order` from the store
    the customer picked, so it is the branch key. A profile without a warehouse
    sees every order for its company.
    """
    filters = {
        "docstatus": 1,
        "company": profile.get("company"),
        "ecommerce_status": ["!=", "Cancelled"],
    }
    if profile.get("warehouse"):
        filters["set_warehouse"] = profile.get("warehouse")
    return filters


def _apply_billing_filter(filters, billing_filter):
    """Split on `per_billed`, not on the stored `billing_status`.

    `billing_status` is only rewritten when an invoice is submitted or
    cancelled and is demonstrably stale on existing data (orders sitting at
    "Not Billed" with per_billed = 100 and a real invoice against them).
    `per_billed` is recomputed from the invoice lines, so it is the honest
    answer — and using it here keeps the list in step with the guard in
    create_sales_invoice_from_ecommerce_order, which would otherwise refuse an
    order the list had just advertised as pending.
    """
    if billing_filter == "Converted":
        filters["per_billed"] = [">=", 100]
    elif billing_filter == "All":
        pass
    else:
        filters["per_billed"] = ["<", 100]
        filters["billing_status"] = ["!=", CLOSED_BILLING_STATUS]
    return filters


def _attach_invoices(orders):
    """One extra query for the whole page, not one per row."""
    if not orders:
        return orders

    names = [o["name"] for o in orders]
    rows = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_ecommerce_sales_order": ["in", names],
            "docstatus": 1,
        },
        fields=["name", "custom_ecommerce_sales_order", "grand_total"],
        limit_page_length=0,
    )

    by_order = {}
    for row in rows:
        by_order.setdefault(row["custom_ecommerce_sales_order"], []).append(row["name"])

    for order in orders:
        order["invoices"] = by_order.get(order["name"], [])

    return orders


@frappe.whitelist()
def get_ecommerce_orders(pos_profile, billing_filter="Pending", search=None, limit=200):
    """List ecommerce orders for this terminal, newest first."""
    if not _ecommerce_installed():
        return []

    profile = _parse_profile(pos_profile)
    filters = _apply_billing_filter(_scope_filters(profile), billing_filter)

    or_filters = None
    if search:
        or_filters = {
            "name": ["like", "%{0}%".format(search)],
            "customer_name": ["like", "%{0}%".format(search)],
        }

    orders = frappe.get_all(
        ESO_DOCTYPE,
        filters=filters,
        or_filters=or_filters,
        fields=LIST_FIELDS,
        order_by="creation desc",
        limit_page_length=int(limit or 200),
    )

    return _attach_invoices(orders)


@frappe.whitelist()
def get_ecommerce_orders_count(pos_profile):
    """Authoritative badge number: orders for this terminal still to invoice."""
    if not _ecommerce_installed():
        return 0

    profile = _parse_profile(pos_profile)
    filters = _apply_billing_filter(_scope_filters(profile), "Pending")
    return frappe.db.count(ESO_DOCTYPE, filters)


@frappe.whitelist()
def get_ecommerce_order(ecommerce_sales_order):
    """Full order doc, for loading into the POS cart."""
    if not _ecommerce_installed():
        return None
    return frappe.get_doc(ESO_DOCTYPE, ecommerce_sales_order).as_dict()


@frappe.whitelist()
def mark_ecommerce_order_processing(ecommerce_sales_order):
    """Signal to the customer's app that a cashier has picked the order up.

    Only nudges "Order Placed" forward — `set_ecommerce_status` preserves a
    manually set "Processing" and computes everything past it from actual
    fulfillment, so this can never fight the controller.
    """
    if not _ecommerce_installed():
        return None

    doc = frappe.get_doc(ESO_DOCTYPE, ecommerce_sales_order)
    if doc.docstatus == 1 and doc.ecommerce_status == "Order Placed":
        doc.db_set("ecommerce_status", "Processing", update_modified=False)
    return doc.ecommerce_status
