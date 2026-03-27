import frappe
from frappe import _
import hashlib
import time
import random
import requests
from datetime import datetime, timedelta

def get_sms_config():
    """Get SMS API configuration from site config or custom doctype"""
    return {
        'access_token': frappe.conf.get('firstdial_access_token'),
        'access_token_key': frappe.conf.get('firstdial_access_token_key'),
        'base_url': 'https://firstdialsms.in/api/sms/v1.0',
        'sms_header': frappe.conf.get('firstdial_sms_header'),
        'entity_id': frappe.conf.get('firstdial_entity_id', ''),
        'template_id': frappe.conf.get('firstdial_otp_template_id'),
    }

def generate_md5_signature(request_for, expire, access_token, access_token_key):
    """Generate MD5 signature for FirstDial SMS API authentication"""
    time_key = hashlib.md5(
        f"{request_for}sms@rits-v1.0{expire}".encode()
    ).hexdigest()
    
    time_access_token_key = hashlib.md5(
        f"{access_token}{time_key}".encode()
    ).hexdigest()
    
    signature = hashlib.md5(
        f"{time_access_token_key}{access_token_key}".encode()
    ).hexdigest()
    
    return signature

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

@frappe.whitelist()
def send_loyalty_otp(customer, mobile_number, loyalty_points_to_redeem):
    """
    Send OTP to customer's mobile number for loyalty points redemption
    Args:
        customer: Customer ID
        mobile_number: Customer's mobile number
        loyalty_points_to_redeem: Points customer wants to redeem
    """
    try:
        # Validate customer
        if not frappe.db.exists("Customer", customer):
            frappe.throw(_("Customer not found"))
        
        # Validate customer doc
        customer_doc = frappe.get_doc("Customer", customer)
        if not customer_doc.loyalty_program:
            frappe.throw(_("Customer is not enrolled in any loyalty program"))
        
        # Get available loyalty points
        loyalty_points = get_loyalty_points(customer)
        if float(loyalty_points_to_redeem) > float(loyalty_points):
            frappe.throw(_("Insufficient loyalty points. Available: {0}").format(loyalty_points))
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP in cache with 5 minutes expiry
        cache_key = f"loyalty_otp_{customer}_{mobile_number}"
        otp_data = {
            'otp': otp,
            'customer': customer,
            'mobile_number': mobile_number,
            'loyalty_points': loyalty_points_to_redeem,
            'attempts': 0,
            'created_at': datetime.now().isoformat()
        }
        frappe.cache().set_value(cache_key, otp_data, expires_in_sec=300)  # 5 minutes
        
        # Send SMS via FirstDial API
        sms_config = get_sms_config()
        if not sms_config['access_token'] or not sms_config['access_token_key']:
            frappe.throw(_("SMS API credentials not configured"))
        
        # Prepare SMS message with DLT template
        # Template: Dear Customer, Your OTP For Point Redemption is : {#var#} - ESPANSHE
        message = f"Dear Customer, Your OTP For Point Redemption is : {otp} - ESPANSHE"
        
        # Calculate authentication
        request_for = "send-sms"
        expire = int(time.time()) + 60  # 1 minute from now
        signature = generate_md5_signature(
            request_for,
            expire,
            sms_config['access_token'],
            sms_config['access_token_key']
        )
        
        # Make API call using GET method (as per your test API)
        url = f"{sms_config['base_url']}/send-sms"
        
        # Prepare query parameters for GET request
        params = {
            'accessToken': sms_config['access_token'],
            'expire': expire,
            'authSignature': signature,
            'route': 'transactional',
            'smsHeader': sms_config['sms_header'],
            'messageContent': message,
            'recipients': mobile_number,
            'contentType': 'text',
            'entityId': sms_config['entity_id'],
            'templateId': sms_config['template_id'],
        }
        
        frappe.log_error(
            title="OTP SMS Request",
            message=f"Sending SMS to {mobile_number}\nParams: {params}"
        )
        
        # Use GET method as shown in your test API
        response = requests.get(url, params=params, timeout=10)
        response_data = response.json()
        
        frappe.log_error(
            title="OTP SMS Response",
            message=f"Response: {response_data}\nStatus Code: {response.status_code}"
        )
        
        if response.status_code == 200 and response_data.get('status') == 'success':
            return {
                'success': True,
                'message': _('OTP sent successfully to {0}').format(mobile_number),
                'submission_id': response_data.get('submissionId')
            }
        else:
            error_message = response_data.get('message', 'Unknown error')
            frappe.log_error(
                title="SMS API Error",
                message=f"Failed to send OTP: {response_data}"
            )
            frappe.throw(_("Failed to send OTP: {0}").format(error_message))
            
    except Exception as e:
        frappe.log_error(title="OTP Send Error", message=str(e))
        frappe.throw(_("Error sending OTP: {0}").format(str(e)))

@frappe.whitelist()
def verify_loyalty_otp(customer, mobile_number, otp_code):
    """
    Verify OTP for loyalty points redemption
    Args:
        customer: Customer ID
        mobile_number: Customer's mobile number
        otp_code: OTP entered by user
    """
    try:
        cache_key = f"loyalty_otp_{customer}_{mobile_number}"
        otp_data = frappe.cache().get_value(cache_key)
        
        if not otp_data:
            return {
                'success': False,
                'message': _('OTP expired or not found. Please request a new OTP.')
            }
        
        # Check attempts limit
        if otp_data.get('attempts', 0) >= 3:
            frappe.cache().delete_value(cache_key)
            return {
                'success': False,
                'message': _('Maximum verification attempts exceeded. Please request a new OTP.')
            }
        
        # Increment attempts
        otp_data['attempts'] = otp_data.get('attempts', 0) + 1
        frappe.cache().set_value(cache_key, otp_data, expires_in_sec=300)
        
        # Verify OTP
        if str(otp_code) == str(otp_data['otp']):
            # OTP verified successfully
            frappe.cache().delete_value(cache_key)
            
            # Log the verification
            log_otp_verification(customer, mobile_number, True, otp_data['loyalty_points'])
            
            return {
                'success': True,
                'message': _('OTP verified successfully'),
                'loyalty_points': otp_data['loyalty_points']
            }
        else:
            remaining_attempts = 3 - otp_data['attempts']
            return {
                'success': False,
                'message': _('Invalid OTP. {0} attempts remaining.').format(remaining_attempts)
            }
            
    except Exception as e:
        frappe.log_error(title="OTP Verification Error", message=str(e))
        return {
            'success': False,
            'message': _('Error verifying OTP: {0}').format(str(e))
        }

def get_loyalty_points(customer):
    """Get available loyalty points for customer"""
    try:
        from erpnext.accounts.doctype.loyalty_program.loyalty_program import get_loyalty_program_details_with_points
        
        loyalty_program_details = get_loyalty_program_details_with_points(
            customer=customer,
            company=frappe.defaults.get_user_default("company"),
            loyalty_program="Loyalty 1",
            expiry_date=frappe.utils.nowdate(),
            silent=True
        )
        
        return loyalty_program_details.get('loyalty_points', 0) if loyalty_program_details else 0
    except Exception as e:
        frappe.log_error(title="Get Loyalty Points Error", message=str(e))
        return 0

def log_otp_verification(customer, mobile_number, success, loyalty_points):
    """Log OTP verification attempts"""
    try:
        frappe.get_doc({
            'doctype': 'Comment',
            'comment_type': 'Info',
            'reference_doctype': 'Customer',
            'reference_name': customer,
            'content': f"OTP Verification {'Successful' if success else 'Failed'} for {loyalty_points} loyalty points redemption. Mobile: {mobile_number}"
        }).insert(ignore_permissions=True)
    except:
        pass

@frappe.whitelist()
def resend_loyalty_otp(customer, mobile_number, loyalty_points_to_redeem):
    """Resend OTP (same as send but clears previous cache)"""
    cache_key = f"loyalty_otp_{customer}_{mobile_number}"
    frappe.cache().delete_value(cache_key)
    return send_loyalty_otp(customer, mobile_number, loyalty_points_to_redeem)