import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Settings({ token }) {
    const [config, setConfig] = useState({
        risk_level: 'medium',
        max_position_size: 1000,
        stop_loss_percent: 2,
        take_profit_percent: 5,
        demo_mode: true
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
                <h2>Bot Configuration</h2>
                <form onSubmit={handleConfigSubmit}>
                    <div className="form-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={config.demo_mode}
                                onChange={(e) => setConfig({ ...config, demo_mode: e.target.checked })}
                                style={{ width: 'auto', marginRight: '0.5rem' }}
                            />
                            <strong>DEMO Mode</strong> - Simulate trades without real broker API
                        </label>
                        <p style={{ fontSize: '0.9em', color: '#666', marginTop: '0.5rem' }}>
                            When enabled, the bot will create simulated positions when TradingView alerts arrive, without executing real trades.
                        </p>
                    </div>
                    <div className="form-group">
                        <label>Risk Level</label>
                        <select
                            value={config.risk_level}
                            onChange={(e) => setConfig({ ...config, risk_level: e.target.value })}
                        >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Max Position Size ($)</label>
                        <input
                            type="number"
                            value={config.max_position_size}
                            onChange={(e) => setConfig({ ...config, max_position_size: parseFloat(e.target.value) })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Stop Loss (%)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={config.stop_loss_percent}
                            onChange={(e) => setConfig({ ...config, stop_loss_percent: parseFloat(e.target.value) })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Take Profit (%)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={config.take_profit_percent}
                            onChange={(e) => setConfig({ ...config, take_profit_percent: parseFloat(e.target.value) })}
                        />
                    </div>
                    <button type="submit" className="btn">Save Configuration</button>
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
