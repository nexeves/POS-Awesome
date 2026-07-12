<template>
  <v-row justify="center">
    <v-dialog
      v-model="customerDialog"
      max-width="600px"
      @click:outside="clear_customer"
    >
      <v-card>
        <v-card-title>
          <span v-if="customer_id" class="headline primary--text">{{
            __('Update Customer')
          }}</span>
          <span v-else class="headline primary--text">{{
            __('Create Customer')
          }}</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>

            <!-- Mobile lookup banner -->
            <v-alert v-if="lookup_status === 'checking'" type="info" dense text class="mb-2">
              <v-progress-circular indeterminate size="14" width="2" class="mr-2"></v-progress-circular>
              {{ __('Checking mobile number...') }}
            </v-alert>
            <v-alert v-if="lookup_status === 'exists'" type="warning" dense text class="mb-2">
              {{ __('Customer already exists in ERPNext with this mobile. They have been selected.') }}
            </v-alert>
            <v-alert v-if="lookup_status === 'created'" type="success" dense text class="mb-2">
              {{ __('Customer found in Profit One and created in ERPNext!') }}
              <span v-if="lookup_points"> ({{ lookup_points }} loyalty points synced)</span>
            </v-alert>
            <v-alert v-if="lookup_status === 'not_found'" type="info" dense text class="mb-2">
              {{ __('No Profit One record found. Fill in details manually.') }}
            </v-alert>
            <v-alert v-if="lookup_status === 'error'" type="error" dense text class="mb-2">
              {{ __('Lookup error. Fill in details manually.') }}
            </v-alert>

            <v-row>
<<<<<<< HEAD
              <!-- Mobile first for lookup -->
=======
              <v-col cols="12">
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Customer Name') + ' *'"
                  background-color="white"
                  hide-details
                  v-model="customer_name"
                ></v-text-field>
              </v-col>
               <v-col cols="6" >
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Customer Invoice Name')"
                  background-color="white"
                  hide-details
                  v-model="custom_invoice_name"
                ></v-text-field>
              </v-col>
               <v-col cols="6" >
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Vat Number')"
                  background-color="white"
                  hide-details
                  v-model="custom_vat_no"
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-show="false">
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Tax ID')"
                  background-color="white"
                  hide-details
                  v-model="tax_id"
                ></v-text-field>
              </v-col>
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Mobile No')"
                  background-color="white"
                  hide-details
                  v-model="mobile_no"
                  :disabled="!!customer_id"
                  :loading="lookup_status === 'checking'"
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-show="false">
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Customer ID') + ' *'"
                  background-color="white"
                  hide-details
<<<<<<< HEAD
                  v-model="custom_customer_id"
=======
                  v-model="email_id"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-select
                  dense
                  label="Gender"
                  :items="genders"
                  v-model="gender"
                ></v-select>
              </v-col>
              <v-col cols="6" v-show="false">
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Referral Code')"
                  background-color="white"
                  hide-details
                  v-model="referral_code"
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-show="false">
                <v-menu
                  ref="birthday_menu"
                  v-model="birthday_menu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  dense
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="birthday"
                      :label="frappe._('Birthday')"
                      readonly
                      dense
                      clearable
                      hide-details
                      v-bind="attrs"
                      v-on="on"
                      color="primary"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="birthday"
                    color="primary"
                    no-title
                    scrollable
                    :max="frappe.datetime.now_date()"
                    @input="birthday_menu = false"
                  >
                  </v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  :label="frappe._('Customer Group') + ' *'"
                  v-model="group"
                  :items="groups"
                  background-color="white"
                  :no-data-text="__('Group not found')"
                  hide-details
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  :label="frappe._('Customer Name') + ' *'"
                  background-color="white"
                  hide-details
                  v-model="customer_name"
                  @input="customer_name = customer_name.toUpperCase()"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  :label="frappe._('Territory') + ' *'"
                  v-model="territory"
                  :items="territorys"
                  background-color="white"
                  :no-data-text="__('Territory not found')"
                  hide-details
                  required
                >
                </v-autocomplete>
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  :label="frappe._('Payment Term Template')"
                  v-model="payment_term"
                  :items="payment_terms"
                  background-color="white"
                  :no-data-text="__('Payment Term Template not found')"
                  hide-details
                ></v-autocomplete>
              </v-col>
              <v-col cols="6" v-if="loyalty_program">
                <v-text-field
                  v-model="loyalty_program"
                  :label="frappe._('Loyalty Program')"
                  dense
                  readonly
                  hide-details
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-if="loyalty_points">
                <v-text-field
                  v-model="loyalty_points"
                  :label="frappe._('Loyalty Points')"
                  dense
                  readonly
                  hide-details
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">{{
            __('Close')
          }}</v-btn>
          <v-btn color="success" dark @click="submit_dialog" :disabled="lookup_status === 'checking'">{{
            __('Submit')
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    customerDialog: false,
    pos_profile: '',
    customer_id: '',
    custom_customer_id: '',
    customer_name: '',
<<<<<<< HEAD
=======
    custom_invoice_name: '',
    custom_vat_no: '',
    tax_id: '',
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
    mobile_no: '',
    referral_code: '',
    birthday: null,
    birthday_menu: false,
    group: '',
    groups: [],
    territory: '',
    territorys: [],
    genders: [],
    customer_type: 'Individual',
    gender: '',
    loyalty_points: null,
    loyalty_program: null,
<<<<<<< HEAD
    custom_location: '',
    // lookup state
    lookup_status: '',   // 'checking' | 'exists' | 'created' | 'not_found' | 'error' | ''
    lookup_points: 0,
    _mobile_timer: null,
=======
    payment_term: '', 
    payment_terms: [],
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
  }),
  watch: {
    mobile_no(val) {
      if (this.customer_id) return; // editing, not creating
      clearTimeout(this._mobile_timer);
      this.lookup_status = '';
      const mobile = (val || '').trim();
      if (mobile.length < 8) return; // don't search until meaningful length
      this._mobile_timer = setTimeout(() => {
        this.do_mobile_lookup(mobile);
      }, 600);
    },
  },
  methods: {
    do_mobile_lookup(mobile) {
      const vm = this;
      vm.lookup_status = 'checking';
      frappe.call({
        method: 'espanshe_erp.espanshe_erp.profit_one.lookup_customer_by_mobile',
        args: { mobile_no: mobile },
        callback(r) {
          if (!r.message) { vm.lookup_status = 'error'; return; }
          const res = r.message;

          if (res.status === 'exists_in_erp') {
            vm.lookup_status = 'exists';
            const c = res.customer;
            // Auto-select the existing customer and close the dialog
            evntBus.$emit('add_customer_to_list', {
              name: c.name,
              customer_name: c.customer_name,
              mobile_no: c.mobile_no || mobile,
            });
            evntBus.$emit('set_customer', c.name);
            evntBus.$emit('fetch_customer_details');
            setTimeout(() => vm.close_dialog(), 1200);

          } else if (res.status === 'created') {
            vm.lookup_status = 'created';
            vm.lookup_points = res.points || 0;
            const c = res.customer;
            // Auto-fill the form fields from Profit One data
            vm.customer_name = c.customer_name;
            vm.custom_customer_id = c.name;
            evntBus.$emit('add_customer_to_list', {
              name: c.name,
              customer_name: c.customer_name,
              mobile_no: mobile,
            });
            evntBus.$emit('set_customer', c.name);
            evntBus.$emit('fetch_customer_details');
            setTimeout(() => vm.close_dialog(), 1500);

          } else if (res.status === 'not_found') {
            vm.lookup_status = 'not_found';

          } else {
            vm.lookup_status = 'error';
          }
        },
        error() { vm.lookup_status = 'error'; },
      });
    },

    close_dialog() {
      this.customerDialog = false;
      this.clear_customer();
    },
    clear_customer() {
      this.customer_name = '';
<<<<<<< HEAD
=======
      this.custom_invoice_name = '';
      this.custom_vat_no = '';
      this.tax_id = '';
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
      this.mobile_no = '';
      this.referral_code = '';
      this.birthday = '';
      this.group = frappe.defaults.get_user_default('Customer Group');
      this.territory = frappe.defaults.get_user_default('Territory');
      this.customer_id = '';
      this.custom_customer_id = '';
      this.customer_type = 'Individual';
      this.gender = '';
      this.loyalty_points = null;
      this.loyalty_program = null;
<<<<<<< HEAD
      this.custom_location = '';
      this.lookup_status = '';
      this.lookup_points = 0;
=======
      this.payment_term = '';
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
    },
    getCustomerGroups() {
      if (this.groups.length > 0) return;
      const vm = this;
      frappe.db
        .get_list('Customer Group', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 1000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => { vm.groups.push(el.name); });
          }
        });
    },
    getCustomerTerritorys() {
      if (this.territorys.length > 0) return;
      const vm = this;
      frappe.db
        .get_list('Territory', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 5000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => { vm.territorys.push(el.name); });
          }
        });
    },
    getGenders() {
      const vm = this;
      frappe.db
        .get_list('Gender', { fields: ['name'], page_length: 10 })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => { vm.genders.push(el.name); });
          }
        });
    },
    getPaymentTerms() {
      if (this.payment_terms.length > 0) return;
      frappe.db.get_list('Payment Terms Template', {
        fields: ['name'],
        limit: 1000,
        order_by: 'name',
      }).then((data) => {
        this.payment_terms = data.map((d) => d.name);
      });
    },
    submit_dialog() {
      if (!this.customer_name) {
        evntBus.$emit('show_mesage', { text: __('Customer name is required.'), color: 'error' });
        return;
      }
      if (!this.custom_customer_id) {
        evntBus.$emit('show_mesage', { text: __('Customer ID is required.'), color: 'error' });
        return;
      }
      if (!this.territory) {
        evntBus.$emit('show_mesage', { text: __('Customer territory is required.'), color: 'error' });
        return;
      }
      if (this.customer_name) {
        const vm = this;
        const args = {
          customer_id: this.customer_id || this.custom_customer_id,
          custom_customer_id: this.custom_customer_id,
          customer_name: this.customer_name,
          custom_invoice_name: this.custom_invoice_name,
          custom_vat_no: this.custom_vat_no,
          company: this.pos_profile.company,
          mobile_no: this.mobile_no,
          referral_code: this.referral_code,
          birthday: this.birthday,
          customer_group: this.group,
          territory: this.territory,
          customer_type: this.customer_type,
          gender: this.gender,
          payment_term: this.payment_term,
          method: this.customer_id ? 'update' : 'create',
          pos_profile_doc: this.pos_profile,
          custom_location: this.custom_location,
        };
        frappe.call({
          method: 'posawesome.posawesome.api.posapp.create_customer',
          args: args,
          callback: (r) => {
            if (!r.exc && r.message.name) {
              let text = __('Customer created successfully.');
              if (vm.customer_id) { text = __('Customer updated successfully.'); }
              evntBus.$emit('show_mesage', { text: text, color: 'success' });
              args.name = r.message.name;
              frappe.utils.play_sound('submit');
              evntBus.$emit('add_customer_to_list', args);
              evntBus.$emit('set_customer', r.message.name);
              evntBus.$emit('fetch_customer_details');
              this.close_dialog();
            } else {
              frappe.utils.play_sound('error');
              evntBus.$emit('show_mesage', { text: __('Customer creation failed.'), color: 'error' });
            }
          },
        });
        this.customerDialog = false;
      }
    },
  },
  created: function () {
    evntBus.$on('open_update_customer', (data) => {
      this.customerDialog = true;
      if (data) {
        this.customer_name = data.customer_name;
        this.custom_invoice_name = data.custom_invoice_name;
        this.custom_vat_no = data.custom_vat_no;
        this.customer_id = data.name;
        this.custom_customer_id = data.name;
        this.mobile_no = data.mobile_no;
        this.referral_code = data.referral_code;
        this.birthday = data.birthday;
        this.group = data.customer_group;
        this.territory = data.territory;
        this.loyalty_points = data.loyalty_points;
        this.loyalty_program = data.loyalty_program;
        this.gender = data.gender;
<<<<<<< HEAD
        this.custom_location = data.custom_location;
=======
        this.payment_term = data.payment_term || '';
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
      }
    });
    evntBus.$on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    evntBus.$on('payments_register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    this.getCustomerGroups();
    this.getCustomerTerritorys();
    this.getGenders();
<<<<<<< HEAD
=======
    this.getPaymentTerms();
    // set default values for customer group and territory from user defaults
>>>>>>> c9645153da8e31666946642005ff371a30bb1f79
    this.group = frappe.defaults.get_user_default('Customer Group');
    this.territory = frappe.defaults.get_user_default('Territory');
  },
};
</script>
