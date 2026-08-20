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
from frappe.utils import flt

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


def _delivered_by_delivery_note(order):
    """Has any submitted Delivery Note already moved stock for this order?

    Checked against Delivery Notes specifically rather than the order's
    `per_delivered`, because that percentage now also counts stock-moving
    invoices — which must not make a later invoice stop updating stock.
    """
    return bool(
        frappe.db.exists(
            "Delivery Note",
            {"custom_ecommerce_sales_order": order.name, "docstatus": 1},
        )
    )


@frappe.whitelist()
def create_sales_invoice_from_ecommerce_order(
    ecommerce_sales_order, pos_profile, pos_opening_shift
):
    """Draft a POS Sales Invoice from an Ecommerce Sales Order.

    The ESO -> Sales Invoice mapping itself already lives in the alrasam app
    (it sets the custom_ecommerce_sales_order links, the ecommerce income
    account and cost center, and skips already-billed lines). What that mapper
    cannot know is the POS context, so this fills in the gaps the plain
    `create_sales_invoice_from_order` leaves open: is_pos, pos_profile,
    posa_pos_opening_shift, naming_series, payments and posa_row_id.

    Goods are handed to the customer at the counter, so the invoice moves the
    stock itself (`update_stock = 1`); the POS flow never creates a Delivery
    Note. If one already exists from the desk, stock is left alone instead.
    """
    if not _ecommerce_installed():
        frappe.throw(_("Ecommerce Sales Order is not installed on this site"))

    from alrasam.alrasam_erp.doctype.ecommerce_sales_order.ecommerce_sales_order import (
        make_sales_invoice,
    )

    profile = _parse_profile(pos_profile)
    order = frappe.get_doc(ESO_DOCTYPE, ecommerce_sales_order)

    if order.docstatus != 1:
        frappe.throw(_("Order {0} is not submitted").format(order.name))

    # `billing_status` is a stored field and can lag behind reality (it is only
    # rewritten when a Sales Invoice is submitted or cancelled). `per_billed`
    # is recomputed from the invoice lines themselves, so trust it as well —
    # otherwise a stale "Not Billed" lets a fully billed order through to an
    # empty mapping and a bare MandatoryError.
    if order.billing_status == "Fully Billed" or flt(order.per_billed) >= 100:
        frappe.throw(_("Order {0} is already fully invoiced").format(order.name))

    invoice = make_sales_invoice(order.name, ignore_permissions=True)

    # The mapper drops lines that are already billed. If that leaves nothing,
    # say so plainly instead of letting the mandatory-items check surface.
    if not invoice.get("items"):
        frappe.throw(
            _("Order {0} has no lines left to invoice").format(order.name)
        )

    invoice.is_pos = 1
    invoice.pos_profile = profile.get("name")
    invoice.posa_pos_opening_shift = pos_opening_shift
    invoice.naming_series = profile.get("naming_series") or invoice.naming_series
    invoice.campaign = invoice.campaign or profile.get("campaign")
    invoice.ignore_pricing_rule = 1

    # Goods are handed over at the counter, so the invoice moves the stock
    # itself. The one exception is an order a Delivery Note already shipped —
    # deducting again would take the same units out of stock twice. The POS
    # flow never creates a Delivery Note, so this only guards against an order
    # that went out through the desk before reaching the till.
    invoice.update_stock = 0 if _delivered_by_delivery_note(order) else 1

    # The terminal's warehouse wins over the one carried by the order. The
    # invoice moves the stock itself, and the goods physically leave the branch
    # the cashier is standing in — not necessarily the branch the order was
    # placed against (an order left on the guest fallback warehouse being the
    # obvious case). Falls back to the order's own warehouse for a profile that
    # has none configured.
    if profile.get("warehouse"):
        invoice.set_warehouse = profile.get("warehouse")
    for item in invoice.items:
        if profile.get("warehouse"):
            item.warehouse = profile.get("warehouse")
        else:
            item.warehouse = item.warehouse or invoice.set_warehouse
        # The POS offers engine keys off posa_row_id. The cart generates one for
        # every line it builds, so a server-built line has to generate its own.
        if not item.get("posa_row_id"):
            item.posa_row_id = frappe.generate_hash(length=20)

    invoice.payments = []
    for row in profile.get("payments") or []:
        invoice.append(
            "payments",
            {
                "mode_of_payment": row.get("mode_of_payment"),
                "default": row.get("default"),
                "amount": 0,
            },
        )

    invoice.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice.save()

    return invoice
