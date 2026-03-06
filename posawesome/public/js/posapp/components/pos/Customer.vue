<template>
  <div>
    <v-autocomplete
      dense
      clearable
      auto-select-first
      outlined
      color="primary"
      :label="frappe._('Customer')"
      v-model="customer"
      :items="customers"
      item-text="customer_name"
      item-value="name"
      background-color="white"
      :no-data-text="searching ? __('Searching...') : __('No customer found')"
      hide-details
      no-filter
      :disabled="readonly"
      append-icon="mdi-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer"
      :search-input.sync="search_input"
      :loading="searching"
    >
      <template v-slot:item="data">
        <template>
          <v-list-item-content>
            <v-list-item-title
              class="primary--text subtitle-1"
              v-html="data.item.customer_name"
            ></v-list-item-title>
            <v-list-item-subtitle
              v-if="data.item.customer_name != data.item.name"
              v-html="`ID: ${data.item.name}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.tax_id"
              v-html="`TAX ID: ${data.item.tax_id}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.email_id"
              v-html="`Email: ${data.item.email_id}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.mobile_no"
              v-html="`Mobile No: ${data.item.mobile_no}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="data.item.primary_address"
              v-html="`Primary Address: ${data.item.primary_address}`"
            ></v-list-item-subtitle>
          </v-list-item-content>
        </template>
      </template>
    </v-autocomplete>
    <div class="mb-8">
      <UpdateCustomer></UpdateCustomer>
    </div>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import UpdateCustomer from './UpdateCustomer.vue';
export default {
  data: () => ({
    pos_profile: '',
    customers: [],
    customer: '',
    readonly: false,
    customer_info: {},
    search_input: '',
    searching: false,
    _search_timer: null,
    _last_search: null,
  }),

  components: {
    UpdateCustomer,
  },

  methods: {
    fetch_customers(txt) {
      const vm = this;
      if (txt === vm._last_search) return;
      vm._last_search = txt;
      vm.searching = true;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.search_customers_pos',
        args: { txt: txt || '' },
        callback(r) {
          vm.searching = false;
          if (r.message) {
            const current = vm.customers.find(c => c.name === vm.customer);
            const results = r.message;
            if (current && !results.find(c => c.name === current.name)) {
              results.unshift(current);
            }
            vm.customers = results;
          }
        },
        error() {
          vm.searching = false;
        },
      });
    },
    new_customer() {
      evntBus.$emit('open_update_customer', null);
    },
    edit_customer() {
      evntBus.$emit('open_update_customer', this.customer_info);
    },
  },

  computed: {},

  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.fetch_customers('');
      });
      evntBus.$on('payments_register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.fetch_customers('');
      });
      evntBus.$on('set_customer', (customer) => {
        this.customer = customer;
      });
      evntBus.$on('add_customer_to_list', (customer) => {
        if (!this.customers.find(c => c.name === customer.name)) {
          this.customers.unshift(customer);
        }
      });
      evntBus.$on('set_customer_readonly', (value) => {
        this.readonly = value;
      });
      evntBus.$on('set_customer_info_to_edit', (data) => {
        this.customer_info = data;
      });
      evntBus.$on('fetch_customer_details', () => {
        this.fetch_customers(this.search_input || '');
      });
    });
  },

  watch: {
    customer() {
      evntBus.$emit('update_customer', this.customer);
    },
    search_input(val) {
      if (val === this.customer_info?.customer_name) return;
      clearTimeout(this._search_timer);
      this._search_timer = setTimeout(() => {
        this.fetch_customers(val || '');
      }, 300);
    },
  },
};
</script>
