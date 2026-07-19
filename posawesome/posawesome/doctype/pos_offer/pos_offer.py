# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class POSOffer(Document):
    def validate(self):
        self.validate_item_selection()

    def validate_item_selection(self):
        """Enforce the tables that back the "Item Selection" option.

        The POS Offer form hides/shows these tables, but form-side rules can be
        bypassed by API writes, so guard the invariants here too.
        """
        if self.apply_on == "Item Selection" and not self._rows_with_item_code(
            self.selection_items
        ):
            frappe.throw(
                _(
                    "Add at least one item to <b>Selection Items</b> when "
                    "Qualifying Transaction / Item is 'Item Selection'."
                )
            )

        if self.apply_type == "Item Selection" and not self._rows_with_item_code(
            self.give_items
        ):
            frappe.throw(
                _(
                    "Add at least one item to <b>Give Items</b> when "
                    "Apply Type is 'Item Selection'."
                )
            )

    @staticmethod
    def _rows_with_item_code(rows):
        return [row for row in (rows or []) if row.item_code]
