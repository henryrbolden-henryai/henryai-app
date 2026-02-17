"""
Stripe Service for HenryHQ

Handles Stripe Checkout sessions, Customer Portal sessions, and webhook events
for subscription billing.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import stripe
from supabase import Client

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Price ID mapping: tier -> {monthly: price_id, annual: price_id}
STRIPE_PRICE_MAP = {
    'recruiter': {
        'monthly': os.getenv('STRIPE_PRICE_RECRUITER_MONTHLY'),
        'annual': os.getenv('STRIPE_PRICE_RECRUITER_ANNUAL'),
    },
    'principal': {
        'monthly': os.getenv('STRIPE_PRICE_PRINCIPAL_MONTHLY'),
        'annual': os.getenv('STRIPE_PRICE_PRINCIPAL_ANNUAL'),
    },
    'partner': {
        'monthly': os.getenv('STRIPE_PRICE_PARTNER_MONTHLY'),
        'annual': os.getenv('STRIPE_PRICE_PARTNER_ANNUAL'),
    },
    'coach': {
        'monthly': os.getenv('STRIPE_PRICE_COACH_MONTHLY'),
        'annual': os.getenv('STRIPE_PRICE_COACH_ANNUAL'),
    },
}

# Reverse map: price_id -> tier name (built at import time)
PRICE_TO_TIER: Dict[str, str] = {}
for tier_name, prices in STRIPE_PRICE_MAP.items():
    for period, price_id in prices.items():
        if price_id:
            PRICE_TO_TIER[price_id] = tier_name


def get_price_id(tier: str, billing_period: str) -> Optional[str]:
    """Get the Stripe Price ID for a tier and billing period."""
    tier_prices = STRIPE_PRICE_MAP.get(tier)
    if not tier_prices:
        return None
    return tier_prices.get(billing_period)


def tier_from_price_id(price_id: str) -> Optional[str]:
    """Look up tier name from a Stripe Price ID."""
    return PRICE_TO_TIER.get(price_id)


class StripeService:
    """Service for managing Stripe subscription billing."""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        tier: str,
        billing_period: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """
        Create a Stripe Checkout Session for subscribing to a tier.

        Returns the Checkout Session URL to redirect the user to.
        """
        price_id = get_price_id(tier, billing_period)
        if not price_id:
            raise ValueError(f"No Stripe price configured for tier={tier}, period={billing_period}")

        # Look up or create Stripe Customer
        customer_id = await self._get_or_create_customer(user_id, user_email)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode='subscription',
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': user_id,
                'tier': tier,
            },
            subscription_data={
                'metadata': {
                    'user_id': user_id,
                    'tier': tier,
                },
            },
        )

        return session.url

    async def create_portal_session(self, user_id: str, return_url: str) -> str:
        """
        Create a Stripe Customer Portal session for managing a subscription.

        Returns the Portal Session URL to redirect the user to.
        """
        # Look up stripe_customer_id from user_profiles
        profile = self._get_user_profile(user_id)
        customer_id = profile.get('stripe_customer_id') if profile else None

        if not customer_id:
            raise ValueError("No Stripe customer found for this user. Subscribe first.")

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return session.url

    async def handle_webhook_event(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify and handle a Stripe webhook event.

        Returns a dict with the event type and processing result.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid webhook signature")

        event_type = event['type']
        data = event['data']['object']

        logger.info(f"Stripe webhook received: {event_type}")

        if event_type == 'checkout.session.completed':
            await self._handle_checkout_completed(data)
        elif event_type == 'customer.subscription.updated':
            await self._handle_subscription_updated(data)
        elif event_type == 'customer.subscription.deleted':
            await self._handle_subscription_deleted(data)
        elif event_type == 'invoice.payment_failed':
            await self._handle_payment_failed(data)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")

        return {'event_type': event_type, 'status': 'processed'}

    # -------------------------------------------------------------------------
    # Webhook event handlers
    # -------------------------------------------------------------------------

    async def _handle_checkout_completed(self, session: Dict[str, Any]) -> None:
        """Handle checkout.session.completed — activate the subscription."""
        user_id = session.get('metadata', {}).get('user_id')
        if not user_id:
            logger.error("checkout.session.completed missing user_id in metadata")
            return

        subscription_id = session.get('subscription')
        customer_id = session.get('customer')

        if not subscription_id:
            logger.error("checkout.session.completed missing subscription ID")
            return

        # Retrieve the subscription to get the price and period end
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['items']['data'][0]['price']['id']
        tier = tier_from_price_id(price_id)

        if not tier:
            logger.error(f"Unknown price_id from subscription: {price_id}")
            return

        current_period_end = datetime.fromtimestamp(
            subscription['current_period_end'], tz=timezone.utc
        ).isoformat()

        # Update user_profiles
        self.supabase.table('user_profiles').update({
            'tier': tier,
            'stripe_customer_id': customer_id,
            'stripe_subscription_id': subscription_id,
            'subscription_status': 'active',
            'current_period_end': current_period_end,
        }).eq('id', user_id).execute()

        logger.info(f"User {user_id} subscribed to {tier} (subscription={subscription_id})")

    async def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> None:
        """Handle customer.subscription.updated — upgrade, downgrade, or status change."""
        user_id = subscription.get('metadata', {}).get('user_id')
        if not user_id:
            logger.error("subscription.updated missing user_id in metadata")
            return

        price_id = subscription['items']['data'][0]['price']['id']
        tier = tier_from_price_id(price_id)

        if not tier:
            logger.error(f"Unknown price_id in subscription.updated: {price_id}")
            return

        status = subscription.get('status', 'active')
        # Map Stripe statuses to our simplified set
        status_map = {
            'active': 'active',
            'past_due': 'past_due',
            'canceled': 'canceled',
            'trialing': 'trialing',
            'incomplete': 'past_due',
            'incomplete_expired': 'canceled',
            'unpaid': 'past_due',
        }
        mapped_status = status_map.get(status, 'active')

        current_period_end = datetime.fromtimestamp(
            subscription['current_period_end'], tz=timezone.utc
        ).isoformat()

        update_data = {
            'tier': tier,
            'subscription_status': mapped_status,
            'current_period_end': current_period_end,
        }

        self.supabase.table('user_profiles').update(
            update_data
        ).eq('id', user_id).execute()

        logger.info(f"User {user_id} subscription updated: tier={tier}, status={mapped_status}")

    async def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> None:
        """Handle customer.subscription.deleted — downgrade to Preview."""
        user_id = subscription.get('metadata', {}).get('user_id')
        if not user_id:
            logger.error("subscription.deleted missing user_id in metadata")
            return

        self.supabase.table('user_profiles').update({
            'tier': 'sourcer',
            'subscription_status': 'canceled',
            'stripe_subscription_id': None,
            'current_period_end': None,
        }).eq('id', user_id).execute()

        logger.info(f"User {user_id} subscription deleted — downgraded to sourcer (free tier)")

    async def _handle_payment_failed(self, invoice: Dict[str, Any]) -> None:
        """Handle invoice.payment_failed — mark subscription as past_due."""
        customer_id = invoice.get('customer')
        if not customer_id:
            logger.error("invoice.payment_failed missing customer ID")
            return

        # Look up user by stripe_customer_id
        try:
            response = self.supabase.table('user_profiles').select('id').eq(
                'stripe_customer_id', customer_id
            ).single().execute()
            user_id = response.data['id']
        except Exception:
            logger.error(f"Could not find user for customer {customer_id}")
            return

        self.supabase.table('user_profiles').update({
            'subscription_status': 'past_due',
        }).eq('id', user_id).execute()

        logger.info(f"User {user_id} payment failed — marked as past_due")

    # -------------------------------------------------------------------------
    # Helper methods
    # -------------------------------------------------------------------------

    async def _get_or_create_customer(self, user_id: str, email: str) -> str:
        """Get existing Stripe Customer ID or create a new one."""
        profile = self._get_user_profile(user_id)
        customer_id = profile.get('stripe_customer_id') if profile else None

        if customer_id:
            return customer_id

        # Create new Stripe Customer
        customer = stripe.Customer.create(
            email=email,
            metadata={'user_id': user_id},
        )

        # Save to user_profiles
        self.supabase.table('user_profiles').update({
            'stripe_customer_id': customer.id,
        }).eq('id', user_id).execute()

        return customer.id

    def _get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from database."""
        try:
            response = self.supabase.table('user_profiles').select('*').eq(
                'id', user_id
            ).single().execute()
            return response.data
        except Exception:
            return None
