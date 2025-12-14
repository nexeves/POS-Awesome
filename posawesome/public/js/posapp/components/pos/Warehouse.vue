<template>
    <v-row justify="center">
      <v-dialog v-model="warehouseDialog" max-width="800px" min-width="800px">
        <v-card>
          <v-card-title>
            <span class="headline primary--text">{{
              __('Stock Details')
            }}</span>
          </v-card-title>
          <v-container>
            <v-row class="mb-4">
              <v-text-field
                color="primary"
                :label="frappe._('Item Code')"
                background-color="white"
                hide-details
                v-model="item_code"
                dense
                clearable
                class="mx-4"
              ></v-text-field>
              <v-btn
                text
                class="ml-2"
                color="primary"
                dark
                @click="search_stock"
                >{{ __('Search') }}</v-btn
              >
            </v-row>
            <v-row>
              <v-col cols="12" class="pa-1" v-if="dialog_data">
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
                    <template v-slot:item.grand_total="{ item }">{{
                      formtCurrency(item.grand_total)
                    }}</template>
                  </v-data-table>
                </template>
              </v-col>
            </v-row>
          </v-container>
          <v-card-actions class="mt-4">
            <v-spacer></v-spacer>
            <v-btn color="error mx-2" dark @click="close_dialog">Close</v-btn>
            <!-- <v-btn
              v-if="selected.length"
              color="success"
              dark
              @click="submit_dialog"
              >{{ __('Select') }}</v-btn
            > -->
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </template>
  <script>
  import { evntBus } from '../../bus';
  export default {
    data: () => ({
      warehouseDialog: false,
      singleSelect: true,
      selected: [],
      dialog_data: '',
      company: '',
      item_code: '',
      headers: [
        {
          text: __('Warehouse'),
          value: 'warehouse',
          align: 'start',
          sortable: true,
        },
        {
          text: __('Stock'),
          align: 'start',
          sortable: true,
          value: 'qty',
        },
      ],
    }),
    watch: {},
    methods: {
      close_dialog() {
        this.warehouseDialog = false;
      },

      search_stock() {
        const vm = this;
        frappe.call({
          method: 'posawesome.posawesome.api.posapp.search_available_qty',
          args: {
            item_code: vm.item_code,
            company: vm.company,
          },
          async: false,
          callback: function (r) {
            if (r.message) {
              console.log(r.message)
              vm.dialog_data = r.message;
            }
          },
        });
      },

    },
    created: function () {
      evntBus.$on('open_stock', (data) => {
        this.warehouseDialog = true;
        this.company = data.company;
        this.item_code = data.item_code;

        this.dialog_data = '';
        // this.selected = [];
      });
    },
  };
  </script>