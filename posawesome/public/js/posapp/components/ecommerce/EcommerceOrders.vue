<template>
  <div fluid>
    <v-row>
      <v-col cols="12" class="pb-2">
        <v-card
          class="main mx-auto grey lighten-5 mt-3 p-3 pb-16 overflow-y-auto"
          style="max-height: 94vh; height: 94vh"
        >
          <v-row align="center" class="px-2 pt-2">
            <v-col md="4" cols="12">
              <p class="mb-0">
                <strong class="primary--text">{{ __("Online Orders") }}</strong>
                <span v-if="pending_count" class="error--text ml-2">
                  {{ __("- {0} awaiting invoice", [pending_count]) }}
                </span>
              </p>
            </v-col>
            <v-col md="4" cols="12">
              <v-btn-toggle
                v-model="billing_filter"
                mandatory
                dense
                color="primary"
                @change="get_orders"
              >
                <v-btn small value="Pending">{{ __("Pending") }}</v-btn>
                <v-btn small value="Converted">{{ __("Converted") }}</v-btn>
                <v-btn small value="All">{{ __("All") }}</v-btn>
              </v-btn-toggle>
            </v-col>
            <v-col md="4" cols="12" class="d-flex">
              <v-text-field
                color="primary"
                :label="frappe._('Order ID or Customer')"
                background-color="white"
                hide-details
                v-model="search"
                dense
                clearable
                @keyup.enter="get_orders"
              ></v-text-field>
              <v-btn text color="primary" class="ml-2" @click="get_orders">
                <v-icon small class="mr-1">mdi-refresh</v-icon>
                {{ __("Refresh") }}
              </v-btn>
            </v-col>
          </v-row>

          <v-divider class="my-2"></v-divider>

          <v-data-table
            :headers="headers"
            :items="orders"
            item-key="name"
            class="elevation-1"
            :loading="loading"
            :items-per-page="20"
            :footer-props="{ 'items-per-page-options': [20, 50, 100, -1] }"
          >
            <template v-slot:item.transaction_date="{ item }">
              {{ item.transaction_date }}
            </template>

            <template v-slot:item.grand_total="{ item }">
              {{ currencySymbol(item.currency) }}
              {{ formtCurrency(item.grand_total) }}
            </template>

            <template v-slot:item.ecommerce_status="{ item }">
              <v-chip
                small
                label
                dark
                :color="status_color(item.ecommerce_status)"
              >
                {{ item.ecommerce_status }}
              </v-chip>
            </template>

            <template v-slot:item.billing_status="{ item }">
              <v-chip small label dark :color="billing_color(item)">
                {{ billing_label(item) }}
                <span v-if="is_partly_billed(item)" class="ml-1">
                  {{ billed_pct(item) }}%
                </span>
              </v-chip>
            </template>

            <template v-slot:item.invoices="{ item }">
              <span v-if="!item.invoices || !item.invoices.length">-</span>
              <v-chip
                v-for="invoice in item.invoices"
                :key="invoice"
                x-small
                outlined
                color="primary"
                class="mr-1"
                @click="open_invoice(invoice)"
              >
                {{ invoice }}
              </v-chip>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-btn
                v-if="!is_fully_billed(item)"
                small
                color="success"
                dark
                :loading="loading_order === item.name"
                @click="load_to_pos(item)"
              >
                <v-icon small class="mr-1">mdi-cart-arrow-down</v-icon>
                {{ __("Load to POS") }}
              </v-btn>
              <v-icon v-else color="success">mdi-check-circle</v-icon>
            </template>

            <template v-slot:no-data>
              <div class="pa-4 text-center grey--text">
                {{ __("No orders to show") }}
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { evntBus } from "../../bus";
import { posStore } from "../../store";
import format from "../../format";

export default {
  mixins: [format],
  data: () => ({
    pos_profile: {},
    pos_opening_shift: {},
    orders: [],
    loading: false,
    loading_order: null,
    pending_count: 0,
    billing_filter: "Pending",
    search: "",
    headers: [
      { text: __("Order"), value: "name", align: "start", sortable: true },
      {
        text: __("Date"),
        value: "transaction_date",
        align: "start",
        sortable: true,
      },
      {
        text: __("Customer"),
        value: "customer_name",
        align: "start",
        sortable: true,
      },
      {
        text: __("Phone"),
        value: "contact_phone",
        align: "start",
        sortable: false,
      },
      {
        text: __("Amount"),
        value: "grand_total",
        align: "end",
        sortable: true,
      },
      {
        text: __("Status"),
        value: "ecommerce_status",
        align: "center",
        sortable: true,
      },
      {
        text: __("Billing"),
        value: "billing_status",
        align: "center",
        sortable: true,
      },
      {
        text: __("Invoice"),
        value: "invoices",
        align: "start",
        sortable: false,
      },
      { text: "", value: "actions", align: "end", sortable: false },
    ],
  }),

  methods: {
    status_color(status) {
      return (
        {
          "Order Placed": "info",
          Processing: "warning",
          "Out for Delivery": "primary",
          Completed: "success",
          Cancelled: "error",
        }[status] || "grey"
      );
    },

    // Billing display derives from per_billed, not from the stored
    // billing_status, which lags behind and is stale on existing data. Keeping
    // the whole column on one source of truth stops the list from offering
    // "Load to POS" on an order the server will then refuse as fully invoiced.
    is_fully_billed(item) {
      return flt(item.per_billed) >= 100;
    },

    is_partly_billed(item) {
      return flt(item.per_billed) > 0 && flt(item.per_billed) < 100;
    },

    billing_label(item) {
      if (item.billing_status === "Closed") return __("Closed");
      if (this.is_fully_billed(item)) return __("Fully Billed");
      if (this.is_partly_billed(item)) return __("Partly Billed");
      return __("Not Billed");
    },

    billing_color(item) {
      if (item.billing_status === "Closed") return "grey";
      if (this.is_fully_billed(item)) return "success";
      if (this.is_partly_billed(item)) return "warning";
      return "error";
    },

    billed_pct(item) {
      // format.js clamps a 0 precision back to 2 (`precision || 2`), so round
      // here rather than going through formtFloat.
      return Math.round(flt(item.per_billed));
    },

    open_invoice(name) {
      window.open("/app/sales-invoice/" + encodeURIComponent(name), "_blank");
    },

    get_orders() {
      if (!this.pos_profile.name) return;
      this.loading = true;
      frappe.call({
        method:
          "posawesome.posawesome.api.ecommerce_orders.get_ecommerce_orders",
        args: {
          pos_profile: JSON.stringify(this.pos_profile),
          billing_filter: this.billing_filter,
          search: this.search || null,
        },
        callback: (r) => {
          this.loading = false;
          this.orders = r.message || [];
          if (this.billing_filter === "Pending") {
            this.pending_count = this.orders.length;
          } else {
            this.get_pending_count();
          }
        },
        error: () => {
          this.loading = false;
        },
      });
    },

    get_pending_count() {
      frappe.call({
        method:
          "posawesome.posawesome.api.ecommerce_orders.get_ecommerce_orders_count",
        args: { pos_profile: JSON.stringify(this.pos_profile) },
        callback: (r) => {
          this.pending_count = r.message || 0;
        },
      });
    },

    load_to_pos(order) {
      this.loading_order = order.name;
      frappe.call({
        method: "posawesome.posawesome.api.ecommerce_orders.get_ecommerce_order",
        args: { ecommerce_sales_order: order.name },
        callback: (r) => {
          this.loading_order = null;
          if (!r.message) {
            evntBus.$emit("show_mesage", {
              text: __("Could not load order {0}", [order.name]),
              color: "error",
            });
            return;
          }
          // Tell the customer's app someone is on it. Fire and forget — a
          // failure here must not block the cashier from billing.
          frappe.call({
            method:
              "posawesome.posawesome.api.ecommerce_orders.mark_ecommerce_order_processing",
            args: { ecommerce_sales_order: order.name },
          });
          // Park the order for Invoice.vue, then switch pages. Invoice.vue is
          // not mounted yet, so this cannot go over the event bus.
          posStore.pending_ecommerce_order = r.message;
          evntBus.$emit("change_page", "POS");
        },
        error: () => {
          this.loading_order = null;
        },
      });
    },

    on_new_ecommerce_order() {
      this.get_orders();
    },

    check_opening_entry() {
      return frappe
        .call("posawesome.posawesome.api.posapp.check_opening_shift", {
          user: frappe.session.user,
        })
        .then((r) => {
          if (r.message) {
            this.pos_profile = r.message.pos_profile;
            this.pos_opening_shift = r.message.pos_opening_shift;
            evntBus.$emit("set_company", r.message.company);
            this.get_orders();
          }
        });
    },
  },

  mounted: function () {
    this.$nextTick(function () {
      // check_opening_entry is self-sufficient: register_pos_profile has
      // already fired by the time this page mounts, so listening for it would
      // never resolve anyway.
      this.check_opening_entry();
      // Navbar owns the realtime subscription; it re-broadcasts so an open
      // list refreshes itself instead of going stale behind the badge.
      // Keep the handler reference — $off(event) with no handler would strip
      // every other component's listener for the same event.
      evntBus.$on("new_ecommerce_order", this.on_new_ecommerce_order);
    });
  },

  beforeDestroy() {
    evntBus.$off("new_ecommerce_order", this.on_new_ecommerce_order);
  },
};
</script>
