import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios to use the backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

const DodoPaymentTest = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState('');
  const [healthStatus, setHealthStatus] = useState(null);
  
  // Test payment form state
  const [amount, setAmount] = useState('10.00');
  const [currency, setCurrency] = useState('USD');
  const [customerEmail, setCustomerEmail] = useState('test@example.com');
  const [customerName, setCustomerName] = useState('Test User');

  // Check API health on component mount
  useEffect(() => {
    checkHealthStatus();
  }, []);

  const checkHealthStatus = async () => {
    try {
      const response = await api.get('/api/health');
      setHealthStatus(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'error', message: error.message });
    }
  };

  const handleSimplePayment = async () => {
    setIsLoading(true);
    setResult('');
    
    try {
      const paymentData = {
        billing_currency: currency,
        allowed_payment_method_types: ['credit', 'debit'],
        product_cart: [
          {
            product_id: 'test_product',
            amount: Math.round(parseFloat(amount) * 100), // Convert to cents
            quantity: 1
          }
        ],
        return_url: `${window.location.origin}/payment-success`,
        customer: {
          email: customerEmail,
          name: customerName
        },
        metadata: {
          test: true,
          source: 'frontend_test',
          timestamp: new Date().toISOString()
        }
      };

      const response = await api.post('/api/payments/checkout', paymentData);
      
      setResult(`✅ Payment session created successfully!\n\n` +
                `Payment ID: ${response.data.id}\n` +
                `Status: ${response.data.status}\n` +
                `Checkout URL: ${response.data.url}\n\n` +
                `Redirecting to checkout page...`);
      
      // Redirect to payment page after 2 seconds
      if (response.data.url) {
        setTimeout(() => {
          window.open(response.data.url, '_blank');
        }, 2000);
      }
      
    } catch (error) {
      console.error('Payment error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error occurred';
      setResult(`❌ Payment creation failed:\n\n${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestEndpoint = async () => {
    setIsLoading(true);
    setResult('');
    
    try {
      const response = await api.post('/api/payments/test/simple-payment');
      
      setResult(`✅ Test endpoint successful!\n\n` +
                `Payment ID: ${response.data.id}\n` +
                `Status: ${response.data.status}\n` +
                `Checkout URL: ${response.data.url}`);
      
    } catch (error) {
      console.error('Test endpoint error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error occurred';
      setResult(`❌ Test endpoint failed:\n\n${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSubscription = async () => {
    setIsLoading(true);
    setResult('');
    
    try {
      const subscriptionData = {
        customer: {
          customer_id: `customer_${Date.now()}`,
          email: customerEmail,
          name: customerName
        },
        product_id: 'monthly_subscription',
        billing: {
          street: '123 Test Street',
          city: 'Test City',
          state: 'Test State',
          country: 'US',
          zipcode: '12345'
        },
        payment_link: true,
        metadata: {
          test: true,
          subscription_type: 'monthly',
          source: 'frontend_test'
        }
      };

      const response = await api.post('/api/payments/subscriptions', subscriptionData);
      
      setResult(`✅ Subscription created successfully!\n\n` +
                `Subscription ID: ${response.data.subscription_id}\n` +
                `Customer ID: ${response.data.customer_id}\n` +
                `Status: ${response.data.status}\n` +
                `Product ID: ${response.data.product_id}`);
      
      if (response.data.payment_url) {
        setResult(prev => prev + `\n\nPayment URL: ${response.data.payment_url}\n\nRedirecting...`);
        setTimeout(() => {
          window.open(response.data.payment_url, '_blank');
        }, 2000);
      }
      
    } catch (error) {
      console.error('Subscription error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error occurred';
      setResult(`❌ Subscription creation failed:\n\n${errorMsg}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      maxWidth: '800px', 
      margin: '0 auto',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1>🦤 Dodo Payments Test Center</h1>
      <p>Comprehensive testing for Dodo Payments integration - FastAPI backend with React frontend</p>
      
      {/* Health Status */}
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        padding: '15px', 
        borderRadius: '8px', 
        marginBottom: '20px' 
      }}>
        <h3>🔧 System Status</h3>
        {healthStatus ? (
          <div>
            <p><strong>API Status:</strong> {healthStatus.status}</p>
            {healthStatus.dodo_payments && (
              <div>
                <p><strong>Dodo API Key:</strong> {healthStatus.dodo_payments.api_key_configured ? '✅ Configured' : '❌ Missing'}</p>
                <p><strong>Webhook Secret:</strong> {healthStatus.dodo_payments.webhook_secret_configured ? '✅ Configured' : '❌ Missing'}</p>
                <p><strong>Mode:</strong> {healthStatus.dodo_payments.mode}</p>
              </div>
            )}
            {healthStatus.database && (
              <p><strong>Database:</strong> {healthStatus.database.connected ? '✅ Connected' : '❌ Disconnected'} ({healthStatus.database.name})</p>
            )}
          </div>
        ) : (
          <p>Loading status...</p>
        )}
        <button 
          onClick={checkHealthStatus}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Refresh Status
        </button>
      </div>

      {/* Payment Form */}
      <div style={{ 
        backgroundColor: '#ffffff', 
        padding: '20px', 
        border: '1px solid #ddd', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3>💳 Payment Configuration</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
          <div>
            <label>Amount ($):</label>
            <input
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                marginTop: '5px'
              }}
            />
          </div>
          <div>
            <label>Currency:</label>
            <input
              type="text"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                marginTop: '5px'
              }}
            />
          </div>
          <div>
            <label>Customer Email:</label>
            <input
              type="email"
              value={customerEmail}
              onChange={(e) => setCustomerEmail(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                marginTop: '5px'
              }}
            />
          </div>
          <div>
            <label>Customer Name:</label>
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                marginTop: '5px'
              }}
            />
          </div>
        </div>
      </div>

      {/* Test Buttons */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px', 
        marginBottom: '20px' 
      }}>
        <button
          onClick={handleSimplePayment}
          disabled={isLoading}
          style={{
            padding: '15px 20px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? 'Processing...' : `💰 Create Payment ($${amount})`}
        </button>

        <button
          onClick={handleTestEndpoint}
          disabled={isLoading}
          style={{
            padding: '15px 20px',
            backgroundColor: '#17a2b8',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? 'Testing...' : '🧪 Test API Endpoint'}
        </button>

        <button
          onClick={handleCreateSubscription}
          disabled={isLoading}
          style={{
            padding: '15px 20px',
            backgroundColor: '#6f42c1',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? 'Creating...' : '🔄 Create Subscription'}
        </button>
      </div>

      {/* Test Information */}
      <div style={{ 
        backgroundColor: '#e7f3ff', 
        padding: '15px', 
        borderRadius: '8px', 
        marginBottom: '20px' 
      }}>
        <h3>💳 Test Card Information</h3>
        <div style={{ fontFamily: 'monospace', fontSize: '14px' }}>
          <p><strong>Success (Global):</strong> 4242 4242 4242 4242</p>
          <p><strong>Success (India):</strong> 6074 8259 7208 3818</p>
          <p><strong>Decline:</strong> 4000 0000 0000 0002</p>
          <p><strong>3D Secure:</strong> 4000 0000 0000 3220</p>
          <p><strong>Insufficient Funds:</strong> 4000 0000 0000 9995</p>
          <p style={{ marginTop: '10px', fontFamily: 'Arial, sans-serif' }}>
            <em>Use any future expiry date and any 3-digit CVC</em>
          </p>
        </div>
      </div>

      {/* Results */}
      <div style={{ 
        backgroundColor: '#f8f9fa', 
        padding: '15px', 
        border: '1px solid #dee2e6', 
        borderRadius: '8px' 
      }}>
        <h3>📊 Test Results</h3>
        <textarea
          value={result}
          readOnly
          placeholder="Test results will appear here...

• API responses
• Payment status
• Error messages
• Success confirmations"
          style={{
            width: '100%',
            height: '200px',
            padding: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '12px',
            backgroundColor: '#ffffff',
            resize: 'vertical'
          }}
        />
      </div>

      {/* Configuration Info */}
      <div style={{ 
        marginTop: '20px', 
        padding: '15px', 
        backgroundColor: '#fff3cd', 
        border: '1px solid #ffeeba',
        borderRadius: '8px',
        fontSize: '14px'
      }}>
        <h4>🔧 Current Configuration:</h4>
        <p><strong>Backend URL:</strong> {API_BASE_URL}</p>
        <p><strong>Dodo API Key:</strong> {process.env.REACT_APP_DODO_PAYMENTS_API_KEY ? '✅ Configured' : '❌ Missing'}</p>
        <p><strong>Mode:</strong> {process.env.REACT_APP_DODO_PAYMENTS_MODE || 'test'}</p>
        <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
      </div>
    </div>
  );
};

export default DodoPaymentTest;