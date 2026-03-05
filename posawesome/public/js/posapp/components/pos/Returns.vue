<template>
  <v-row justify="center">
    <v-dialog v-model="invoicesDialog" max-width="800px" min-width="800px">
      <v-card>
        <v-card-title>
          <span class="headline primary--text">{{
            __('Select Return Invoice')
          }}</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
            <v-text-field
              color="primary"
              :label="frappe._('Invoice ID, Customer ID Or Mobile No')"
              background-color="white"
              hide-details
              v-model="invoice_name"
              dense
              clearable
              class="mx-4"
            ></v-text-field>
            <v-btn
              text
              class="ml-2"
              color="primary"
              dark
              @click="search_invoices"
              >{{ __('Search') }}</v-btn
            >
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1" v-if="dialog_data && !showItemSelection">
              <template>
                <v-data-table
                  :headers="headers"
                  :items="dialog_data"
                  item-key="name"
                  class="elevation-1"
                  :single-select="singleSelect"
                  show-select
                  v-model="selected"
                >
                  <template v-slot:item.grand_total="{ item }">
                    {{ currencySymbol(item.currency) }}
                    {{ formtCurrency(item.grand_total) }}</template
                  >
                </v-data-table>
              </template>
            </v-col>
            
            <!-- Item Selection Table -->
            <v-col cols="12" class="pa-1" v-if="showItemSelection">
              <v-card-subtitle class="pb-0">
                <v-btn icon small @click="backToInvoiceList">
                  <v-icon>mdi-arrow-left</v-icon>
                </v-btn>
                <span class="ml-2">{{ __('Select Items from Invoice:') }} {{ selectedInvoice.name }}</span>
              </v-card-subtitle>
              <v-data-table
                :headers="itemHeaders"
                :items="invoiceItems"
                item-key="idx"
                class="elevation-1"
                show-select
                v-model="selectedItems"
              >
                <template v-slot:item.rate="{ item }">
                  {{ currencySymbol(selectedInvoice.currency) }}
                  {{ formtCurrency(item.rate) }}
                </template>
                <template v-slot:item.amount="{ item }">
                  {{ currencySymbol(selectedInvoice.currency) }}
                  {{ formtCurrency(item.amount) }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error mx-2" dark @click="close_dialog">Close</v-btn>
          <v-btn
            v-if="selected.length && !showItemSelection"
            color="primary"
            dark
            @click="showItems"
            >{{ __('Next') }}</v-btn
          >
          <v-btn
            v-if="showItemSelection && selectedItems.length"
            color="success"
            dark
            @click="submit_dialog"
            >{{ __('Select') }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
import format from '../../format';
export default {
  mixins: [format],
  data: () => ({
    invoicesDialog: false,
    singleSelect: true,
    selected: [],
    selectedItems: [],
    dialog_data: '',
    company: '',
    invoice_name: '',
    showItemSelection: false,
    selectedInvoice: null,
    invoiceItems: [],
    headers: [
      {
        text: __('Customer'),
        value: 'customer',
        align: 'start',
        sortable: true,
      },
      {
        text: __('Name'),
        value: 'customer_name',
        sortable: true,
      },
      {
        text: __('Date'),
        align: 'start',
        sortable: true,
        value: 'posting_date',
      },
      {
        text: __('Invoice'),
        value: 'name',
        align: 'start',
        sortable: true,
      },
      {
        text: __('Amount'),
        value: 'grand_total',
        align: 'end',
        sortable: false,
      },
    ],
    itemHeaders: [
      {
        text: __('Item Code'),
        value: 'item_code',
        align: 'start',
        sortable: true,
      },
      {
        text: __('Item Name'),
        value: 'item_name',
        sortable: true,
      },
      {
        text: __('Qty'),
        value: 'qty',
        align: 'center',
        sortable: false,
      },
      {
        text: __('Rate'),
        value: 'rate',
        align: 'end',
        sortable: false,
      },
      {
        text: __('Amount'),
        value: 'amount',
        align: 'end',
        sortable: false,
      },
    ],
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.invoicesDialog = false;
      this.showItemSelection = false;
      this.selectedItems = [];
      this.selectedInvoice = null;
      this.invoiceItems = [];
    },
    search_invoices_by_enter(e) {
      if (e.keyCode === 13) {
        this.search_invoices();
      }
    },
    search_invoices() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.search_invoices_for_return',
        args: {
          invoice_name: vm.invoice_name,
          company: vm.company,
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            vm.dialog_data = r.message;
          }
        },
      });
    },
    showItems() {
      if (this.selected.length > 0) {
        this.selectedInvoice = this.selected[0];
        this.invoiceItems = [...this.selectedInvoice.items];
        this.showItemSelection = true;
        this.selectedItems = [];
      }
    },
    backToInvoiceList() {
      this.showItemSelection = false;
      this.selectedItems = [];
      this.invoiceItems = [];
    },
    submit_dialog() {
      if (this.selectedItems.length > 0) {
        const return_doc = this.selectedInvoice;
        const invoice_doc = {};
        const items = [];
        
        // Only process selected items
        this.selectedItems.forEach((item) => {
          const new_item = { ...item };
          new_item.qty = item.qty * -1;
          new_item.stock_qty = item.stock_qty * -1;
          new_item.amount = item.amount * -1;
          items.push(new_item);
        });
        
        invoice_doc.items = items;
        invoice_doc.is_return = 1;
        invoice_doc.return_against = return_doc.name;
        invoice_doc.customer = return_doc.customer;
        const data = { invoice_doc, return_doc };
        evntBus.$emit('load_return_invoice', data);
        this.invoicesDialog = false;
        this.showItemSelection = false;
        this.selectedItems = [];
        this.selectedInvoice = null;
      }
    },
  },
  created: function () {
    evntBus.$on('open_returns', (data) => {
      this.invoicesDialog = true;
      this.company = data;
      this.invoice_name = '';
      this.dialog_data = '';
      this.selected = [];
      this.showItemSelection = false;
      this.selectedItems = [];
      this.selectedInvoice = null;
      this.invoiceItems = [];
    });
  },
};
</script>