<template>
  <v-row justify="center">
    <v-dialog v-model="closingDialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="headline primary--text">{{ __('Closing POS Shift') }}</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12" class="pa-1">
                <!-- Payment Reconciliation Table -->
                <v-data-table
                  :headers="headers"
                  :items="dialog_data.payment_reconciliation"
                  item-key="mode_of_payment"
                  class="elevation-1"
                  :items-per-page="itemsPerPage"
                  hide-default-footer
                >
                  <template v-slot:item.closing_amount="props">
                    <v-edit-dialog :return-value.sync="props.item.closing_amount">
                      {{ currencySymbol(pos_profile.currency) }}{{ formtCurrency(props.item.closing_amount) }}
                      <template v-slot:input>
                        <v-text-field
                          v-model="props.item.closing_amount"
                          :rules="[max25chars]"
                          :label="frappe._('Edit')"
                          single-line
                          counter
                          type="number"
                        ></v-text-field>
                      </template>
                    </v-edit-dialog>
                  </template>
                  <template v-slot:item.difference="{ item }">
                    {{ currencySymbol(pos_profile.currency) }}{{ formtCurrency(item.expected_amount - item.closing_amount) }}
                  </template>
                  <template v-slot:item.opening_amount="{ item }">
                    {{ currencySymbol(pos_profile.currency) }}{{ formtCurrency(item.opening_amount) }}
                  </template>
                  <template v-slot:item.expected_amount="{ item }">
                    {{ currencySymbol(pos_profile.currency) }}{{ formtCurrency(item.expected_amount) }}
                  </template>
                </v-data-table>
              </v-col>

              <!-- Currency Denomination Table -->
              <v-col cols="12" class="pa-1">
                <h3>{{ __('Currency Denomination') }}</h3>
                <v-data-table
                  :headers="denominationHeaders"
                  :items="currencyDenomination"
                  item-key="denomination"
                  hide-default-footer
                >
                  <template v-slot:body.prepend>
                    <tr>
                      <td>
                        <v-select
                          v-model="newDenomination.denomination"
                          :items="denominationOptions"
                          label="Denomination"
                          dense
                        ></v-select>
                      </td>
                      <td>
                        <v-text-field
                          v-model="newDenomination.count"
                          label="Count"
                          type="number"
                          dense
                        ></v-text-field>
                      </td>
                      <td>
                        <v-btn color="success" @click="addCurrencyDenomination">{{ __('Add') }}</v-btn>
                      </td>
                    </tr>
                  </template>

                  <template v-slot:item.total="{ item }">
                    {{ formtCurrency(item.denomination * item.count) }}
                  </template>
                </v-data-table>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">{{ __('Close') }}</v-btn>
          <v-btn color="success" dark @click="submit_dialog">{{ __('Submit') }}</v-btn>
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
    closingDialog: false,
    itemsPerPage: 20,
    dialog_data: {},
    pos_profile: '',
    currencyDenomination: [],
    newDenomination: {
      denomination: '',
      count: 0,
    },
    denominationOptions: ['0.5', '1', '5', '10', '20'],
    headers: [
      {
        text: __('Mode of Payment'),
        value: 'mode_of_payment',
        align: 'start',
        sortable: true,
      },
      {
        text: __('Opening Amount'),
        align: 'end',
        sortable: true,
        value: 'opening_amount',
      },
      {
        text: __('Closing Amount'),
        value: 'closing_amount',
        align: 'end',
        sortable: true,
      },
    ],
    denominationHeaders: [
      {
        text: __('Denomination'),
        value: 'denomination',
        align: 'start',
      },
      {
        text: __('Count'),
        value: 'count',
        align: 'start',
      },
      {
        text: __('Total'),
        value: 'total',
        align: 'start',
      },
    ],
    max25chars: (v) => v.length <= 25 || 'Input too long!',
  }),

  methods: {
    close_dialog() {
      this.closingDialog = false;
    },
    submit_dialog() {
      // Include the currencyDenomination data in dialog_data
      this.dialog_data.currencyDenomination = this.currencyDenomination;

      evntBus.$emit('submit_closing_pos', this.dialog_data);
      this.closingDialog = false;
    },
    addCurrencyDenomination() {
      if (this.newDenomination.denomination && this.newDenomination.count > 0) {
        // Add new denomination to the array
        this.currencyDenomination.push({
          denomination: this.newDenomination.denomination,
          count: this.newDenomination.count,
        });
        console.log('Current Currency Denomination:', this.currencyDenomination);

        // Clear the input fields
        this.newDenomination.denomination = '';
        this.newDenomination.count = 0;
      } else {
        // Optionally show a message if the inputs are invalid
        alert('Please fill in both fields correctly.');
      }
    },
  },

  created() {
    evntBus.$on('open_ClosingDialog', (data) => {
      this.closingDialog = true;
      this.dialog_data = data;
    });
    evntBus.$on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
      if (!this.pos_profile.hide_expected_amount) {
        this.headers.push({
          text: __('Expected Amount'),
          value: 'expected_amount',
          align: 'end',
          sortable: false,
        });
        this.headers.push({
          text: __('Difference'),
          value: 'difference',
          align: 'end',
          sortable: false,
        });
      }
    });
  },
};
</script>
