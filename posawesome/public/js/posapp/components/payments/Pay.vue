<template>
  <div fluid>
    <v-row>
      <!-- LEFT -->
      <v-col md="6" cols="12" class="pb-2 pr-0">
        <v-card
          class="main mx-auto grey lighten-5 mt-3 p-3 overflow-y-auto"
          style="max-height: 94vh"
        >
          <!-- CUSTOMER (WORKING NOW) -->
          <Customer />
          <v-divider />

          <v-row class="mt-2">
            <v-col cols="7">
              <strong>{{ __("Sales Orders") }}</strong>
            </v-col>
          </v-row>

          <!-- FILTERS -->
          <v-row align="center" no-gutters class="mb-2">
            <v-col md="4" cols="12">
              <v-select
                dense
                outlined
                hide-details
                clearable
                background-color="white"
                v-model="pos_profile_search"
                :items="pos_profiles_list"
                label="POS Profile"
              />
            </v-col>

            <v-col md="4" cols="12" class="pl-2">
              <v-text-field
                dense
                outlined
                hide-details
                clearable
                background-color="white"
                v-model="search_so"
                label="Search Sales Order"
              />
            </v-col>
          </v-row>

          <!-- SALES ORDER LIST -->
          <v-data-table
            :headers="headers"
            :items="sales_orders"
            item-key="name"
            :loading="loading"
            class="elevation-1"
            @click:row="open_so"
          >
            <template v-slot:item.grand_total="{ item }">
              {{ currencySymbol(item.currency) }}
              {{ formtCurrency(item.grand_total) }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>

      <!-- RIGHT -->
      <v-col md="6" cols="12">
        <v-card
          class="white mt-3 pa-4"
          style="max-height: 94vh; overflow-y: auto"
        >
          <template v-if="selected_so">
            <!-- HEADER -->
            <v-row>
              <v-col cols="6">
                <div class="label">{{ __("Sales Order") }}:</div>
                <div class="value">{{ selected_so.name }}</div>

                <div class="label mt-2">{{ __("Customer Name") }}:</div>
                <div class="value">{{ selected_so.customer_name }}</div>

                <div class="label mt-2">{{ __("Mobile No") }}:</div>
                <div class="value">{{ selected_so.mobile_no || "N/A" }}</div>
              </v-col>

              <v-col cols="6" class="text-right">
                <div class="label">{{ __("Order Date") }}:</div>
                <div class="value">{{ selected_so.posting_date }}</div>

                <div class="label mt-2">{{ __("Delivery Date") }}:</div>
                <div class="value">{{ selected_so.delivery_date || "-" }}</div>

                <div class="label mt-2">{{ __("Sales Person") }}:</div>
                <div class="value">{{ selected_so.sales_person || "-" }}</div>
              </v-col>
            </v-row>


            <v-divider class="my-3" />

            <!-- ITEMS -->
            <v-data-table
              dense
              hide-default-footer
              :headers="item_headers"
              :items="selected_so.items || []"
            >
              <template v-slot:item.rate="{ item }">
                {{ formtCurrency(item.rate) }}
              </template>
              <template v-slot:item.amount="{ item }">
                {{ formtCurrency(item.amount) }}
              </template>
            </v-data-table>

            <v-divider class="my-3" />

            <!-- TOTALS -->
            <v-row justify="end">
              <v-col cols="6" class="text-right">
                <div class="total-line">
                  {{ __("Amount before Discount") }}:
                  {{ formtCurrency(selected_so.amount_before_discount) }}
                </div>
                <div class="total-line">
                  {{ __("Total Discount Amount") }}:
                  {{ formtCurrency(selected_so.total_discount) }}
                </div>
                <div class="total-line">
                  {{ __("Amount Excl. VAT") }}:
                  {{ formtCurrency(selected_so.amount_excl_vat) }}
                </div>
                <div class="total-line">
                  {{ __("VAT Amount") }}:
                  {{ formtCurrency(selected_so.vat_amount) }}
                </div>
                <div class="grand-total">
                  {{ __("Grand Total") }}:
                  {{ formtCurrency(selected_so.grand_total) }}
                </div>
              </v-col>
            </v-row>

            <v-row justify="end" class="mt-4">
              <v-btn color="success" @click="submit_and_print">
                SUBMIT & PRINT
              </v-btn>
            </v-row>
          </template>

          <template v-else>
            <div class="text-center grey--text">
              {{ __("Click a Sales Order to view details") }}
            </div>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import Customer from "../pos/Customer.vue";
import { evntBus } from "../../bus";
import format from "../../format";
export default {
  mixins: [format],
  components: { Customer },

  data() {
    return {
      loading: false,
      company: "",
      pos_profile: null,

      customer: null,

      pos_profile_search: "",
      pos_profiles_list: [],

      search_so: "",
      all_sales_orders: [],
      sales_orders: [],

      selected_so: null,

      headers: [
        { text: __("Sales Order"), value: "name" },
        { text: __("Customer"), value: "customer_name" },
        { text: __("Date"), value: "posting_date" },
        { text: __("Amount"), value: "grand_total", align: "end" },
      ],

      item_headers: [
        { text: __("Item Code"), value: "item_code" },
        { text: __("Item Name"), value: "item_name" },
        { text: __("Qty"), value: "qty", align: "end" },
        { text: __("Rate"), value: "rate", align: "end" },
        { text: __("Amount"), value: "amount", align: "end" },
      ],
    };
  },

  watch: {
    search_so(val) {
      const s = (val || "").toLowerCase();
      this.sales_orders = this.all_sales_orders.filter(so =>
        so.name.toLowerCase().includes(s)
      );
    },

    pos_profile_search() {
      this.load_sales_orders();
    },
  },

  methods: {
    load_sales_orders() {
      if (!this.company || !this.pos_profile) return;

      this.loading = true;
      frappe.call(
        "posawesome.posawesome.api.payment_entry.get_sales_orders",
        {
          company: this.company,
          currency: this.pos_profile.currency,
          customer: this.customer,
          pos_profile_name: this.pos_profile_search,
        }
      ).then(r => {
        this.all_sales_orders = r.message || [];
        this.sales_orders = [...this.all_sales_orders];
        this.loading = false;
      });
    },

    open_so(row) {
      frappe.call({
        method: "posawesome.posawesome.api.payment_entry.get_sales_order_details",
        args: { sales_order_id: row.name },
        callback: r => {
          this.selected_so = r.message;
        },
      });
    },
    submit_and_print() {
      frappe.call({
        method: "posawesome.posawesome.api.payment_entry.make_si_from_so_with_advances",
        args: {
          sales_order: this.selected_so.name,
          pos_profile: this.pos_profile.name
        },
        callback: (r) => {
          if (!r.message) return;

          const si_name = r.message.sales_invoice;

          const print_format =
            this.pos_profile.print_format_for_online ||
            this.pos_profile.print_format;

          const letter_head = this.pos_profile.letter_head || 0;

          const url =
            frappe.urllib.get_base_url() +
            "/printview?doctype=Sales%20Invoice" +
            "&name=" + si_name +
            "&trigger_print=1" +
            "&format=" + encodeURIComponent(print_format) +
            "&no_letterhead=" + letter_head;

          const w = window.open(url, "Print-SI");

          w.addEventListener(
            "load",
            () => {
              w.print();

              // 🔥 REFRESH POSAWESOME AFTER PRINT
              setTimeout(() => {
                window.location.reload();
              }, 500);
            },
            true
          );
        }
      });
    },
    load_pos_profiles() {
      frappe.call(
        "posawesome.posawesome.api.payment_entry.get_available_pos_profiles",
        {
          company: this.company,
          currency: this.pos_profile.currency,
        }
      ).then(r => {
        this.pos_profiles_list = r.message || [];
      });
    },

    check_opening_entry() {
      frappe.call(
        "posawesome.posawesome.api.posapp.check_opening_shift",
        { user: frappe.session.user }
      ).then(r => {
        if (!r.message) return;

        this.pos_profile = r.message.pos_profile;
        this.company = r.message.company.name;

        /* 🔥 REQUIRED FOR CUSTOMER.vue */
        evntBus.$emit("set_company", r.message.company);
        evntBus.$emit("payments_register_pos_profile", r.message);

        this.pos_profile_search = this.pos_profile.name;

        this.load_pos_profiles();
        this.load_sales_orders();
      });
    },
  },

  mounted() {
    this.check_opening_entry();

    evntBus.$on("update_customer", customer => {
      this.customer = customer || null; // Customer ID
      this.load_sales_orders();
    });
  },

  beforeDestroy() {
    evntBus.$off("update_customer");
  },
};
</script>
<style>
.label {
  font-size: 13px;
  font-weight: 600;
  color: #555;
}
.value {
  font-size: 14px;
}
.total-line {
  font-size: 14px;
  margin-bottom: 4px;
}
.grand-total {
  font-size: 16px;
  font-weight: bold;
  color: #1976d2;
  margin-top: 6px;
}
</style>