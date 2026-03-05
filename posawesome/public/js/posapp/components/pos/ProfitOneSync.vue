<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title>
        <span class="headline">{{ __('Fetch Profit One Loyalty') }}</span>
      </v-card-title>

      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-autocomplete
                v-model="customer"
                :items="customer_list"
                :search-input.sync="customer_search"
                item-text="label"
                item-value="name"
                :label="__('Customer')"
                :placeholder="__('Search by ID, name or mobile')"
                return-object
                clearable
                no-filter
                @change="on_customer_change"
              >
                <template v-slot:item="data">
                  <v-list-item-content>
                    <v-list-item-title>{{ data.item.customer_name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ __('ID') }}: {{ data.item.name }}
                      <span v-if="data.item.mobile_no"> | {{ data.item.mobile_no }}</span>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </template>
                <template v-slot:selection="data">
                  {{ data.item.customer_name }} ({{ data.item.name }})
                </template>
              </v-autocomplete>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="card_no"
                :label="__('Profit One Card No')"
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v-card-actions>
        <v-btn color="secondary" text :loading="sync_all_loading" @click="sync_all">{{ __('Sync All Customers') }}</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="close">{{ __('Close') }}</v-btn>
        <v-btn color="primary" :loading="loading" :disabled="!customer || !card_no" @click="sync_now">{{ __('Sync Now') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { evntBus } from '../../bus';

export default {
  data() {
    return {
      dialog: false,
      customer: null,
      customer_list: [],
      customer_search: null,
      card_no: '',
      loading: false,
      sync_all_loading: false,
      _search_timeout: null,
    };
  },
  watch: {
    customer_search(val) {
      // Only search if the value changed and is not already the selected customer
      if (val && val !== (this.customer ? this.customer.customer_name : null)) {
        clearTimeout(this._search_timeout);
        this._search_timeout = setTimeout(() => {
          this.search_customers(val);
        }, 300);
      }
    },
  },
  created() {
    this.$nextTick(() => {
      evntBus.$on('open_loyalty_sync_dialog', () => {
        this.dialog = true;
        this.reset_form();
      });
    });
  },
  methods: {
    reset_form() {
      this.customer = null;
      this.card_no = '';
      this.customer_list = [];
      this.customer_search = null;
    },
    close() {
      this.dialog = false;
      this.reset_form();
    },
    search_customers(txt) {
      frappe.call({
        method: 'espanshe_erp.espanshe_erp.profit_one.search_customers_for_sync',
        args: { txt: txt },
        callback: (r) => {
          if (r.message) {
            // Add a computed label field for display (Vuetify needs item-text to be a real field)
            this.customer_list = r.message.map(c => ({
              ...c,
              label: `${c.customer_name} (${c.name})`,
            }));
          }
        },
      });
    },
    on_customer_change() {
      if (this.customer) {
        this.card_no = this.customer.name;
      }
    },
    sync_now() {
      if (!this.customer || !this.card_no) return;
      this.loading = true;

      frappe.call({
        method: 'espanshe_erp.espanshe_erp.profit_one.sync_loyalty_now',
        args: {
          customer: this.customer.name,
          card_no: this.card_no,
        },
        callback: (r) => {
          this.loading = false;
          if (!r.exc && r.message) {
            if (r.message.status === 'success') {
              evntBus.$emit('show_mesage', {
                text: `${this.__('Points Synced:')} ${r.message.points}`,
                color: 'success',
              });
              this.close();
            } else {
              evntBus.$emit('show_mesage', {
                text: this.__(r.message.message),
                color: 'error',
              });
            }
          } else {
            evntBus.$emit('show_mesage', {
              text: this.__('Error occurred during sync'),
              color: 'error',
            });
          }
        },
        error: () => {
          this.loading = false;
        }
      });
    },
    sync_all() {
      this.sync_all_loading = true;
      frappe.call({
        method: 'espanshe_erp.espanshe_erp.profit_one.trigger_daily_sync',
        callback: (r) => {
          this.sync_all_loading = false;
          if (!r.exc && r.message) {
            evntBus.$emit('show_mesage', {
              text: this.__(r.message.message),
              color: r.message.status === 'success' ? 'success' : 'error',
            });
            if (r.message.status === 'success') {
              this.close();
            }
          } else {
            evntBus.$emit('show_mesage', {
              text: this.__('Error starting sync'),
              color: 'error',
            });
          }
        },
        error: () => {
          this.sync_all_loading = false;
        }
      });
    },
  },
};
</script>

<style scoped>
</style>
