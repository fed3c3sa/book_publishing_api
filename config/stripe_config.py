#!/usr/bin/env python3
"""
Stripe Configuration Module
Handles Stripe payment integration with proper security and best practices
"""

import os
import stripe
from typing import Dict, Any, Optional
from decimal import Decimal

class StripeConfig:
    """Stripe configuration and utilities following best practices"""
    
    def __init__(self):
        """Initialize Stripe configuration"""
        # Environment detection
        self.is_local = os.getenv('ENVIRONMENT', 'local').lower() == 'local'
        self.is_production = os.getenv('ENVIRONMENT', 'local').lower() == 'production'
        
        # Stripe API Keys (use test keys for development)
        if self.is_production:
            self.api_key = os.getenv('STRIPE_LIVE_SECRET_KEY')
            self.publishable_key = os.getenv('STRIPE_LIVE_PUBLISHABLE_KEY')
            self.webhook_secret = os.getenv('STRIPE_LIVE_WEBHOOK_SECRET')
        else:
            self.api_key = os.getenv('STRIPE_TEST_SECRET_KEY', 'sk_test_...')
            self.publishable_key = os.getenv('STRIPE_TEST_PUBLISHABLE_KEY', 'pk_test_...')
            self.webhook_secret = os.getenv('STRIPE_TEST_WEBHOOK_SECRET', 'whsec_...')
        
        # Configure Stripe - use real keys if available, otherwise mock
        # Check if we have real Stripe keys configured
        has_real_keys = (
            self.api_key and self.api_key != 'sk_test_...' and 
            self.publishable_key and self.publishable_key != 'pk_test_...'
        )
        
        if has_real_keys:
            stripe.api_key = self.api_key
            self.mock_payment = False
            print(f"✅ Using real Stripe API keys ({'LIVE' if self.is_production else 'TEST'} mode)")
        else:
            self.mock_payment = True
            print("⚠️  Using mock payments - no valid Stripe keys found")
        
        # Product configuration
        self.book_price_cents = 599  # $5.99
        self.currency = 'eur'  # Changed to EUR for Italian market
        
        # Mock payment settings
        self.mock_payment_delay = 2  # seconds to simulate payment processing
        
    def get_publishable_key(self) -> str:
        """Get the publishable key for frontend"""
        return self.publishable_key
    
    def create_checkout_session(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session following best practices
        
        Args:
            order_data: Dictionary containing order information
            
        Returns:
            Dictionary with session data or mock data for local development
        """
        if self.mock_payment:
            # Return mock data for local development
            return {
                'id': f"cs_mock_{order_data['order_id']}",
                'url': f"/api/mock-payment/{order_data['order_id']}",
                'payment_status': 'mock'
            }
        
        try:
            # Create the actual Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': self.currency,
                        'product_data': {
                            'name': f"Libro Personalizzato: {order_data['book_title']}",
                            'description': f"Libro per bambini personalizzato ({order_data['num_pages']} pagine, età {order_data['age_group']})",
                            'images': [order_data.get('cover_url', '')],
                        },
                        'unit_amount': self.book_price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5001')}/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order_data['order_id']}",
                cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5001')}/?cancelled=true",
                metadata={
                    'order_id': order_data['order_id'],
                    'customer_email': order_data['customer_email'],
                    'book_title': order_data['book_title'],
                },
                customer_email=order_data['customer_email'],
                billing_address_collection='required',
                shipping_address_collection={
                    'allowed_countries': ['IT', 'US', 'GB', 'FR', 'DE', 'ES'],
                },
                phone_number_collection={
                    'enabled': True,
                },
            )
            
            return {
                'id': session.id,
                'url': session.url,
                'payment_status': 'pending'
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature for security
        
        Args:
            payload: Raw request body
            sig_header: Stripe signature header
            
        Returns:
            Verified event data
        """
        if self.mock_payment:
            # Mock event for local development
            return {
                'type': 'checkout.session.completed',
                'data': {'object': {'id': 'mock_session'}}
            }
        
        # Verify we have a webhook secret
        if not self.webhook_secret or self.webhook_secret == 'whsec_...':
            raise Exception("No valid webhook secret configured for Stripe verification")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")
    
    def retrieve_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve Stripe session details
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            Session data
        """
        if self.mock_payment or session_id.startswith('cs_mock_'):
            # Mock session data for local development
            order_id = session_id.replace('cs_mock_', '')
            return {
                'id': session_id,
                'payment_status': 'paid',
                'amount_total': self.book_price_cents,
                'currency': self.currency,
                'metadata': {'order_id': order_id},
                'customer_details': {
                    'email': 'test@example.com',
                    'name': 'Test Customer'
                }
            }
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Error retrieving session: {str(e)}")
    
    def format_amount(self, amount_cents: int) -> str:
        """
        Format amount for display
        
        Args:
            amount_cents: Amount in cents
            
        Returns:
            Formatted amount string
        """
        amount = Decimal(amount_cents) / 100
        if self.currency == 'eur':
            return f"€{amount:.2f}"
        elif self.currency == 'usd':
            return f"${amount:.2f}"
        else:
            return f"{amount:.2f} {self.currency.upper()}"

# Global instance
stripe_config = StripeConfig() 