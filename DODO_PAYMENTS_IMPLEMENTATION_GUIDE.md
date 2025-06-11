# Dodo Payments Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Backend Implementation](#backend-implementation)
5. [Frontend Implementation](#frontend-implementation)
6. [Testing](#testing)
7. [Going Live](#going-live)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)

## Overview

This guide documents the complete implementation of Dodo Payments integration in a FastAPI/React/MongoDB application. The implementation supports both one-time payments and recurring subscriptions with comprehensive test functionality.

### Key Features Implemented
- ✅ One-time payment processing
- ✅ Recurring subscription management
- ✅ Webhook event handling
- ✅ Test mode with test cards
- ✅ Database persistence
- ✅ Error handling and validation
- ✅ Frontend payment UI
- ✅ Health monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   MongoDB       │
│                 │    │   Backend       │    │   Database      │
│  - Payment UI   │◄──►│  - Payment API  │◄──►│  - Payments     │
│  - Test Pages   │    │  - Webhooks     │    │  - Subscriptions│
│  - Success Page │    │  - Services     │    │  - Customers    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         └───────────────────────┼─────────────────┐
                                 │                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │  Dodo Payments  │    │   Webhook       │
                    │     API         │    │   Endpoint      │
                    │                 │    │                 │
                    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### Required API Keys
- **Dodo Payments API Key**: Obtain from [Dodo Payments Dashboard](https://dashboard.dodopayments.com)
- **Webhook Secret**: Required for webhook signature verification
- **MongoDB Connection**: For data persistence

### Development Environment
- Python 3.11+
- Node.js 16+
- MongoDB 4.4+
- FastAPI 0.110+
- React 18+

## Backend Implementation

### 1. Environment Configuration

Create `/app/backend/.env`:
```env
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# Dodo Payments Configuration
DODO_PAYMENTS_API_KEY="your_api_key_here"
DODO_PAYMENTS_WEBHOOK_SECRET="your_webhook_secret_here"
DODO_PAYMENTS_API_URL="https://test.dodopayments.com/"
DODO_PAYMENTS_MODE="test"
```

### 2. Dependencies

Add to `/app/backend/requirements.txt`:
```txt
fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
pymongo==4.5.0
dodopayments>=1.32.0
httpx==0.25.0
python-dotenv>=1.0.1
```

### 3. Core Components

#### Payment Models (`/app/backend/models/payment.py`)
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"

class CreatePaymentRequest(BaseModel):
    billing_currency: str = "USD"
    allowed_payment_method_types: List[str] = ["credit", "debit"]
    product_cart: List[ProductItem]
    return_url: str
    customer: Optional[PaymentCustomer] = None
    billing: Optional[BillingAddress] = None
    metadata: Optional[Dict[str, Any]] = None
```

#### Dodo Payments Service (`/app/backend/services/dodo_payments.py`)
```python
from dodopayments import DodoPayments

class DodoPaymentsService:
    def __init__(self, db_collections: Dict[str, AsyncIOMotorCollection]):
        self.client = DodoPayments(bearer_token=os.getenv("DODO_PAYMENTS_API_KEY"))
        self.payments_collection = db_collections.get("payments")
        
    async def create_payment(self, payment_request: CreatePaymentRequest):
        # Create payment with Dodo Payments API
        response = self.client.payments.create(**payment_data)
        
        # Save to database
        await self.payments_collection.insert_one(payment_record.dict())
        
        return PaymentResponse(
            id=response.id,
            url=response.url,
            status=response.status
        )
```

#### Payment Routes (`/app/backend/routes/payments.py`)
Key endpoints:
- `POST /api/payments/checkout` - Create payment session
- `POST /api/payments/subscriptions` - Create subscription
- `POST /api/webhooks/dodo` - Handle webhook events
- `GET /api/health` - System health check

### 4. Database Setup

#### Collections Created
- `payments` - Payment records
- `subscriptions` - Subscription records
- `customers` - Customer information
- `webhook_events` - Webhook event logs

#### Indexes
```python
# Payment indexes
await db.payments.create_index("payment_id", unique=True)
await db.payments.create_index("user_id")
await db.payments.create_index("status")

# Subscription indexes
await db.subscriptions.create_index("subscription_id", unique=True)
await db.subscriptions.create_index("customer_id")
```

## Frontend Implementation

### 1. Environment Configuration

Add to `/app/frontend/.env`:
```env
REACT_APP_BACKEND_URL=https://your-backend-url.com
REACT_APP_DODO_PAYMENTS_API_KEY=your_api_key_here
REACT_APP_DODO_PAYMENTS_MODE=test
```

### 2. Dependencies

```bash
cd /app/frontend
yarn add dodopayments-checkout axios react-router-dom
```

### 3. Core Components

#### Payment Test Component (`/app/frontend/src/components/DodoPaymentTest.js`)
Features:
- Health status monitoring
- Payment form with configurable amounts
- Test card information display
- API integration with backend
- Real-time results display

#### Payment Flow Components
- `PaymentSuccess.js` - Success page with payment details
- `PaymentCancel.js` - Cancellation page
- Route configuration in `App.js`

## Testing

### Test Mode Setup

#### Test API Keys
- Use test API keys from Dodo Payments Dashboard
- Set `DODO_PAYMENTS_MODE="test"`
- Configure test webhook URL if needed

#### Test Cards
```
Success (Global):     4242 4242 4242 4242
Success (India):      6074 8259 7208 3818
Decline:              4000 0000 0000 0002
3D Secure:           4000 0000 0000 3220
Insufficient Funds:   4000 0000 0000 9995
```

### Backend Testing
Comprehensive test suite created in `backend_test.py`:
- Health check endpoint verification
- Payment creation testing
- Subscription testing
- Error handling validation
- Database connectivity checks

### Frontend Testing
Access the test interface at `/payment-test`:
- System health monitoring
- Payment form testing
- Real-time API result display
- Multiple test scenarios

## Going Live

### 1. Update Environment Variables
```env
# Switch to live mode
DODO_PAYMENTS_MODE="live"
DODO_PAYMENTS_API_URL="https://api.dodopayments.com/"

# Use production API keys
DODO_PAYMENTS_API_KEY="live_your_production_key"
DODO_PAYMENTS_WEBHOOK_SECRET="your_production_webhook_secret"
```

### 2. Webhook Configuration
- Configure production webhook URL in Dodo Dashboard
- Ensure SSL certificate for webhook endpoint
- Test webhook delivery in live environment

### 3. Security Checklist
- ✅ API keys stored securely in environment variables
- ✅ Webhook signature verification implemented
- ✅ Input validation and sanitization
- ✅ HTTPS for all communications
- ✅ Database indexes optimized
- ✅ Error logging configured

## Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check supervisor logs
tail -n 50 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

#### Payment Creation Fails
1. Verify API keys are correct
2. Check Dodo Payments API status
3. Validate request data format
4. Review backend logs for errors

#### Webhook Events Not Received
1. Verify webhook URL is publicly accessible
2. Check webhook secret configuration
3. Validate signature verification logic
4. Test with ngrok for local development

#### Database Connection Issues
1. Verify MongoDB is running
2. Check MONGO_URL configuration
3. Validate database permissions
4. Review connection string format

### Debug Commands
```bash
# Check service status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log

# Test API endpoints
curl -X GET "http://localhost:8001/api/health"
curl -X POST "http://localhost:8001/api/payments/test/simple-payment"
```

## Security Considerations

### API Key Management
- Store API keys in environment variables only
- Never commit API keys to version control
- Use separate keys for test and production
- Rotate keys regularly

### Webhook Security
- Always verify webhook signatures
- Use HTTPS for webhook endpoints
- Implement rate limiting
- Log webhook events for monitoring

### Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all API communications
- Implement proper authentication
- Regular security audits

### Database Security
- Use MongoDB authentication
- Implement proper access controls
- Regular backups
- Monitor database access

## Production Deployment Checklist

- [ ] Production API keys configured
- [ ] Webhook URLs updated in Dodo Dashboard
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] Error logging configured
- [ ] Security review completed
- [ ] Load testing performed
- [ ] Documentation updated

## Support and Resources

### Documentation
- [Dodo Payments API Documentation](https://docs.dodopayments.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://reactjs.org/docs)

### Support Channels
- Dodo Payments Discord Community
- Email support: support@dodopayments.com
- API status page: [status.dodopayments.com]

---

**Implementation Complete!** 🎉

This implementation provides a robust, production-ready Dodo Payments integration with comprehensive testing, error handling, and security features. The modular architecture makes it easy to extend and maintain.
