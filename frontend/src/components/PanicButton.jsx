import React, { useState } from 'react';
import axios from 'axios';
import './PanicButton.css';

const PanicButton = () => {
  const [isActivating, setIsActivating] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [result, setResult] = useState(null);

  const handleKillSwitch = async () => {
    setIsActivating(true);
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/safety/panic/kill-switch`,
        {
          reason: 'Manual panic button activation by user'
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setResult({
        success: true,
        message: response.data.message || 'Kill switch activated successfully',
        data: response.data
      });

      // Auto-hide result after 5 seconds
      setTimeout(() => {
        setResult(null);
        setShowConfirm(false);
      }, 5000);

    } catch (error) {
      setResult({
        success: false,
        message: error.response?.data?.error || 'Failed to activate kill switch',
      });
    } finally {
      setIsActivating(false);
    }
  };

  return (
    <div className="panic-button-container">
      {!showConfirm ? (
        <button
          className="panic-button"
          onClick={() => setShowConfirm(true)}
          title="Emergency Kill Switch - Close all positions"
        >
          <span className="panic-icon">🚨</span>
          <span className="panic-text">EMERGENCY STOP</span>
        </button>
      ) : (
        <div className="panic-confirm-modal">
          <div className="panic-confirm-content">
            <h3>⚠️ EMERGENCY KILL SWITCH</h3>
            <p>This will immediately:</p>
            <ul>
              <li>Close ALL open positions at market price</li>
              <li>Deactivate the trading bot</li>
              <li>Stop receiving new signals</li>
            </ul>
            <p className="panic-warning">
              <strong>This action cannot be undone!</strong>
            </p>

            <div className="panic-confirm-buttons">
              <button
                className="panic-confirm-yes"
                onClick={handleKillSwitch}
                disabled={isActivating}
              >
                {isActivating ? 'ACTIVATING...' : 'YES, STOP EVERYTHING'}
              </button>
              <button
                className="panic-confirm-no"
                onClick={() => setShowConfirm(false)}
                disabled={isActivating}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className={`panic-result ${result.success ? 'success' : 'error'}`}>
          <div className="panic-result-content">
            <span className="panic-result-icon">
              {result.success ? '✅' : '❌'}
            </span>
            <div className="panic-result-message">
              <strong>{result.success ? 'Success' : 'Error'}</strong>
              <p>{result.message}</p>
              {result.data && result.success && (
                <div className="panic-result-details">
                  <p>Positions closed: {result.data.positions_closed || 0}</p>
                  <p>Bot status: {result.data.bot_deactivated ? 'DEACTIVATED' : 'ACTIVE'}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PanicButton;
