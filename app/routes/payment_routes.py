"""
Payment Routes
Handles Stripe payment processing, webhooks, and success pages
"""

import json
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect

from config.stripe_config import stripe_config
from app.services.email_service import EmailService

payment_bp = Blueprint('payment', __name__, url_prefix='/api')

@payment_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe Checkout Session for payment."""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'Order ID is required'
            }), 400
        
        # Load order data
        order_file_path = Path('output/orders') / f"order_{order_id}.json"
        if not order_file_path.exists():
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        with open(order_file_path, 'r', encoding='utf-8') as f:
            order_data = json.load(f)
        
        # Add full cover URL for Stripe
        order_data['cover_url'] = f"{request.host_url}api/cover/{order_id}"
        
        # Create Stripe Checkout Session
        session_data = stripe_config.create_checkout_session(order_data)
        
        # Update order with session info
        order_data['stripe_session_id'] = session_data['id']
        order_data['payment_status'] = 'checkout_created'
        order_data['checkout_created_at'] = datetime.now().isoformat()
        
        # Save updated order
        with open(order_file_path, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'checkout_url': session_data['url'],
            'session_id': session_data['id'],
            'amount': stripe_config.format_amount(stripe_config.book_price_cents)
        })
        
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create checkout session: {str(e)}'
        }), 500

@payment_bp.route('/mock-payment/<order_id>')
def mock_payment_page(order_id):
    """Mock payment page for local development."""
    if not stripe_config.mock_payment:
        return jsonify({'error': 'Mock payments not enabled'}), 404
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mock Payment - Local Development</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .payment-form {{ background: #f9f9f9; padding: 30px; border-radius: 10px; text-align: center; }}
            button {{ background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
            button:hover {{ background: #218838; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="warning">
            <strong>⚠️ DEVELOPMENT MODE</strong><br>
            This is a mock payment page for local development only.
        </div>
        <div class="payment-form">
            <h2>Complete Your Payment</h2>
            <p>Order ID: {order_id}</p>
            <p>Amount: {stripe_config.format_amount(stripe_config.book_price_cents)}</p>
            <button onclick="processPayment()">Complete Mock Payment</button>
        </div>
        
        <script>
            function processPayment() {{
                // Simulate payment processing
                document.body.innerHTML = '<div style="text-align: center; margin-top: 100px;"><h2>Processing Payment...</h2><p>Please wait...</p></div>';
                
                setTimeout(() => {{
                    fetch('/api/webhook/stripe', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            type: 'checkout.session.completed',
                            data: {{ object: {{ id: 'cs_mock_{order_id}', metadata: {{ order_id: '{order_id}' }} }} }}
                        }})
                    }}).then(() => {{
                        window.location.href = '/success?session_id=cs_mock_{order_id}&order_id={order_id}';
                    }});
                }}, {stripe_config.mock_payment_delay * 1000});
            }}
        </script>
    </body>
    </html>
    """

@payment_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for payment confirmation."""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature', '')
        
        # Verify webhook signature
        event = stripe_config.verify_webhook_signature(payload, sig_header)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session_data = event['data']['object']
            order_id = session_data['metadata']['order_id']
            
            # Update order status
            order_file_path = Path('output/orders') / f"order_{order_id}.json"
            if order_file_path.exists():
                with open(order_file_path, 'r', encoding='utf-8') as f:
                    order_data = json.load(f)
                
                # Update payment status
                order_data['payment_status'] = 'paid'
                order_data['payment_date'] = datetime.now().isoformat()
                order_data['stripe_session_completed'] = session_data['id']
                order_data['status'] = 'paid_awaiting_production'
                
                # Save updated order
                with open(order_file_path, 'w', encoding='utf-8') as f:
                    json.dump(order_data, f, indent=2, ensure_ascii=False)
                
                # Send confirmation emails
                email_service = EmailService()
                email_service.send_customer_confirmation(order_data)
                email_service.send_production_notification(order_data)
                
                print(f"Payment completed for order {order_id}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400 