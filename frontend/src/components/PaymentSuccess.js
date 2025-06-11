import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const [paymentInfo, setPaymentInfo] = useState({});

  useEffect(() => {
    // Extract payment information from URL parameters
    const info = {};
    for (let [key, value] of searchParams.entries()) {
      info[key] = value;
    }
    setPaymentInfo(info);
  }, [searchParams]);

  return (
    <div style={{ 
      padding: '40px', 
      maxWidth: '600px', 
      margin: '0 auto',
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        backgroundColor: '#d4edda',
        border: '1px solid #c3e6cb',
        borderRadius: '8px',
        padding: '30px',
        marginBottom: '20px'
      }}>
        <h1 style={{ color: '#155724', marginBottom: '20px' }}>
          ✅ Payment Successful!
        </h1>
        <p style={{ fontSize: '18px', color: '#155724', marginBottom: '20px' }}>
          Your payment has been processed successfully.
        </p>
        
        {Object.keys(paymentInfo).length > 0 && (
          <div style={{ 
            backgroundColor: '#f8f9fa', 
            padding: '20px', 
            borderRadius: '6px',
            textAlign: 'left',
            marginTop: '20px'
          }}>
            <h3 style={{ marginBottom: '15px', color: '#333' }}>Payment Details:</h3>
            {Object.entries(paymentInfo).map(([key, value]) => (
              <p key={key} style={{ margin: '5px 0', color: '#666' }}>
                <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {value}
              </p>
            ))}
          </div>
        )}
      </div>

      <div style={{ marginTop: '30px' }}>
        <button
          onClick={() => window.location.href = '/'}
          style={{
            padding: '12px 30px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            cursor: 'pointer',
            marginRight: '10px'
          }}
        >
          Return to Home
        </button>
        
        <button
          onClick={() => window.location.href = '/payment-test'}
          style={{
            padding: '12px 30px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
        >
          Test More Payments
        </button>
      </div>
    </div>
  );
};

export default PaymentSuccess;