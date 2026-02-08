"""
Payment API Routes
Handles Stripe payment integration for subscriptions
"""

import logging
import os
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Dict, Any

import stripe

from models.schemas import (
    CreateCheckoutRequest,
    PaymentCheckoutResponse,
    PaymentConfirmRequest,
    PaymentConfirmResponse
)
from middleware.auth import get_current_user_id
from data.user_manager import user_manager
from auth.environment_loader import env_loader
from spotify.baseline_calculator import baseline_calculator

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/payment", tags=["Payment"])

# Load Stripe configuration from Parameter Store
# Using default user 'tresch' for app-level Stripe config
stripe_config = env_loader.get_stripe_config()
stripe.api_key = stripe_config.get('secret_key')

# Stripe price IDs for each tier (from Parameter Store)
STRIPE_PRICES = {
    'talent': stripe_config.get('price_talent'),
    'star': stripe_config.get('price_star'),
    'legend': stripe_config.get('price_legend')
}

# Frontend URL for Stripe redirects
# Default to localhost for development
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')


@router.post("/create-checkout", response_model=PaymentCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> PaymentCheckoutResponse:
    """
    Create Stripe checkout session for subscription payment.

    Returns session ID and checkout URL to redirect user to.
    """
    try:
        # Verify user is creating checkout for themselves
        if request.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create checkout for other users"
            )

        logger.info(f"Creating Stripe checkout session for user {request.user_id}, tier: {request.tier}")

        # Get price ID for tier
        price_id = STRIPE_PRICES.get(request.tier)
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {request.tier}"
            )

        # Get user profile for email
        user_profile = user_manager.get_user_profile(request.user_id)
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        customer_email = user_profile.get('email', '')

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=customer_email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&user_id={request.user_id}',
            cancel_url=f'{FRONTEND_URL}/pricing',
            metadata={
                'user_id': request.user_id,
                'tier': request.tier
            },
            subscription_data={
                'metadata': {
                    'user_id': request.user_id,
                    'tier': request.tier
                }
            }
        )

        logger.info(f"Checkout session created: {checkout_session.id}")

        return PaymentCheckoutResponse(
            session_id=checkout_session.id,
            checkout_url=checkout_session.url
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.post("/confirm", response_model=PaymentConfirmResponse)
async def confirm_payment(
    request: PaymentConfirmRequest
) -> PaymentConfirmResponse:
    """
    Confirm payment completion after Stripe checkout.

    Verifies payment was successful and updates user subscription.
    """
    try:
        logger.info(f"Confirming payment for session: {request.session_id}")

        # Retrieve checkout session from Stripe
        session = stripe.checkout.Session.retrieve(request.session_id)

        if session.payment_status != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not completed"
            )

        # Get user_id and tier from metadata
        user_id = session.metadata.get('user_id')
        tier = session.metadata.get('tier')

        # User is verified via Stripe session metadata - no JWT needed

        # Update user subscription tier
        success = user_manager.update_subscription_tier(user_id, tier)

        if not success:
            logger.error(f"Failed to update subscription for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update subscription"
            )

        # Set account_status to 'active' now that payment is confirmed
        user_manager.update_user_profile(user_id, {'account_status': 'active'})
        logger.info(f"Payment confirmed, subscription and account_status updated for user {user_id}")

        # Trigger first_payment milestone (enables video to play)
        user_manager.achieve_milestone(user_id, 'first_payment')
        logger.info(f"First payment milestone achieved for user {user_id}")

        # Calculate user's baseline popularity from Spotify catalog
        try:
            baseline_profile = user_manager.get_user_profile(user_id)
            artist_id = baseline_profile.get('spotify_artist_id') if baseline_profile else None
            if artist_id and not baseline_profile.get('current_baseline'):
                baseline_calculator.calculate_baseline(user_id, artist_id)
                logger.info(f"Baseline calculated for user {user_id}")
            elif artist_id:
                logger.info(f"Baseline already exists for user {user_id}, skipping")
            else:
                logger.warning(f"No spotify_artist_id for user {user_id}, skipping baseline")
        except Exception as e:
            logger.error(f"Baseline calculation failed for {user_id}: {e}")

        # Move onboarding to next step (platforms selection)
        user_manager.update_onboarding_status(user_id, 'platforms_pending')
        logger.info(f"Onboarding status updated to platforms_pending for user {user_id}")

        # Generate new JWT token in case it was lost during Stripe redirect
        from middleware.auth import create_jwt_token
        token = create_jwt_token(user_id)

        return PaymentConfirmResponse(
            success=True,
            message=f"Subscription activated: {tier} tier",
            token=token
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error confirming payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm payment"
        )


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks for subscription events.

    Processes events like payment succeeded, subscription canceled, etc.
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        webhook_secret = stripe_config.get('webhook_secret')

        if not webhook_secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload), stripe.api_key
            )
        else:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Invalid webhook signature: {e}")
                raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle different event types
        event_type = event['type']
        logger.info(f"Received Stripe webhook: {event_type}")

        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get('metadata', {}).get('user_id')
            tier = session.get('metadata', {}).get('tier')

            if user_id and tier:
                # Update subscription tier and set account to active
                user_manager.update_subscription_tier(user_id, tier)
                user_manager.update_user_profile(user_id, {'account_status': 'active'})
                logger.info(f"Subscription activated for user {user_id}: {tier}, account_status: active")

                # Trigger first_payment milestone
                try:
                    user_manager.achieve_milestone(user_id, 'first_payment')
                    logger.info(f"Webhook: first_payment milestone achieved for user {user_id}")
                except Exception as e:
                    logger.error(f"Webhook: milestone failed for {user_id}: {e}")

                # Calculate baseline popularity (with idempotency guard)
                try:
                    webhook_profile = user_manager.get_user_profile(user_id)
                    artist_id = webhook_profile.get('spotify_artist_id') if webhook_profile else None
                    if artist_id and not webhook_profile.get('current_baseline'):
                        baseline_calculator.calculate_baseline(user_id, artist_id)
                        logger.info(f"Webhook: baseline calculated for user {user_id}")
                    elif artist_id:
                        logger.info(f"Webhook: baseline already exists for user {user_id}, skipping")
                except Exception as e:
                    logger.error(f"Webhook: baseline failed for {user_id}: {e}")

                # Advance onboarding
                try:
                    user_manager.update_onboarding_status(user_id, 'platforms_pending')
                    logger.info(f"Webhook: onboarding updated to platforms_pending for user {user_id}")
                except Exception as e:
                    logger.error(f"Webhook: onboarding update failed for {user_id}: {e}")

        elif event_type == 'customer.subscription.deleted':
            subscription = event['data']['object']
            user_id = subscription.get('metadata', {}).get('user_id')

            if user_id:
                # Set account to pending (subscription canceled)
                user_manager.update_user_profile(user_id, {'account_status': 'pending'})
                user_manager.deactivate_user_account(user_id, reason='subscription_canceled')
                logger.info(f"Subscription canceled for user {user_id}, account_status: pending")

        elif event_type == 'invoice.payment_failed':
            invoice = event['data']['object']
            # Try to get user_id from subscription metadata
            subscription_id = invoice.get('subscription')
            if subscription_id:
                try:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    user_id = subscription.get('metadata', {}).get('user_id')
                    if user_id:
                        # Set account to pending due to failed payment
                        user_manager.update_user_profile(user_id, {'account_status': 'pending'})
                        logger.warning(f"Payment failed for user {user_id}, account_status: pending")
                except Exception as e:
                    logger.warning(f"Could not retrieve subscription for failed invoice: {e}")
            logger.warning(f"Payment failed for invoice: {invoice.get('id')}")

        return {"received": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )
