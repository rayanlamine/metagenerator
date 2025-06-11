import React from 'react';

const PaymentCancel = () => {
  return (
    <div style={{ 
      padding: '40px', 
      maxWidth: '600px', 
      margin: '0 auto',
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        backgroundColor: '#f8d7da',
        border: '1px solid #f5c6cb',
        borderRadius: '8px',
        padding: '30px',
        marginBottom: '20px'
      }}>
        <h1 style={{ color: '#721c24', marginBottom: '20px' }}>
          ❌ Payment Cancelled
        </h1>
        <p style={{ fontSize: '18px', color: '#721c24', marginBottom: '20px' }}>
          Your payment was cancelled or interrupted.
        </p>
        <p style={{ color: '#856404' }}>
          No charges have been made to your account.
        </p>
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
          Try Again
        </button>
      </div>
    </div>
  );
};

export default PaymentCancel;