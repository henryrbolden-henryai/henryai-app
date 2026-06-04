"""
Stripe Service for HenryHQ

Handles Stripe Checkout sessions, Customer Portal sessions, and webhook events
for subscription billing.
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import stripe
from supabase import Client

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
RESEND_API_URL = "https://api.resend.com/emails"

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
        return_url: str,
        promotion_code: str | None = None,
    ) -> str:
        """
        Create a Stripe Checkout Session in embedded mode.

        Returns the client_secret needed to mount the embedded checkout form.
        """
        price_id = get_price_id(tier, billing_period)
        if not price_id:
            raise ValueError(f"No Stripe price configured for tier={tier}, period={billing_period}")

        # Look up or create Stripe Customer
        customer_id = await self._get_or_create_customer(user_id, user_email)

        # Build session params
        session_params = dict(
            customer=customer_id,
            mode='subscription',
            ui_mode='embedded_page',
            payment_method_types=['card'],
            billing_address_collection='required',
            customer_update={'name': 'auto', 'address': 'auto'},
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            return_url=return_url,
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

        # If a promotion code was provided, look it up and apply it
        if promotion_code:
            promo_codes = stripe.PromotionCode.list(code=promotion_code, active=True, limit=1)
            if promo_codes.data:
                session_params['discounts'] = [{'promotion_code': promo_codes.data[0].id}]
            else:
                raise ValueError(f"Invalid promotion code: {promotion_code}")
        else:
            # Allow manual entry in Stripe's UI
            session_params['allow_promotion_codes'] = True

        session = stripe.checkout.Session.create(**session_params)

        return session.client_secret

    def get_checkout_session_status(self, session_id: str) -> dict:
        """Retrieve a Checkout Session's status for the return page."""
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'status': session.status,
            'payment_status': session.payment_status,
            'customer_email': session.customer_details.email if session.customer_details else None,
        }

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
        # Verify signature
        try:
            stripe.Webhook.construct_event(
                payload, sig_header, WEBHOOK_SECRET
            )
        except Exception as e:
            raise ValueError(f"Invalid webhook signature: {str(e)}")

        # Parse the raw payload as plain JSON (no Stripe SDK objects)
        event_json = json.loads(payload)
        event_type = event_json['type']
        data = event_json['data']['object']

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
    # Email
    # -------------------------------------------------------------------------

    def _send_welcome_email(self, email: str, first_name: str, tier: str) -> None:
        """Send a welcome email after successful subscription."""
        if not RESEND_API_KEY:
            logger.warning("RESEND_API_KEY not configured — skipping welcome email")
            return

        html = f"""
        <div style="font-family: Georgia, 'Times New Roman', serif; max-width: 560px; margin: 0 auto; padding: 40px 20px; color: #2a2a2a;">

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                Hi {first_name},
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                I'm glad you're here.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                If you're searching for a job right now, you're doing it in a market that feels very different than it did just a few years ago. The hiring process is changing fast. AI is everywhere. New tools seem to appear every week. And for many job seekers, it feels like nobody stopped to explain the new rules.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                The rejection emails that pile up. The interviews that go silent. The pressure to stay positive when you're not sure what next month looks like. I hear these things every day, and I want you to know: you're not crazy. You're not behind. And you're not alone in feeling this way.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                I built HenryHQ because I believe the hardest part of a job search isn't finding opportunities. It's knowing where to focus your energy, how to position yourself, and when to push forward versus when to change direction. Most people don't need to apply to more jobs. They need to make better moves.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px; font-style: italic; border-left: 3px solid #22d3ee; padding-left: 16px;">
                The goal isn't to help you submit more applications. The goal is to help you make better moves.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                That means knowing which roles are actually worth your time. Showing up to interviews with real preparation, not generic talking points. Keeping your search organized when everything feels chaotic. And having someone in your corner who'll give you honest feedback, not empty encouragement.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                Some days you'll feel motivated. Some days you'll wonder if any of this is working. That's normal. A job search is one of the most emotionally demanding things a person can go through, and nobody talks about that enough.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                On the hard days, don't try to solve everything at once. Come back. Talk to Hey Henry. Review your plan. Take one small step forward. That's enough for today.
            </p>

            <div style="margin: 32px 0;">
                <a href="https://henryhq.ai/professionals/profile/edit" style="display: inline-block; padding: 14px 28px; background: #22d3ee; color: #000; border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 0.95rem; font-family: -apple-system, sans-serif;">
                    Set Up Your Profile
                </a>
            </div>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 20px;">
                If you need help, have feedback, or just want to talk through your search, reply to this email or reach me directly at <a href="mailto:support@henryhq.ai" style="color: #22d3ee; text-decoration: none;">support@henryhq.ai</a>. I read every message personally.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 28px;">
                If you'd prefer dedicated coaching, you can book time with me here: <a href="https://calendly.com/hb-henryhq/45min" style="color: #22d3ee; text-decoration: none;">calendly.com/hb-henryhq</a>.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #3a3a3a; margin-bottom: 4px;">
                I'm rooting for you.
            </p>

            <p style="font-size: 1.05rem; line-height: 1.8; color: #2a2a2a; margin-top: 4px;">
                Henry
            </p>

            <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 32px 0 16px;">

            <p style="font-size: 0.8rem; color: #9a9aaa; line-height: 1.5; font-family: -apple-system, sans-serif;">
                HenryHQ.ai
            </p>
        </div>
        """

        payload = {
            "from": "Henry <support@henryhq.ai>",
            "to": email,
            "subject": f"{first_name}, welcome.",
            "html": html,
            "reply_to": "support@henryhq.ai",
        }

        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            logger.info(f"Welcome email sent to {email}")
        else:
            logger.error(f"Welcome email failed: {response.status_code} - {response.text}")

    # -------------------------------------------------------------------------
    # Webhook event handlers
    # -------------------------------------------------------------------------

    async def _handle_checkout_completed(self, session: Dict[str, Any]) -> None:
        """Handle checkout.session.completed — activate the subscription."""
        logger.info(f"Processing checkout completed. Session keys: {list(session.keys()) if isinstance(session, dict) else type(session)}")

        user_id = session.get('metadata', {}).get('user_id')
        if not user_id:
            logger.error(f"checkout.session.completed missing user_id in metadata. Metadata: {session.get('metadata')}")
            return

        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        logger.info(f"Checkout: user_id={user_id}, subscription_id={subscription_id}, customer_id={customer_id}")

        if not subscription_id:
            logger.error("checkout.session.completed missing subscription ID")
            return

        # Retrieve the subscription to get the price and period end
        sub_obj = stripe.Subscription.retrieve(subscription_id)
        subscription = json.loads(str(sub_obj))
        logger.info(f"Retrieved subscription: {subscription['id']}")
        price_id = subscription['items']['data'][0]['price']['id']
        tier = tier_from_price_id(price_id)
        logger.info(f"Price ID: {price_id}, Tier: {tier}")

        if not tier:
            logger.error(f"Unknown price_id from subscription: {price_id}")
            return

        # Get period end — field location varies by API version
        period_end_ts = subscription.get('current_period_end')
        if not period_end_ts:
            # Try items-level period end
            period_end_ts = subscription.get('items', {}).get('data', [{}])[0].get('current_period_end')

        current_period_end = None
        if period_end_ts:
            current_period_end = datetime.fromtimestamp(
                period_end_ts, tz=timezone.utc
            ).isoformat()

        logger.info(f"Updating user {user_id}: tier={tier}, period_end={current_period_end}")

        # Check if this is a new user (no existing subscription) before updating
        existing = self._get_user_profile(user_id)
        is_new_subscriber = not existing or not existing.get('stripe_subscription_id')

        # Update user_profiles
        update_data = {
            'tier': tier,
            'stripe_customer_id': customer_id,
            'stripe_subscription_id': subscription_id,
            'subscription_status': 'active',
        }
        if current_period_end:
            update_data['current_period_end'] = current_period_end

        self.supabase.table('user_profiles').update(update_data).eq('id', user_id).execute()

        logger.info(f"User {user_id} subscribed to {tier} (subscription={subscription_id})")

        # Send welcome email only for new subscribers (not upgrades)
        if is_new_subscriber:
            try:
                user_email = session.get('customer_details', {}).get('email') or session.get('customer_email')
                user_name = session.get('customer_details', {}).get('name', '').split(' ')[0] or 'there'
                if user_email:
                    self._send_welcome_email(user_email, user_name, tier)
            except Exception as e:
                logger.error(f"Welcome email failed (non-blocking): {str(e)}")
        else:
            logger.info(f"Skipping welcome email — user {user_id} is upgrading, not new")

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
