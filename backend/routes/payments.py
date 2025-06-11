"""
Payment API routes for Dodo Payments integration
"""
import logging
import hmac
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from models.payment import (
    CreatePaymentRequest, PaymentResponse, CreateSubscriptionRequest,
    SubscriptionResponse, WebhookEvent, PaymentStatus, SubscriptionStatus
)
from services.dodo_payments import DodoPaymentsService
from database import get_database_collections

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])

async def get_dodo_service() -> DodoPaymentsService:
    """Dependency to get Dodo Payments service"""
    collections = await get_database_collections()
    return DodoPaymentsService(collections)

@router.post("/checkout", response_model=PaymentResponse)
async def create_payment_checkout(
    payment_request: CreatePaymentRequest,
    request: Request,
    dodo_service: DodoPaymentsService = Depends(get_dodo_service)
):
    """Create a checkout session for one-time payment"""
    try:
        # You can extract user_id from auth token here if needed
        user_id = getattr(request.state, 'user_id', None)
        
        payment_response = await dodo_service.create_payment(payment_request, user_id)
        return payment_response
        
    except Exception as e:
        logger.error(f"Error creating payment checkout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment checkout: {str(e)}"
        )

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_request: CreateSubscriptionRequest,
    request: Request,
    dodo_service: DodoPaymentsService = Depends(get_dodo_service)
):
    """Create a subscription"""
    try:
        # You can extract user_id from auth token here if needed
        user_id = getattr(request.state, 'user_id', None)
        
        subscription_response = await dodo_service.create_subscription(subscription_request, user_id)
        return subscription_response
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.get("/payments/{payment_id}")
async def get_payment(
    payment_id: str,
    dodo_service: DodoPaymentsService = Depends(get_dodo_service)
):
    """Get payment details by ID"""
    try:
        payment = await dodo_service.get_payment(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )

@router.post("/webhooks/dodo")
async def handle_dodo_webhook(
    request: Request,
    dodo_service: DodoPaymentsService = Depends(get_dodo_service)
):
    """Handle Dodo Payments webhook events"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get webhook headers
        webhook_signature = request.headers.get("webhook-signature")
        webhook_id = request.headers.get("webhook-id")
        webhook_timestamp = request.headers.get("webhook-timestamp")
        
        if not webhook_signature or not webhook_id or not webhook_timestamp:
            logger.error("Missing webhook signature headers")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing webhook signature headers"
            )
        
        # Verify webhook signature
        if not verify_webhook_signature(body, webhook_signature, webhook_id, webhook_timestamp, dodo_service.webhook_secret):
            logger.error("Invalid webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse webhook event
        event_data = json.loads(body.decode())
        event = WebhookEvent(**event_data)
        
        # Process webhook event
        await process_webhook_event(event, dodo_service)
        
        return JSONResponse(content={"status": "success"}, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )

def verify_webhook_signature(
    body: bytes, 
    signature: str, 
    webhook_id: str, 
    timestamp: str, 
    secret: str
) -> bool:
    """Verify Dodo Payments webhook signature"""
    try:
        # Create string to sign
        string_to_sign = f"{webhook_id}.{timestamp}.{body.decode()}"
        
        # Compute HMAC with SHA256
        computed_signature = hmac.new(
            secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures using constant-time comparison
        return hmac.compare_digest(signature, computed_signature)
        
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

async def process_webhook_event(event: WebhookEvent, dodo_service: DodoPaymentsService):
    """Process different types of webhook events"""
    try:
        logger.info(f"Processing webhook event: {event.type}")
        
        if event.type == "payment.succeeded":
            await handle_payment_succeeded(event.data, dodo_service)
        elif event.type == "payment.failed":
            await handle_payment_failed(event.data, dodo_service)
        elif event.type == "subscription.active":
            await handle_subscription_active(event.data, dodo_service)
        elif event.type == "subscription.on_hold":
            await handle_subscription_on_hold(event.data, dodo_service)
        elif event.type == "subscription.failed":
            await handle_subscription_failed(event.data, dodo_service)
        elif event.type == "subscription.renewed":
            await handle_subscription_renewed(event.data, dodo_service)
        elif event.type == "subscription.plan_changed":
            await handle_subscription_plan_changed(event.data, dodo_service)
        else:
            logger.warning(f"Unhandled webhook event type: {event.type}")
        
    except Exception as e:
        logger.error(f"Error processing webhook event {event.type}: {str(e)}")
        raise

async def handle_payment_succeeded(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle successful payment"""
    payment_id = data.get("payment_id")
    if payment_id:
        await dodo_service.update_payment_status(
            payment_id, 
            PaymentStatus.SUCCESS,
            {"webhook_data": data}
        )
        logger.info(f"Payment {payment_id} marked as successful")

async def handle_payment_failed(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle failed payment"""
    payment_id = data.get("payment_id")
    if payment_id:
        await dodo_service.update_payment_status(
            payment_id, 
            PaymentStatus.FAILED,
            {"webhook_data": data, "error": data.get("error")}
        )
        logger.info(f"Payment {payment_id} marked as failed")

async def handle_subscription_active(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle subscription activation"""
    subscription_id = data.get("subscription_id")
    if subscription_id:
        await dodo_service.update_subscription_status(
            subscription_id,
            SubscriptionStatus.ACTIVE,
            {"webhook_data": data, "current_period_end": data.get("current_period_end")}
        )
        logger.info(f"Subscription {subscription_id} activated")

async def handle_subscription_on_hold(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle subscription on hold"""
    subscription_id = data.get("subscription_id")
    if subscription_id:
        await dodo_service.update_subscription_status(
            subscription_id,
            SubscriptionStatus.ON_HOLD,
            {"webhook_data": data}
        )
        logger.info(f"Subscription {subscription_id} on hold")

async def handle_subscription_failed(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle subscription failure"""
    subscription_id = data.get("subscription_id")
    if subscription_id:
        await dodo_service.update_subscription_status(
            subscription_id,
            SubscriptionStatus.FAILED,
            {"webhook_data": data}
        )
        logger.info(f"Subscription {subscription_id} failed")

async def handle_subscription_renewed(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle subscription renewal"""
    subscription_id = data.get("subscription_id")
    if subscription_id:
        await dodo_service.update_subscription_status(
            subscription_id,
            SubscriptionStatus.ACTIVE,
            {"webhook_data": data, "current_period_end": data.get("current_period_end")}
        )
        logger.info(f"Subscription {subscription_id} renewed")

async def handle_subscription_plan_changed(data: Dict[str, Any], dodo_service: DodoPaymentsService):
    """Handle subscription plan change"""
    subscription_id = data.get("subscription_id")
    if subscription_id:
        await dodo_service.update_subscription_status(
            subscription_id,
            SubscriptionStatus.ACTIVE,
            {
                "webhook_data": data,
                "previous_plan": data.get("previous_plan"),
                "new_plan": data.get("new_plan"),
                "current_period_end": data.get("current_period_end")
            }
        )
        logger.info(f"Subscription {subscription_id} plan changed")

# Test endpoint for payment functionality
@router.post("/test/simple-payment")
async def test_simple_payment(
    request: Request,
    dodo_service: DodoPaymentsService = Depends(get_dodo_service)
):
    """Test endpoint for simple payment creation"""
    try:
        # Create a simple test payment
        test_payment = CreatePaymentRequest(
            billing_currency="USD",
            product_cart=[{
                "product_id": "test_product",
                "amount": 1000,  # $10.00 in cents
                "quantity": 1
            }],
            return_url="http://localhost:3000/payment-success",
            metadata={"test": True, "source": "api_test"}
        )
        
        payment_response = await dodo_service.create_payment(test_payment)
        return payment_response
        
    except Exception as e:
        logger.error(f"Error in test payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test payment failed: {str(e)}"
        )
