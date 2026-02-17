import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard({ token }) {
    const [stats, setStats] = useState(null);
    const [positions, setPositions] = useState([]);
    const [webhooks, setWebhooks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
        // Reload data every 10 seconds
        const interval = setInterval(loadData, 10000);
        return () => clearInterval(interval);
    }, []);

    const loadData = async () => {
        try {
            const [statsData, positionsData, webhooksData] = await Promise.all([
                api.getStats(token),
                api.getPositions(token),
                api.getWebhooks(token)
            ]);
            setStats(statsData);
            setPositions(positionsData.positions || []);
            setWebhooks(webhooksData.webhooks || []);
        } catch (err) {
            console.error('Error loading data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleBot = async () => {
        try {
            setLoading(true);
            const result = await api.toggleBot(token);
            if (result.error) {
                alert(`Error: ${result.error}`);
            } else {
                setStats({ ...stats, bot_active: result.is_active });
                alert(`Bot ${result.is_active ? 'activated' : 'deactivated'} successfully!`);
            }
        } catch (err) {
            console.error('Error toggling bot:', err);
            alert(`Failed to toggle bot: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="container">Loading...</div>;

    return (
        <div className="container">
            <h1>Dashboard</h1>

            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Trades</h3>
                    <div className="value">{stats?.total_trades || 0}</div>
                </div>
                <div className="stat-card">
                    <h3>Win Rate</h3>
                    <div className="value">{stats?.win_rate || 0}%</div>
                </div>
                <div className="stat-card">
                    <h3>Total Profit</h3>
                    <div className="value">${stats?.total_profit?.toFixed(2) || '0.00'}</div>
                </div>
                <div className="stat-card">
                    <h3>Open Positions</h3>
                    <div className="value">{stats?.open_positions || 0}</div>
                </div>
            </div>

            <div className="card">
                <h2>Bot Status</h2>
                <p style={{ marginBottom: '1rem' }}>
                    Bot is currently: <strong>{stats?.bot_active ? 'Active' : 'Inactive'}</strong>
                </p>
                <button
                    className={`btn ${stats?.bot_active ? 'btn-danger' : 'btn-success'}`}
                    onClick={handleToggleBot}
                >
                    {stats?.bot_active ? 'Stop Bot' : 'Start Bot'}
                </button>
            </div>

            <div className="card">
                <h2>Recent Webhooks from TradingView</h2>
                {webhooks.length === 0 ? (
                    <p>No webhooks received yet</p>
                ) : (
                    <table className="positions-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Ticker</th>
                                <th>Price</th>
                                <th>Signal</th>
                                <th>Payload</th>
                            </tr>
                        </thead>
                        <tbody>
                            {webhooks.slice(0, 10).map((wh) => {
                                const payload = typeof wh.payload === 'string' ? JSON.parse(wh.payload) : wh.payload;
                                return (
                                    <tr key={wh.id}>
                                        <td>{new Date(wh.received_at).toLocaleString()}</td>
                                        <td>{payload.ticker || '-'}</td>
                                        <td>{payload.price ? `$${payload.price}` : '-'}</td>
                                        <td>
                                            {payload.signal ? (
                                                <span style={{color: payload.signal === 'BUY' ? 'green' : 'red'}}>
                                                    {payload.signal}
                                                </span>
                                            ) : '-'}
                                        </td>
                                        <td style={{fontSize: '0.85em', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                                            {payload.raw_message || JSON.stringify(payload).substring(0, 100)}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="card">
                <h2>Recent Positions</h2>
                {positions.length === 0 ? (
                    <p>No positions yet</p>
                ) : (
                    <table className="positions-table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Side</th>
                                <th>Quantity</th>
                                <th>Entry Price</th>
                                <th>PnL</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {positions.map((pos) => (
                                <tr key={pos.id}>
                                    <td>{pos.symbol}</td>
                                    <td>{pos.side}</td>
                                    <td>{pos.quantity}</td>
                                    <td>${pos.entry_price}</td>
                                    <td style={{ color: pos.pnl >= 0 ? 'green' : 'red' }}>
                                        ${pos.pnl?.toFixed(2)}
                                    </td>
                                    <td>
                                        <span className={`status ${pos.status}`}>{pos.status}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
