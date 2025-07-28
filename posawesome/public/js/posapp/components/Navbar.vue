<!--<template>
  <nav>
    <v-app-bar app height="40" class="elevation-2">
      <v-app-bar-nav-icon
        @click.stop="drawer = !drawer"
        class="grey--text"
      ></v-app-bar-nav-icon>
      <v-img
        src="/assets/posawesome/js/posapp/components/pos/pos.png"
        alt="POS Awesome"
        max-width="32"
        class="mr-2"
        color="primary"
      ></v-img>
      <v-toolbar-title
        @click="go_desk"
        style="cursor: pointer"
        class="text-uppercase primary--text"
      >
        <span class="font-weight-light">pos</span>
        <span>awesome</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>
      <v-btn style="cursor: unset" text color="primary">
        <span right>{{ pos_profile.name }}</span>
      </v-btn>
      <div class="text-center">
        <v-menu offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn color="primary" dark text v-bind="attrs" v-on="on"
              >Menu</v-btn
            >
          </template>
          <v-card class="mx-auto" max-width="300" tile>
            <v-list dense>
              <v-list-item-group v-model="menu_item" color="primary">
                <v-list-item
                  @click="close_shift_dialog"
                  v-if="!pos_profile.posa_hide_closing_shift && item == 0"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-content-save-move-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{
                      __('Close Shift')
                    }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  @click="print_last_invoice"
                  v-if="
                    pos_profile.posa_allow_print_last_invoice &&
                    this.last_invoice
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-printer</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{
                      __('Print Last Invoice')
                    }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider class="my-0"></v-divider>
                <v-list-item @click="logOut">
                  <v-list-item-icon>
                    <v-icon>mdi-logout</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ __('Logout') }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item @click="go_about">
                  <v-list-item-icon>
                    <v-icon>mdi-information-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ __('About') }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-menu>
      </div>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant.sync="mini"
      app
      class="primary margen-top"
      width="170"
    >
      <v-list dark>
        <v-list-item class="px-2">
          <v-list-item-avatar>
            <v-img :src="company_img"></v-img>
          </v-list-item-avatar>

          <v-list-item-title>{{ company }}</v-list-item-title>

          <v-btn icon @click.stop="mini = !mini">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item-group v-model="item" color="white">
          <v-list-item
            v-for="item in items"
            :key="item.text"
            @click="changePage(item.text)"
          >
            <v-list-item-icon>
              <v-icon v-text="item.icon"></v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" top right>
      {{ snackText }}
    </v-snackbar>
    <v-dialog v-model="freeze" persistent max-width="290">
      <v-card>
        <v-card-title class="text-h5">
          {{ freezeTitle }}
        </v-card-title>
        <v-card-text>{{ freezeMsg }}</v-card-text>
      </v-card>
    </v-dialog>
  </nav>
</template>

<script>
import { evntBus } from '../bus';

export default {
  // components: {MyPopup},
  data() {
    return {
      drawer: false,
      mini: true,
      item: 0,
      items: [{ text: 'POS', icon: 'mdi-network-pos' }],
      page: '',
      fav: true,
      menu: false,
      message: false,
      hints: true,
      menu_item: 0,
      snack: false,
      snackColor: '',
      snackText: '',
      company: 'POS Awesome',
      company_img: '/assets/erpnext/images/erpnext-logo.svg',
      pos_profile: '',
      freeze: false,
      freezeTitle: '',
      freezeMsg: '',
      last_invoice: '',
    };
  },
  methods: {
    changePage(key) {
      this.$emit('changePage', key);
    },
    go_desk() {
      frappe.set_route('/');
      location.reload();
    },
    go_about() {
      const win = window.open(
        'https://github.com/yrestom/POS-Awesome',
        '_blank'
      );
      win.focus();
    },
    close_shift_dialog() {
      evntBus.$emit('open_closing_dialog');
    },
    show_mesage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
    },
    logOut() {
      var me = this;
      me.logged_out = true;
      return frappe.call({
        method: 'logout',
        callback: function (r) {
          if (r.exc) {
            return;
          }
          frappe.set_route('/login');
          location.reload();
        },
      });
    },
    print_last_invoice() {
      if (!this.last_invoice) return;
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=Sales%20Invoice&name=' +
        this.last_invoice +
        '&trigger_print=1' +
        '&format=' +
        print_format +
        '&no_letterhead=' +
        letter_head;
      const printWindow = window.open(url, 'Print');
      printWindow.addEventListener(
        'load',
        function () {
          printWindow.print();
        },
        true
      );
    },
  },
  created: function () {
    this.$nextTick(function () {
      evntBus.$on('show_mesage', (data) => {
        this.show_mesage(data);
      });
      evntBus.$on('set_company', (data) => {
        this.company = data.name;
        this.company_img = data.company_logo
          ? data.company_logo
          : this.company_img;
      });
      evntBus.$on('register_pos_profile', (data) => {
        this.pos_profile = data.pos_profile;
        const payments = { text: 'Payments', icon: 'mdi-cash-register' };
        if (
          this.pos_profile.posa_use_pos_awesome_payments &&
          this.items.length !== 2
        ) {
          this.items.push(payments);
        }
      });
      evntBus.$on('set_last_invoice', (data) => {
        this.last_invoice = data;
      });
      evntBus.$on('freeze', (data) => {
        this.freeze = true;
        this.freezeTitle = data.title;
        this.freezeMsg = data.msg;
      });
      evntBus.$on('unfreeze', () => {
        this.freeze = false;
        this.freezTitle = '';
        this.freezeMsg = '';
      });
    });
  },
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}
</style>
-->
<template>
  <nav>
    <v-app-bar app height="40" class="elevation-2">
      <v-app-bar-nav-icon
        @click.stop="drawer = !drawer"
        class="grey--text"
      ></v-app-bar-nav-icon>
      <v-img
        src="/assets/posawesome/js/posapp/components/pos/pos.png"
        alt="POS Awesome"
        max-width="32"
        class="mr-2"
        color="primary"
      ></v-img>
      <v-toolbar-title
        @click="go_desk"
        style="cursor: pointer"
        class="text-uppercase primary--text"
      >
        <span class="font-weight-light">pos</span>
        <span>awesome</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>
      <v-btn style="cursor: unset" text color="primary">
        <span right>{{ pos_profile.name }}</span>
      </v-btn>

      <v-btn color="primary" text @click="openCustomerDialog">
        Show Customer Invoices
      </v-btn>

      <div class="text-center">
        <v-menu offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn color="primary" dark text v-bind="attrs" v-on="on"
              >Menu</v-btn
            >
          </template>
          <v-card class="mx-auto" max-width="300" tile>
            <v-list dense>
              <v-list-item-group v-model="menu_item" color="primary">
                <v-list-item
                  @click="close_shift_dialog"
                  v-if="!pos_profile.posa_hide_closing_shift && item == 0"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-content-save-move-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{
                      __('Close Shift')
                    }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  @click="print_last_invoice"
                  v-if="
                    pos_profile.posa_allow_print_last_invoice &&
                    this.last_invoice
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-printer</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{
                      __('Print Last Invoice')
                    }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider class="my-0"></v-divider>
                <v-list-item @click="logOut">
                  <v-list-item-icon>
                    <v-icon>mdi-logout</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ __('Logout') }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item @click="go_about">
                  <v-list-item-icon>
                    <v-icon>mdi-information-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ __('About') }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-menu>
      </div>
    </v-app-bar>
    <!-- Customer Dialog -->
    <v-dialog v-model="customerDialog" max-width="800px">
      <v-card>
        <v-card-title class="sticky-top" style="z-index: 2; background: white;">
          Sales Invoices
        </v-card-title>

        <!-- Filter Field -->
        <div class="px-4 pt-2 sticky-top" style="z-index: 1; background: white;">
          <v-autocomplete
            v-model="selectedCustomer"
            :items="customerOptions"
            item-text="customer_name"
            item-value="name"
            label="Search Customer"
            dense
            outlined
            clearable
            return-object
            :filter="customFilter"
            @change="fetchCustomerInvoices"
          >
            <template v-slot:item="data">
              <v-list-item-content>
                <v-list-item-title>{{ data.item.customer_name }}</v-list-item-title>
                <v-list-item-subtitle>{{ data.item.mobile_no }}</v-list-item-subtitle>
              </v-list-item-content>
            </template>

            <template v-slot:selection="data">
              <span>
                {{ data.item.customer_name }} — {{ data.item.mobile_no }}
              </span>
            </template>
          </v-autocomplete>
        </div>

        <!-- Invoices -->
        <v-card-text class="pt-2" style="max-height: 400px; overflow-y: auto;">
          <v-divider class="my-2" />
          <v-expansion-panels v-if="visibleInvoices.length" accordion>
            <v-expansion-panel
              v-for="invoice in visibleInvoices"
              :key="invoice.name"
            >
              <v-expansion-panel-header>
                <div>
                  <strong>{{ invoice.name }}</strong> — OMR {{ invoice.grand_total }}
                  <div class="grey--text text--darken-1 text-caption">
                    {{ invoice.customer_name }} — {{ invoice.posting_date }}<br>
                    {{ invoice.sales_persons }}
                  </div>
                </div>
              </v-expansion-panel-header>

              <v-expansion-panel-content>
                <div v-if="invoice.items && invoice.items.length">
                  <v-simple-table dense>
                    <thead>
                      <tr>
                        <th class="text-left">Item Name</th>
                        <th class="text-left">Qty</th>
                        <th class="text-left">UOM</th>
                        <th class="text-left">Rate</th>
                        <th class="text-left">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(item, idx) in invoice.items" :key="idx">
                        <td>{{ item.item_name }}</td>
                        <td>{{ item.qty }}</td>
                        <td>{{ item.uom }}</td>
                        <td>{{ item.rate }}</td>
                        <td>{{ item.amount }}</td>
                      </tr>
                    </tbody>
                  </v-simple-table>
                </div>
                <div v-else class="grey--text text-caption">
                  No items found.
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- Load More Button -->
          <v-btn
            v-if="customerInvoices.length > displayCount"
            color="primary"
            block
            text
            @click="loadMore"
          >
            Load More
          </v-btn>

          <div v-else-if="!customerInvoices.length" class="grey--text">No invoices found.</div>
        </v-card-text>

        <!-- Close Button -->
        <v-card-actions class="sticky-bottom" style="z-index: 2; background: white;">
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="closeCustomerDialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

     <v-navigation-drawer
      v-model="drawer"
      :mini-variant.sync="mini"
      app
      class="primary margen-top"
      width="170"
    >
      <v-list>
        <v-list-item class="px-2">
          <v-list-item-avatar>
            <v-img :src="company_img"></v-img>
          </v-list-item-avatar>
          <v-list-item-title>{{ company }}</v-list-item-title>
          <v-btn icon @click.stop="mini = !mini">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </v-list-item>

        <v-list-item-group v-model="item" color="white">
          <v-list-item
            v-for="item in items"
            :key="item.text"
            @click="changePage(item.text)"
          >
            <v-list-item-icon>
              <v-icon v-text="item.icon"></v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" top right>
      {{ snackText }}
    </v-snackbar>

    <v-dialog v-model="freeze" persistent max-width="290">
      <v-card>
        <v-card-title class="text-h5">
          {{ freezeTitle }}
        </v-card-title>
        <v-card-text>{{ freezeMsg }}</v-card-text>
      </v-card>
    </v-dialog>

  </nav>
</template>

<script>
import { evntBus } from '../bus';

export default {
  data() {
    return {
      drawer: false,
      mini: true,
      item: 0,
      items: [{ text: 'POS', icon: 'mdi-network-pos' }],
      menu_item: 0,
      snack: false,
      snackColor: '',
      snackText: '',
      company: 'POS Awesome',
      company_img: '/assets/erpnext/images/erpnext-logo.svg',
      pos_profile: '',
      freeze: false,
      freezeTitle: '',
      freezeMsg: '',
      last_invoice: '',
      customerDialog: false,
      customerOptions: [],
      selectedCustomer: null,
      customerInvoices: [],
      displayCount: 10,
    };
  },
  computed: {
    visibleInvoices() {
      return this.customerInvoices.slice(0, this.displayCount);
    },
  },
  methods: {
    changePage(key) {
      this.$emit('changePage', key);
    },
    go_desk() {
      frappe.set_route('/');
      location.reload();
    },
    go_about() {
      window.open('https://github.com/yrestom/POS-Awesome', '_blank').focus();
    },
    close_shift_dialog() {
      evntBus.$emit('open_closing_dialog');
    },
    show_mesage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
    },
    logOut() {
      frappe.call({
        method: 'logout',
        callback: (r) => {
          if (!r.exc) {
            frappe.set_route('/login');
            location.reload();
          }
        },
      });
    },
    print_last_invoice() {
      if (!this.last_invoice) return;
      const format = this.pos_profile.print_format_for_online || this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        `/printview?doctype=Sales%20Invoice&name=${this.last_invoice}&trigger_print=1&format=${format}&no_letterhead=${letter_head}`;
      const printWindow = window.open(url, 'Print');
      printWindow.addEventListener('load', () => printWindow.print(), true);
    },
    openCustomerDialog() {
      this.customerDialog = true;
      this.displayCount = 10; 
      this.fetchCustomers();
      this.fetchCustomerInvoices();
    },
    fetchCustomers() {
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Customer',
          fields: ['name', 'customer_name', 'mobile_no'],
          limit_page_length: 100,
        },
        callback: (r) => {
          if (r.message) this.customerOptions = r.message;
        },
      });
    },
    fetchCustomerInvoices() {
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Sales Invoice',
          fields: ['name', 'posting_date', 'grand_total', 'customer'],
          filters: {
            pos_profile: this.pos_profile.name,
          },
          order_by: 'creation desc',
          limit_page_length: 50,
        },
        callback: (r) => {
          if (r.message) {
            const allInvoices = r.message;
            frappe.call({
              method: 'frappe.client.get_list',
              args: {
                doctype: 'Customer',
                fields: ['name', 'customer_name', 'mobile_no'],
                limit_page_length: 1000,
              },
              callback: async (res) => {
                const customerMap = {};
                res.message.forEach(cust => {
                  customerMap[cust.name] = cust;
                });
                this.customerOptions = res.message;

                const detailedInvoices = [];
                for (const inv of allInvoices) {
                  try {
                    const result = await frappe.call({
                      method: 'frappe.client.get',
                      args: { doctype: 'Sales Invoice', name: inv.name },
                    });
                    const fullInvoice = result.message;
                    const salesPersons = (fullInvoice.sales_team || []).map(m => m.sales_person).join(', ');
                    const cust = customerMap[inv.customer] || {};
                    detailedInvoices.push({
                      ...fullInvoice,
                      customer_name: cust.customer_name || inv.customer,
                      mobile_no: cust.mobile_no || '',
                      sales_persons: salesPersons || '',
                    });
                  } catch (err) {
                    console.error('Error fetching invoice details:', err);
                  }
                }

                // Filter by selected customer if set
                this.customerInvoices = detailedInvoices.filter(inv =>
                  !this.selectedCustomer || inv.customer === this.selectedCustomer.name
                );
              },
            });
          }
        },
      });
    },
    customFilter(item, queryText) {
      const nameMatch = item.customer_name?.toLowerCase().includes(queryText.toLowerCase());
      const mobileMatch = item.mobile_no?.toLowerCase().includes(queryText.toLowerCase());
      return nameMatch || mobileMatch;
    },
    loadMore() {
      this.displayCount += 10;
    },
    closeCustomerDialog() {
      this.customerDialog = false;
      this.selectedCustomer = null;
      this.customerInvoices = [];
    },
  },
  created() {
    this.$nextTick(() => {
      evntBus.$on('show_mesage', this.show_mesage);
      evntBus.$on('set_company', (data) => {
        this.company = data.name;
        this.company_img = data.company_logo || this.company_img;
      });
      evntBus.$on('register_pos_profile', (data) => {
        this.pos_profile = data.pos_profile;
        const payments = { text: 'Payments', icon: 'mdi-cash-register' };
        if (this.pos_profile.posa_use_pos_awesome_payments && this.items.length !== 2) {
          this.items.push(payments);
        }
      });
      evntBus.$on('set_last_invoice', (data) => {
        this.last_invoice = data;
      });
      evntBus.$on('freeze', (data) => {
        this.freeze = true;
        this.freezeTitle = data.title;
        this.freezeMsg = data.msg;
      });
      evntBus.$on('unfreeze', () => {
        this.freeze = false;
        this.freezeTitle = '';
        this.freezeMsg = '';
      });
    });
  },
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}
</style>