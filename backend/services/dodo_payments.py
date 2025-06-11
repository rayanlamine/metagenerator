"""
Dodo Payments service integration
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import dodopayments
from dodopayments import DodoPayments
from motor.motor_asyncio import AsyncIOMotorCollection

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from models.payment import (
    CreatePaymentRequest, PaymentResponse, CreateSubscriptionRequest, 
    SubscriptionResponse, PaymentRecord, SubscriptionRecord, PaymentStatus,
    SubscriptionStatus
)

logger = logging.getLogger(__name__)

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from models.payment import (
    CreatePaymentRequest, PaymentResponse, CreateSubscriptionRequest, 
    SubscriptionResponse, PaymentRecord, SubscriptionRecord, PaymentStatus,
    SubscriptionStatus
)

logger = logging.getLogger(__name__)

class DodoPaymentsService:
    def __init__(self, db_collections: Dict[str, AsyncIOMotorCollection]):
        self.api_key = os.getenv("DODO_PAYMENTS_API_KEY")
        self.webhook_secret = os.getenv("DODO_PAYMENTS_WEBHOOK_SECRET")
        self.mode = os.getenv("DODO_PAYMENTS_MODE", "test")
        
        if not self.api_key:
            raise ValueError("DODO_PAYMENTS_API_KEY environment variable is required")
        
        # Initialize Dodo Payments client
        self.client = DodoPayments(
            bearer_token=self.api_key,
        )
        
        # Database collections
        self.payments_collection = db_collections.get("payments")
        self.subscriptions_collection = db_collections.get("subscriptions")
        
    async def create_payment(
        self, 
        payment_request: CreatePaymentRequest,
        user_id: Optional[str] = None
    ) -> PaymentResponse:
        """Create a one-time payment"""
        try:
            # Format request for Dodo Payments API
            payment_data = {
                "billing_currency": payment_request.billing_currency,
                "allowed_payment_method_types": payment_request.allowed_payment_method_types,
                "product_cart": [
                    {
                        "amount": item.amount,
                        "product_id": item.product_id,
                        "quantity": item.quantity
                    }
                    for item in payment_request.product_cart
                ],
                "return_url": payment_request.return_url,
                "payment_link": True,
                "metadata": payment_request.metadata or {}
            }
            
            # Add customer if provided
            if payment_request.customer:
                customer_data = {}
                if payment_request.customer.customer_id:
                    customer_data["customer_id"] = payment_request.customer.customer_id
                if payment_request.customer.email:
                    customer_data["email"] = payment_request.customer.email
                if payment_request.customer.name:
                    customer_data["name"] = payment_request.customer.name
                
                if customer_data:
                    payment_data["customer"] = customer_data
            
            # Add billing address if provided
            if payment_request.billing:
                payment_data["billing"] = {
                    "street": payment_request.billing.street,
                    "city": payment_request.billing.city,
                    "state": payment_request.billing.state,
                    "country": payment_request.billing.country,
                    "zipcode": payment_request.billing.zipcode
                }
            
            # Create payment with Dodo Payments
            print(f"Attempting to create payment with Dodo Payments API. API Key: {self.api_key[:5]}...")
            try:
                response = self.client.payments.create(**payment_data)
                print(f"Successfully created payment with Dodo Payments API: {response.id}")
            except Exception as api_error:
                print(f"Error calling Dodo Payments API: {str(api_error)}")
                raise
            
            # Save payment record to database
            if self.payments_collection:
                payment_record = PaymentRecord(
                    id=response.id,
                    payment_id=response.id,
                    user_id=user_id,
                    customer_id=payment_request.customer.customer_id if payment_request.customer else None,
                    amount=sum(item.amount for item in payment_request.product_cart),
                    currency=payment_request.billing_currency,
                    status=PaymentStatus.PENDING,
                    product_id=payment_request.product_cart[0].product_id if payment_request.product_cart else None,
                    metadata=payment_request.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                await self.payments_collection.insert_one(payment_record.dict(by_alias=True))
            
            return PaymentResponse(
                id=response.id,
                url=response.url,
                checkout_url=getattr(response, 'checkout_url', response.url),
                status=response.status,
                expires_at=getattr(response, 'expires_at', None)
            )
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            # In test mode, return a mock response if API fails
            if self.mode == "test":
                mock_id = f"mock_payment_{int(datetime.utcnow().timestamp())}"
                return PaymentResponse(
                    id=mock_id,
                    url=f"https://checkout.dodopayments.com/mock/{mock_id}",
                    status="pending",
                    expires_at=datetime.utcnow().isoformat()
                )
            raise
    
    async def create_subscription(
        self,
        subscription_request: CreateSubscriptionRequest,
        user_id: Optional[str] = None
    ) -> SubscriptionResponse:
        """Create a recurring subscription"""
        try:
            # Format request for Dodo Payments API
            subscription_data = {
                "customer": {
                    "customer_id": subscription_request.customer.customer_id,
                    "email": subscription_request.customer.email,
                    "name": subscription_request.customer.name
                },
                "product_id": subscription_request.product_id,
                "billing": {
                    "street": subscription_request.billing.street,
                    "city": subscription_request.billing.city,
                    "state": subscription_request.billing.state,
                    "country": subscription_request.billing.country,
                    "zipcode": subscription_request.billing.zipcode
                },
                "payment_link": subscription_request.payment_link,
                "metadata": subscription_request.metadata or {}
            }
            
            if subscription_request.subscription_id:
                subscription_data["subscription_id"] = subscription_request.subscription_id
            
            # Create subscription with Dodo Payments
            response = self.client.subscriptions.create(**subscription_data)
            
            # Save subscription record to database
            if self.subscriptions_collection:
                subscription_record = SubscriptionRecord(
                    id=response.subscription_id,
                    subscription_id=response.subscription_id,
                    user_id=user_id,
                    customer_id=subscription_request.customer.customer_id,
                    product_id=subscription_request.product_id,
                    status=SubscriptionStatus.PENDING if hasattr(SubscriptionStatus, 'PENDING') else SubscriptionStatus.ACTIVE,
                    metadata=subscription_request.metadata,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                await self.subscriptions_collection.insert_one(subscription_record.dict(by_alias=True))
            
            return SubscriptionResponse(
                subscription_id=response.subscription_id,
                customer_id=subscription_request.customer.customer_id,
                status=response.status,
                product_id=subscription_request.product_id,
                payment_url=getattr(response, 'payment_url', None)
            )
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            # In test mode, return a mock response if API fails
            if self.mode == "test":
                mock_id = f"mock_subscription_{int(datetime.utcnow().timestamp())}"
                return SubscriptionResponse(
                    subscription_id=mock_id,
                    customer_id=subscription_request.customer.customer_id,
                    status="active",
                    product_id=subscription_request.product_id,
                    payment_url=f"https://checkout.dodopayments.com/mock/{mock_id}"
                )
            raise
    
    async def get_payment(self, payment_id: str) -> Optional[PaymentRecord]:
        """Get payment by ID"""
        if not self.payments_collection:
            return None
            
        payment_data = await self.payments_collection.find_one({"payment_id": payment_id})
        if payment_data:
            return PaymentRecord(**payment_data)
        return None
    
    async def update_payment_status(
        self, 
        payment_id: str, 
        status: PaymentStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update payment status"""
        if not self.payments_collection:
            return False
            
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if metadata:
            update_data["metadata"] = metadata
        
        result = await self.payments_collection.update_one(
            {"payment_id": payment_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def update_subscription_status(
        self,
        subscription_id: str,
        status: SubscriptionStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update subscription status"""
        if not self.subscriptions_collection:
            return False
            
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if metadata:
            update_data["metadata"] = metadata
        
        result = await self.subscriptions_collection.update_one(
            {"subscription_id": subscription_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
