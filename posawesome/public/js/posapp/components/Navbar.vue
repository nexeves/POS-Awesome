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
      <v-btn
        v-if="show_ecommerce_bell"
        icon
        color="primary"
        class="mr-2"
        :title="__('Online Orders')"
        @click="open_ecommerce_orders"
      >
        <v-badge
          :content="ecommerce_count"
          :value="ecommerce_count"
          color="badge"
          overlap
        >
          <v-icon>{{
            ecommerce_count ? 'mdi-bell-ring' : 'mdi-bell-outline'
          }}</v-icon>
        </v-badge>
      </v-btn>
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
        <!-- <MyPopup/> -->
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
              <v-list-item-title
                v-text="item.label || item.text"
              ></v-list-item-title>
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
      items: [{ text: 'POS', label: 'POS', icon: 'mdi-network-pos' }],
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
      ecommerce_count: 0,
      ecommerce_poll: null,
      ecommerce_subscribed: false,
      audio_ctx: null,
    };
  },
  computed: {
    show_ecommerce_bell() {
      return !!this.pos_profile.posa_allow_ecommerce_orders;
    },
  },
  methods: {
    changePage(key) {
      this.$emit('changePage', key);
    },
    add_page(entry) {
      // Keyed on `text` (the component name) rather than on a hardcoded array
      // length, so adding a page never silently suppresses another one.
      if (!this.items.some((item) => item.text === entry.text)) {
        this.items.push(entry);
      }
    },
    open_ecommerce_orders() {
      this.$emit('changePage', 'EcommerceOrders');
    },
    fetch_ecommerce_count() {
      if (!this.show_ecommerce_bell || !this.pos_profile.name) return;
      frappe.call({
        method:
          'posawesome.posawesome.api.ecommerce_orders.get_ecommerce_orders_count',
        args: { pos_profile: JSON.stringify(this.pos_profile) },
        callback: (r) => {
          this.ecommerce_count = r.message || 0;
        },
      });
    },
    on_ecommerce_order_created(data) {
      // The publish is a site-wide broadcast (the customer's own session has no
      // idea which cashiers are on shift), so each terminal filters to its own
      // branch here.
      if (!this.show_ecommerce_bell) return;
      if (
        this.pos_profile.warehouse &&
        data &&
        data.set_warehouse &&
        data.set_warehouse !== this.pos_profile.warehouse
      ) {
        return;
      }
      this.play_new_order_tone();
      evntBus.$emit('show_mesage', {
        text: __('New online order {0} from {1}', [
          data.name,
          data.customer_name || data.customer,
        ]),
        color: 'info',
      });
      // Re-read the count from the server rather than incrementing locally, so
      // the badge cannot drift out of step with reality.
      this.fetch_ecommerce_count();
      evntBus.$emit('new_ecommerce_order', data);
    },
    // A tone of its own for an order arriving from the app.
    //
    // play_sound('alert') is the same short blip the desk uses for every
    // notification; over counter noise it does not read as "an order just came
    // in", and a cashier who is used to it stops hearing it. This is a rising
    // three-note chime played twice, which is unlike anything else the POS
    // makes and carries across a shop.
    //
    // Synthesised rather than shipped as an audio file: no new asset to build
    // or cache-bust, and it still sounds on a terminal whose desk page did not
    // give us the <audio> elements play_sound depends on. Those remain the
    // fallback if the browser offers no Web Audio at all.
    play_new_order_tone() {
      if (frappe.boot && frappe.boot.user && frappe.boot.user.mute_sounds) {
        return;
      }
      try {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) throw new Error('Web Audio unavailable');
        if (!this.audio_ctx || this.audio_ctx.state === 'closed') {
          this.audio_ctx = new Ctx();
        }
        const ctx = this.audio_ctx;
        // Autoplay policy suspends a context built before the first gesture.
        // A cashier on an open shift has clicked something long ago, so
        // resuming is all that is needed.
        if (ctx.state === 'suspended') {
          ctx.resume();
        }

        const notes = [1046.5, 1318.5, 1568.0]; // C6 - E6 - G6
        const note_len = 0.13;
        const pass_gap = 0.55;
        for (let pass = 0; pass < 2; pass++) {
          notes.forEach((freq, i) => {
            const at = ctx.currentTime + pass * pass_gap + i * note_len;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.value = freq;
            // Ramped, not switched: a square edge on a raw oscillator is an
            // audible click on most counter speakers.
            gain.gain.setValueAtTime(0.0001, at);
            gain.gain.exponentialRampToValueAtTime(0.35, at + 0.012);
            gain.gain.exponentialRampToValueAtTime(0.0001, at + note_len);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(at);
            osc.stop(at + note_len + 0.02);
          });
        }
      } catch (e) {
        console.warn('posawesome: new-order tone unavailable', e);
        frappe.utils.play_sound('chime');
      }
    },

    subscribe_ecommerce_realtime(attempt = 0) {
      // frappe.realtime.on silently does nothing when the socket has not
      // connected yet, which would leave the bell permanently mute with no
      // error to show for it. Retry briefly until the socket exists.
      if (frappe.socketio && frappe.socketio.socket) {
        frappe.realtime.on(
          'ecommerce_order_created',
          this.on_ecommerce_order_created
        );
        this.ecommerce_subscribed = true;
        return;
      }
      if (attempt < 20) {
        setTimeout(() => this.subscribe_ecommerce_realtime(attempt + 1), 500);
      } else {
        console.warn(
          'posawesome: socket unavailable, falling back to polling for online orders'
        );
      }
    },
    start_ecommerce_watch() {
      if (!this.show_ecommerce_bell) return;
      this.fetch_ecommerce_count();
      if (!this.ecommerce_poll) {
        // Reconciliation sweep: realtime is the fast path, this catches
        // anything missed while the socket was down or the tab was asleep.
        this.ecommerce_poll = setInterval(() => {
          this.fetch_ecommerce_count();
        }, 60000);
      }
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
        if (this.pos_profile.posa_use_pos_awesome_payments) {
          this.add_page({
            text: 'Payments',
            label: 'Payments',
            icon: 'mdi-cash-register',
          });
        }
        if (this.pos_profile.posa_allow_ecommerce_orders) {
          this.add_page({
            text: 'EcommerceOrders',
            label: 'Online Orders',
            icon: 'mdi-cart-outline',
          });
        }
        this.start_ecommerce_watch();
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
      evntBus.$on('ecommerce_orders_seen', () => {
        this.fetch_ecommerce_count();
      });
      this.subscribe_ecommerce_realtime();
    });
  },
  beforeDestroy() {
    if (this.ecommerce_subscribed) {
      frappe.realtime.off(
        'ecommerce_order_created',
        this.on_ecommerce_order_created
      );
    }
    if (this.ecommerce_poll) {
      clearInterval(this.ecommerce_poll);
      this.ecommerce_poll = null;
    }
  },
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}
</style>
