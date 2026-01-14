<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-card class="rounded-lg">
      <v-card-title class="primary white--text headline" style="font-size: 1.25rem;">
        <v-icon left color="white">mdi-credit-card-plus</v-icon>
        <span class="font-weight-bold">{{ __('Create Advance Payment') }}</span>
        <v-spacer></v-spacer>
        <v-btn icon dark @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-card-text class="pt-6">
        <v-container>
          <v-row dense>
            <v-col cols="12">
              <v-autocomplete
                v-model="customer"
                :items="customers"
                item-text="customer_name"
                item-value="name"
                :label="__('Customer')"
                required
                outlined
                dense
                prepend-inner-icon="mdi-account"
                :loading="loadingCustomers"
                background-color="grey lighten-5"
              ></v-autocomplete>
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="mode_of_payment"
                :items="payment_methods"
                item-text="mode_of_payment"
                item-value="mode_of_payment"
                :label="__('Mode of Payment')"
                required
                outlined
                dense
                prepend-inner-icon="mdi-cash"
                background-color="grey lighten-5"
              ></v-select>
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="amount"
                :label="__('Amount')"
                type="number"
                required
                outlined
                dense
                prepend-inner-icon="mdi-currency"
                background-color="grey lighten-5"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      
      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn 
          color="grey darken-1" 
          text 
          class="text-capitalize"
          @click="close"
        >
          {{ __('Cancel') }}
        </v-btn>
        <v-btn
          color="primary"
          class="px-6 text-capitalize font-weight-bold"
          elevation="2"
          @click="submit"
          :loading="submitting"
        >
          {{ __('Submit') }}
          <v-icon right small>mdi-check</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      customer: null,
      customers: [],
      mode_of_payment: null,
      amount: 0,
      payment_methods: [],
      pos_profile: null,
      loadingCustomers: false,
      submitting: false,
    };
  },
  methods: {
    open(pos_profile) {
      this.pos_profile = pos_profile;
      this.dialog = true;
      this.fetchCustomers();
      this.fetchPaymentMethods();
    },
    close() {
      this.dialog = false;
      this.reset();
    },
    reset() {
      this.customer = null;
      this.mode_of_payment = null;
      this.amount = 0;
      this.customers = [];
      this.payment_methods = [];
    },
    fetchCustomers() {
      this.loadingCustomers = true;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_customer_names',
        args: {
          pos_profile: JSON.stringify(this.pos_profile),
        },
        callback: (r) => {
          this.customers = r.message || [];
          this.loadingCustomers = false;
        },
      });
    },
    fetchPaymentMethods() {
      if (this.pos_profile && this.pos_profile.payments) {
        this.payment_methods = this.pos_profile.payments;
      }
    },
    submit() {
      if (!this.customer || !this.mode_of_payment || !this.amount) {
        frappe.msgprint(__('Please fill all fields'));
        return;
      }
      this.submitting = true;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.create_advance_payment',
        args: {
          customer: this.customer,
          mode_of_payment: this.mode_of_payment,
          amount: this.amount,
          pos_profile: this.pos_profile.name,
        },
        callback: (r) => {
          this.submitting = false;
          if (!r.exc) {
            frappe.show_alert({
              message: __('Advance Payment Created'),
              indicator: 'green',
            });
            this.close();
          }
        },
      });
    },
  },
};
</script>
