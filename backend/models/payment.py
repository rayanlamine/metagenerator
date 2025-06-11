"""
Payment models for Dodo Payments integration
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    FAILED = "failed"
    CANCELED = "canceled"

class BillingAddress(BaseModel):
    street: str
    city: str
    state: str
    country: str
    zipcode: str

class PaymentCustomer(BaseModel):
    customer_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None

class ProductItem(BaseModel):
    product_id: str
    amount: int  # Amount in cents
    quantity: int = 1

class CreatePaymentRequest(BaseModel):
    billing_currency: str = "USD"
    allowed_payment_method_types: List[str] = ["credit", "debit"]
    product_cart: List[ProductItem]
    return_url: str
    customer: Optional[PaymentCustomer] = None
    billing: Optional[BillingAddress] = None
    metadata: Optional[Dict[str, Any]] = None

class PaymentResponse(BaseModel):
    id: str
    url: str
    checkout_url: Optional[str] = None
    status: str
    expires_at: Optional[str] = None

class CreateSubscriptionRequest(BaseModel):
    customer: PaymentCustomer
    product_id: str
    billing: BillingAddress
    payment_link: bool = True
    subscription_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SubscriptionResponse(BaseModel):
    subscription_id: str
    customer_id: str
    status: str
    product_id: str
    payment_url: Optional[str] = None

class WebhookEvent(BaseModel):
    business_id: str
    timestamp: str
    type: str
    data: Dict[str, Any]

class PaymentRecord(BaseModel):
    id: str = Field(alias="_id")
    payment_id: str
    user_id: Optional[str] = None
    customer_id: Optional[str] = None
    amount: int
    currency: str
    status: PaymentStatus
    product_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class SubscriptionRecord(BaseModel):
    id: str = Field(alias="_id")
    subscription_id: str
    user_id: Optional[str] = None
    customer_id: str
    product_id: str
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
