<template>
  <v-container fill-height fluid class="customer-display primary px-0 py-0" style="height: 100vh; max-width: 100%;">
    <v-row no-gutters class="fill-height">
      <!-- Left side: Items List -->
      <v-col cols="7" class="white fill-height d-flex flex-column" style="box-shadow: 4px 0 16px rgba(0,0,0,0.08); z-index: 2;">
        <v-toolbar color="primary" dark flat class="elevation-2 px-4" height="80">
          <v-img
            src="/assets/posawesome/js/posapp/components/pos/pos.png"
            max-width="50"
            class="mr-4"
          ></v-img>
          <v-toolbar-title class="text-h4 font-weight-black tracking-wide">
            CUSTOMER DISPLAY
          </v-toolbar-title>
        </v-toolbar>

        <div class="px-6 py-4 bg-light font-weight-bold grey--text text--darken-2 d-flex justify-space-between mt-2" style="border-bottom: 2px solid #eee;">
          <div style="flex: 2">Item</div>
          <div style="flex: 1" class="text-center">Qty x Rate</div>
          <div style="flex: 1" class="text-right">Total</div>
        </div>

        <div class="flex-grow-1 overflow-auto px-6 py-4 bg-light">
          <transition-group name="list" tag="div">
            <v-card
              v-for="(item, index) in invoice.items"
              :key="item.posa_row_id || index"
              class="mb-3 item-card hover-lift transition-fast"
              elevation="1"
            >
              <v-card-text class="pa-4">
                <v-row align="center">
                  <v-col cols="6">
                    <div class="text-h6 font-weight-bold black--text text-truncate">{{ item.item_name }}</div>
                  </v-col>
                  <v-col cols="3" class="text-center">
                    <v-chip color="primary" outlined class="font-weight-bold text-subtitle-1 px-3">
                      {{ formtFloat(item.qty) }} x {{ formtCurrency(item.rate) }}
                    </v-chip>
                  </v-col>
                  <v-col cols="3" class="text-right">
                    <div class="text-h5 primary--text font-weight-black">
                      {{ formtCurrency(flt(item.qty, float_precision) * flt(item.rate, currency_precision)) }}
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </transition-group>
          
          <div v-if="!invoice.items || invoice.items.length === 0" class="text-center mt-12 d-flex flex-column align-center justify-center">
            <v-avatar size="140" color="primary lighten-5" class="mb-6 elevation-2">
              <v-icon size="80" color="primary">mdi-cart-arrow-down</v-icon>
            </v-avatar>
            <div class="text-h4 primary--text font-weight-bold mb-2">Welcome!</div>
            <div class="text-h6 grey--text">Please proceed to scan your items...</div>
          </div>
        </div>
      </v-col>

      <!-- Right side: Totals -->
      <v-col cols="5" class="fill-height d-flex flex-column justify-center align-center" style="background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%);">
        <v-card class="elevation-12 rounded-xl pa-8 text-center" width="85%" max-width="500" color="rgba(255,255,255,0.95)" style="backdrop-filter: blur(10px);">
          
          <div class="text-h6 grey--text text--darken-1 mb-1 text-uppercase tracking-widest">Total Items</div>
          <div class="text-h3 font-weight-black mb-6 black--text">{{ formtFloat(invoice.total_qty) || 0 }}</div>
          
          <v-divider class="my-4"></v-divider>
          
          <div class="d-flex justify-space-between align-center mb-3 px-4">
            <span class="text-h6 grey--text text--darken-2 font-weight-medium">Subtotal</span>
            <span class="text-h6 font-weight-bold">{{ currencySymbol(pos_profile.currency) }} {{ formtCurrency(invoice.subtotal) || '0.00' }}</span>
          </div>
          
          <div class="d-flex justify-space-between align-center mb-4 px-4 red--text text--darken-1" v-if="invoice.discount_amount > 0">
            <span class="text-h6 font-weight-medium">Discount</span>
            <span class="text-h6 font-weight-bold">- {{ currencySymbol(pos_profile.currency) }} {{ formtCurrency(invoice.discount_amount) }}</span>
          </div>
          
          <div class="primary rounded-xl pa-6 mt-6 elevation-4">
            <div class="text-subtitle-1 white--text text-uppercase tracking-widest mb-1 opacity-80">Total Amount Due</div>
            <div class="d-flex justify-center align-baseline">
              <span class="text-h4 white--text mr-2 font-weight-medium">{{ currencySymbol(pos_profile.currency) }}</span>
              <span class="text-h1 white--text font-weight-black" style="font-size: 4.5rem !important;">{{ formtCurrency(invoice.grand_total) || '0.00' }}</span>
            </div>
          </div>

        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

export default {
  data() {
    return {
      channel: null,
      invoice: {
        items: [],
        total_qty: 0,
        subtotal: 0,
        discount_amount: 0,
        grand_total: 0
      },
      pos_profile: {
        currency: frappe.defaults.get_default("currency") || 'OMR'
      },
      float_precision: 3,
      currency_precision: 3
    }
  },
  methods: {
    extractNumber(val) {
      if (typeof val === 'number') return val;
      if (!val) return 0;
      const matches = String(val).match(/-?\d+(\.\d+)?/);
      return matches ? Number(matches[0]) : 0;
    },
    formtCurrency(value) {
      return this.extractNumber(value).toLocaleString(undefined, { minimumFractionDigits: this.currency_precision, maximumFractionDigits: this.currency_precision });
    },
    formtFloat(value) {
      return this.extractNumber(value).toLocaleString(undefined, { minimumFractionDigits: this.float_precision, maximumFractionDigits: this.float_precision });
    },
    currencySymbol(currency) {
      return frappe.model.get_value('Currency', currency, 'symbol') || currency;
    },
    flt(value, precision) {
      return this.extractNumber(value);
    }
  },
  mounted() {
    this.float_precision = frappe.defaults.get_default("float_precision") || 3;
    this.currency_precision = frappe.defaults.get_default("currency_precision") || 3;
    
    // Hide navbar if present
    document.querySelectorAll('.navbar').forEach(el => el.style.display = 'none');

    // Setup BroadcastChannel
    if ('BroadcastChannel' in window) {
      const urlParams = new URLSearchParams(window.location.search);
      const channelId = urlParams.get('channel_id') || 'default';
      this.channel = new BroadcastChannel(channelId);
      this.channel.onmessage = (event) => {
        if (event.data && event.data.action === 'UPDATE_INVOICE') {
          this.invoice = event.data.invoice;
          if (event.data.pos_profile) {
            this.pos_profile = event.data.pos_profile;
          }
        }
      };
      
      // Request initial state from POS
      this.channel.postMessage({ action: 'REQUEST_INVOICE' });
    } else {
      console.warn("BroadcastChannel API not supported in this browser.");
    }
  },
  beforeDestroy() {
    if (this.channel) {
      this.channel.close();
    }
  }
}
</script>

<style scoped>
.customer-display {
  font-family: "Inter", "Roboto", "Segoe UI", sans-serif;
  overflow: hidden; /* Prevent body scroll */
}

.bg-light {
  background-color: #f8fbfa;
}

.tracking-wide {
  letter-spacing: 1px;
}

.tracking-widest {
  letter-spacing: 2px;
}

.opacity-80 {
  opacity: 0.8;
}

/* List Transitions */
.list-enter-active, .list-leave-active {
  transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1); /* Smoother vuetify curve */
}
.list-enter, .list-leave-to {
  opacity: 0;
  transform: translateX(-40px) scale(0.98);
}
.transition-fast {
  transition: all 0.2s ease-in-out;
}
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

.item-card {
  border-left: 6px solid #0097A7 !important;
  border-radius: 12px;
  background: white;
}
.item-card:nth-child(even) {
  border-left-color: #00BCD4 !important;
}

.totals-card {
  box-shadow: 0 16px 40px rgba(0,0,0,0.12) !important;
}
</style>
