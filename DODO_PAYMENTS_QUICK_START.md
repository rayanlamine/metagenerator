# Dodo Payments Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Clone and Setup
```bash
# Repository already cloned in /app/meta-generation-tool-official
cd /app

# Backend is already configured with Dodo Payments integration
# Frontend is already set up with payment components
```

### 2. Configure API Keys
Update `/app/backend/.env`:
```env
DODO_PAYMENTS_API_KEY="Y5h-0edhftQ-_aWv.UDaLs-NfZ0DRsjzWCVZztJH_3xCF9UL7dHbe34fZZyDQd6Ij"
DODO_PAYMENTS_WEBHOOK_SECRET="whsec_WCNk54MC15TS8FZ8eVIFZk1K"
DODO_PAYMENTS_MODE="test"
```

Update `/app/frontend/.env`:
```env
REACT_APP_DODO_PAYMENTS_API_KEY=Y5h-0edhftQ-_aWv.UDaLs-NfZ0DRsjzWCVZztJH_3xCF9UL7dHbe34fZZyDQd6Ij
REACT_APP_DODO_PAYMENTS_MODE=test
```

### 3. Start Services
```bash
sudo supervisorctl restart all
```

### 4. Test Integration
1. **Backend Test**: Run the comprehensive backend test
2. **Frontend Test**: Visit the test page at your frontend URL + `/payment-test`
3. **Health Check**: Check `/api/health` endpoint

## 🧪 Testing Payments

### Test Cards
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0000 0000 3220`

Use any future expiry date and any 3-digit CVC.

### Test Flow
1. Go to `/payment-test` on your frontend
2. Configure payment amount (default $10.00)
3. Click "Create Payment"
4. Use test card on Dodo checkout page
5. Verify success/failure handling

## 📊 API Endpoints

### Payment Endpoints
- `POST /api/payments/checkout` - Create payment
- `POST /api/payments/subscriptions` - Create subscription
- `GET /api/payments/payments/{id}` - Get payment details
- `GET /api/health` - System health check

### Webhook
- `POST /api/webhooks/dodo` - Process webhook events

## 🔧 Key Files

### Backend
- `/app/backend/models/payment.py` - Payment models
- `/app/backend/services/dodo_payments.py` - Dodo Payments service
- `/app/backend/routes/payments.py` - Payment API routes
- `/app/backend/database.py` - Database utilities

### Frontend
- `/app/frontend/src/components/DodoPaymentTest.js` - Test interface
- `/app/frontend/src/components/PaymentSuccess.js` - Success page
- `/app/frontend/src/components/PaymentCancel.js` - Cancel page

## 🎯 Going Live

1. **Get Production Keys**: From Dodo Payments dashboard
2. **Update Environment**: Set `DODO_PAYMENTS_MODE="live"`
3. **Configure Webhooks**: Point to your production URL
4. **Test**: Run a small live transaction
5. **Monitor**: Check logs and webhook deliveries

## 📞 Support

- **Documentation**: See `DODO_PAYMENTS_IMPLEMENTATION_GUIDE.md`
- **Issues**: Check troubleshooting section
- **Logs**: `tail -f /var/log/supervisor/backend.err.log`

---

**You're ready to process payments with Dodo! 🦤💳**
