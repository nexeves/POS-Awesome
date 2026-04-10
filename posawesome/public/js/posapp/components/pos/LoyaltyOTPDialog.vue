<template>
  <v-dialog v-model="dialog" max-width="450" persistent>
    <v-card>
      <v-card-title class="headline primary--text">
        <v-icon left color="primary">mdi-shield-lock</v-icon>
        {{ __("Verify Loyalty Points Redemption") }}
      </v-card-title>

      <v-card-text class="pt-4">
        <!-- Customer Info -->
        <v-alert type="info" text dense class="mb-4">
          <div class="subtitle-2">{{ __("Customer") }}: {{ customer_name }}</div>
          <div class="subtitle-2">{{ __("Mobile") }}: {{ mobile_number }}</div>
          <div class="subtitle-2">
            {{ __("Points to Redeem") }}: {{ flt(loyalty_points_to_redeem, 2) }}
          </div>
          <div class="subtitle-2">
            {{ __("Amount") }}: {{ currency }}{{ flt(loyalty_amount, 2) }}
          </div>
        </v-alert>

        <!-- OTP Not Sent State -->
        <div v-if="!otp_sent && !otp_verified">
          <v-btn
            block
            large
            color="primary"
            @click="sendOTP"
            :loading="sending_otp"
            :disabled="sending_otp"
          >
            <v-icon left>mdi-message-text</v-icon>
            {{ __("Send OTP") }}
          </v-btn>
        </div>

        <!-- OTP Sent - Verification State -->
        <div v-if="otp_sent && !otp_verified">
          <v-text-field
            v-model="otp_code"
            :label="__('Enter OTP')"
            outlined
            dense
            type="text"
            maxlength="6"
            :rules="[rules.required, rules.otp_length]"
            :error-messages="otp_error"
            @input="otp_error = ''"
            @keyup.enter="verifyOTP"
            autofocus
            class="mb-2"
          >
            <template v-slot:append>
              <v-icon>mdi-lock</v-icon>
            </template>
          </v-text-field>

          <!-- Timer and Resend -->
          <div class="d-flex justify-space-between align-center mb-3">
            <div v-if="timer > 0" class="caption">
              {{ __("Resend OTP in") }} {{ timer }}s
            </div>
            <v-btn
              v-else
              text
              small
              color="primary"
              @click="resendOTP"
              :loading="sending_otp"
            >
              <v-icon left small>mdi-refresh</v-icon>
              {{ __("Resend OTP") }}
            </v-btn>
            <div class="caption grey--text">
              {{ __("Attempts") }}: {{ attempts }}/3
            </div>
          </div>

          <v-btn
            block
            large
            color="success"
            @click="verifyOTP"
            :loading="verifying_otp"
            :disabled="verifying_otp || !otp_code || otp_code.length !== 6"
          >
            <v-icon left>mdi-check-circle</v-icon>
            {{ __("Verify OTP") }}
          </v-btn>
        </div>

        <!-- OTP Verified State -->
        <div v-if="otp_verified">
          <v-alert type="success" prominent>
            <v-row align="center">
              <v-col class="grow">
                <div class="title">{{ __("Verification Successful!") }}</div>
                <div>{{ __("You can now redeem loyalty points") }}</div>
              </v-col>
            </v-row>
          </v-alert>
        </div>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          v-if="!otp_verified"
          color="grey"
          text
          @click="closeDialog"
          :disabled="sending_otp || verifying_otp"
        >
          {{ __("Cancel") }}
        </v-btn>
        <v-btn
          v-if="otp_verified"
          color="success"
          @click="applyLoyaltyPoints"
          large
        >
          <v-icon left>mdi-check</v-icon>
          {{ __("Apply Points") }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { evntBus } from "../../bus";

export default {
  data() {
    return {
      dialog: false,
      customer: "",
      customer_name: "",
      mobile_number: "",
      loyalty_points_to_redeem: 0,
      loyalty_amount: 0,
      currency: "",
      otp_sent: false,
      otp_verified: false,
      otp_code: "",
      otp_error: "",
      sending_otp: false,
      verifying_otp: false,
      timer: 0,
      attempts: 0,
      submission_id: "",
      timer_interval: null,
      rules: {
        required: (value) => !!value || this.__("Required"),
        otp_length: (value) =>
          (value && value.length === 6) || this.__("OTP must be 6 digits"),
      },
    };
  },

  methods: {
    flt(value, decimals = 2) {
      return parseFloat(value || 0).toFixed(decimals);
    },

    openDialog(data) {
      this.customer = data.customer;
      this.customer_name = data.customer_name;
      this.mobile_number = data.mobile_number;
      this.loyalty_points_to_redeem = data.loyalty_points_to_redeem;
      this.loyalty_amount = data.loyalty_amount;
      this.currency = data.currency || "";
      
      // Reset state
      this.otp_sent = false;
      this.otp_verified = false;
      this.otp_code = "";
      this.otp_error = "";
      this.attempts = 0;
      this.submission_id = "";
      
      this.dialog = true;
    },

    async sendOTP() {
      this.sending_otp = true;
      this.otp_error = "";

      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.otp_verification.send_loyalty_otp",
          args: {
            customer: this.customer,
            mobile_number: this.mobile_number,
            loyalty_points_to_redeem: this.loyalty_points_to_redeem,
          },
        });

        if (response.message && response.message.success) {
          this.otp_sent = true;
          this.submission_id = response.message.submission_id;
          this.startTimer();
          
          evntBus.$emit("show_mesage", {
            text: response.message.message,
            color: "success",
          });
        } else {
          evntBus.$emit("show_mesage", {
            text: this.__("Failed to send OTP"),
            color: "error",
          });
        }
      } catch (error) {
        console.error("Send OTP Error:", error);
        evntBus.$emit("show_mesage", {
          text: error.message || this.__("Error sending OTP"),
          color: "error",
        });
      } finally {
        this.sending_otp = false;
      }
    },

    async resendOTP() {
      this.otp_code = "";
      this.otp_error = "";
      
      this.sending_otp = true;

      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.otp_verification.resend_loyalty_otp",
          args: {
            customer: this.customer,
            mobile_number: this.mobile_number,
            loyalty_points_to_redeem: this.loyalty_points_to_redeem,
          },
        });

        if (response.message && response.message.success) {
          this.submission_id = response.message.submission_id;
          this.attempts = 0;
          this.startTimer();
          
          evntBus.$emit("show_mesage", {
            text: this.__("OTP resent successfully"),
            color: "success",
          });
        }
      } catch (error) {
        console.error("Resend OTP Error:", error);
        evntBus.$emit("show_mesage", {
          text: error.message || this.__("Error resending OTP"),
          color: "error",
        });
      } finally {
        this.sending_otp = false;
      }
    },

    async verifyOTP() {
      if (!this.otp_code || this.otp_code.length !== 6) {
        this.otp_error = this.__("Please enter a valid 6-digit OTP");
        return;
      }

      this.verifying_otp = true;
      this.otp_error = "";
      this.attempts++;

      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.otp_verification.verify_loyalty_otp",
          args: {
            customer: this.customer,
            mobile_number: this.mobile_number,
            otp_code: this.otp_code,
          },
        });

        if (response.message && response.message.success) {
          this.otp_verified = true;
          this.stopTimer();
          evntBus.$emit("show_mesage", {
            text: response.message.message,
            color: "success",
          });

          // ADD THIS FOR NEW WORKFLOW
          evntBus.$emit("loyalty_otp_verified", {
            customer: this.customer,
            loyalty_points: this.loyalty_points_to_redeem,
            loyalty_amount: this.loyalty_amount,
          });
        } else {
          this.otp_error = response.message.message;
          this.otp_code = "";
          if (this.attempts >= 3) {
            evntBus.$emit("show_mesage", {
              text: this.__("Maximum attempts exceeded. Please request a new OTP."),
              color: "error",
            });
            this.resetDialog();
          }
        }
      } catch (error) {
        console.error("Verify OTP Error:", error);
        this.otp_error = error.message || this.__("Error verifying OTP");
        this.otp_code = "";
      } finally {
        this.verifying_otp = false;
      }
    },

    applyLoyaltyPoints() {
      // Emit event to parent component (Payments.vue) to apply loyalty points
      evntBus.$emit("loyalty_otp_verified", {
        customer: this.customer,
        loyalty_points: this.loyalty_points_to_redeem,
        loyalty_amount: this.loyalty_amount,
      });
      
      this.closeDialog();
    },

    startTimer() {
      this.timer = 60; // 60 seconds
      this.timer_interval = setInterval(() => {
        this.timer--;
        if (this.timer <= 0) {
          this.stopTimer();
        }
      }, 1000);
    },

    stopTimer() {
      if (this.timer_interval) {
        clearInterval(this.timer_interval);
        this.timer_interval = null;
      }
    },

    resetDialog() {
      this.otp_sent = false;
      this.otp_verified = false;
      this.otp_code = "";
      this.otp_error = "";
      this.attempts = 0;
      this.stopTimer();
    },

    closeDialog() {
      this.stopTimer();
      this.dialog = false;
      
      // Reset after animation
      setTimeout(() => {
        this.resetDialog();
      }, 300);
    },
  },

  beforeDestroy() {
    this.stopTimer();
  },
};
</script>

<style scoped>
.v-text-field >>> input {
  text-align: center;
  font-size: 24px;
  letter-spacing: 8px;
  font-weight: bold;
}
</style>