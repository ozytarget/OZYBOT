import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Settings({ token }) {
    const [config, setConfig] = useState({
        risk_level: 'medium',
        max_position_size: 1000,
        stop_loss_percent: 2,
        take_profit_percent: 5,
        demo_mode: true,
        auto_close_enabled: true
    });
    const [broker, setBroker] = useState({
        broker_name: '',
        api_key: '',
        api_secret: ''
    });
    const [message, setMessage] = useState('');

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            const [configData, brokerData] = await Promise.all([
                api.getConfig(token),
                api.getBroker(token)
            ]);
            if (!configData.error) setConfig(configData);
            if (!brokerData.error) setBroker(brokerData);
        } catch (err) {
            console.error('Error loading settings:', err);
        }
    };

    const handleConfigSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await api.updateConfig(token, config);
            setMessage(result.message || 'Config updated successfully');
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setMessage('Error updating config');
        }
    };

    const handleBrokerSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await api.updateBroker(token, broker);
            setMessage(result.message || 'Broker settings updated successfully');
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setMessage('Error updating broker settings');
        }
    };

    return (
        <div className="container">
            <h1>Settings</h1>

            {message && (
                <div style={{
                    padding: '1rem',
                    background: '#d4edda',
                    color: '#155724',
                    borderRadius: '4px',
                    marginBottom: '1rem'
                }}>
                    {message}
                </div>
            )}

            <div className="card">
                <h2>⚙️ Bot Configuration</h2>
                <form onSubmit={handleConfigSubmit}>
                    
                    {/* Trading Mode Section */}
                    <div style={{ 
                        padding: '1rem', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '8px', 
                        marginBottom: '1.5rem',
                        border: '1px solid #dee2e6'
                    }}>
                        <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#495057' }}>Trading Mode</h3>
                        
                        <div className="form-group">
                            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={config.demo_mode}
                                    onChange={(e) => setConfig({ ...config, demo_mode: e.target.checked })}
                                    style={{ width: 'auto', marginRight: '0.75rem', transform: 'scale(1.2)' }}
                                />
                                <div>
                                    <strong style={{ fontSize: '1rem' }}>📊 DEMO Mode</strong>
                                    <p style={{ fontSize: '0.85em', color: '#666', margin: '0.25rem 0 0 0' }}>
                                        Simulate trades without executing real orders through your broker. Perfect for testing strategies.
                                    </p>
                                </div>
                            </label>
                        </div>
                    </div>

                    {/* Risk Management Section */}
                    <div style={{ 
                        padding: '1rem', 
                        backgroundColor: '#fff3cd', 
                        borderRadius: '8px', 
                        marginBottom: '1.5rem',
                        border: '1px solid #ffc107'
                    }}>
                        <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#856404' }}>🛡️ Risk Management</h3>
                        
                        <div className="form-group">
                            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={config.auto_close_enabled}
                                    onChange={(e) => setConfig({ ...config, auto_close_enabled: e.target.checked })}
                                    style={{ width: 'auto', marginRight: '0.75rem', transform: 'scale(1.2)' }}
                                />
                                <div>
                                    <strong style={{ fontSize: '1rem' }}>🤖 Automatic Stop Loss / Take Profit</strong>
                                    <p style={{ fontSize: '0.85em', color: '#856404', margin: '0.25rem 0 0 0' }}>
                                        Automatically close positions when Stop Loss or Take Profit levels are reached. Recommended for risk protection.
                                    </p>
                                </div>
                            </label>
                        </div>

                        <div className="form-group">
                            <label>Stop Loss (%)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={config.stop_loss_percent}
                                onChange={(e) => setConfig({ ...config, stop_loss_percent: parseFloat(e.target.value) })}
                                placeholder="e.g., 2 for 2% loss"
                            />
                            <p style={{ fontSize: '0.85em', color: '#666', marginTop: '0.25rem' }}>
                                Close position if loss reaches this percentage
                            </p>
                        </div>

                        <div className="form-group">
                            <label>Take Profit (%)</label>
                            <input
                                type="number"
                                step="0.1"
                                value={config.take_profit_percent}
                                onChange={(e) => setConfig({ ...config, take_profit_percent: parseFloat(e.target.value) })}
                                placeholder="e.g., 5 for 5% profit"
                            />
                            <p style={{ fontSize: '0.85em', color: '#666', marginTop: '0.25rem' }}>
                                Close position if profit reaches this percentage
                            </p>
                        </div>
                    </div>

                    {/* Position Sizing Section */}
                    <div style={{ 
                        padding: '1rem', 
                        backgroundColor: '#d4edda', 
                        borderRadius: '8px', 
                        marginBottom: '1.5rem',
                        border: '1px solid #28a745'
                    }}>
                        <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#155724' }}>💰 Position Sizing</h3>
                        
                        <div className="form-group">
                            <label>Risk Level</label>
                            <select
                                value={config.risk_level}
                                onChange={(e) => setConfig({ ...config, risk_level: e.target.value })}
                                style={{ padding: '0.5rem', width: '100%' }}
                            >
                                <option value="low">Low - Conservative</option>
                                <option value="medium">Medium - Balanced</option>
                                <option value="high">High - Aggressive</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Max Position Size ($)</label>
                            <input
                                type="number"
                                value={config.max_position_size}
                                onChange={(e) => setConfig({ ...config, max_position_size: parseFloat(e.target.value) })}
                                placeholder="e.g., 1000"
                            />
                            <p style={{ fontSize: '0.85em', color: '#155724', marginTop: '0.25rem' }}>
                                Maximum dollar amount per trade
                            </p>
                        </div>
                    </div>

                    <button type="submit" className="btn" style={{ 
                        width: '100%', 
                        padding: '0.75rem',
                        fontSize: '1rem',
                        fontWeight: 'bold'
                    }}>
                        💾 Save Configuration
                    </button>
                </form>
            </div>

            <div className="card">
                <h2>Broker Settings</h2>
                <form onSubmit={handleBrokerSubmit}>
                    <div className="form-group">
                        <label>Broker Name</label>
                        <input
                            type="text"
                            value={broker.broker_name || ''}
                            onChange={(e) => setBroker({ ...broker, broker_name: e.target.value })}
                            placeholder="e.g., Interactive Brokers, Alpaca"
                        />
                    </div>
                    <div className="form-group">
                        <label>API Key</label>
                        <input
                            type="text"
                            value={broker.api_key || ''}
                            onChange={(e) => setBroker({ ...broker, api_key: e.target.value })}
                            placeholder="Your broker API key"
                        />
                    </div>
                    <div className="form-group">
                        <label>API Secret</label>
                        <input
                            type="password"
                            value={broker.api_secret || ''}
                            onChange={(e) => setBroker({ ...broker, api_secret: e.target.value })}
                            placeholder="Your broker API secret"
                        />
                    </div>
                    <button type="submit" className="btn">Save Broker Settings</button>
                </form>
            </div>
        </div>
    );
}
