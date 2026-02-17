import { useState, useEffect } from 'react';
import { api } from '../api';
import ConnectionStatus from '../components/ConnectionStatus';
import EquityCurve from '../components/EquityCurve';
import PriceTicker from '../components/PriceTicker';

export default function Dashboard({ token }) {
    const [stats, setStats] = useState(null);
    const [analytics, setAnalytics] = useState(null);
    const [positions, setPositions] = useState([]);
    const [webhooks, setWebhooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState(null);

    useEffect(() => {
        loadData();
        // Reload data every 10 seconds
        const interval = setInterval(loadData, 10000);
        return () => clearInterval(interval);
    }, []);

    const loadData = async () => {
        try {
            const [statsData, analyticsData, positionsData, webhooksData] = await Promise.all([
                api.getStats(token),
                api.getAdvancedAnalytics(token),
                api.getPositions(token),
                api.getWebhooks(token)
            ]);
            setStats(statsData);
            setAnalytics(analyticsData.analytics || {});
            setPositions(positionsData.positions || []);
            setWebhooks(webhooksData.webhooks || []);
            setLastUpdate(new Date());
        } catch (err) {
            console.error('Error loading data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleClosePosition = async (positionId) => {
        if (!confirm('Are you sure you want to close this position?')) {
            return;
        }

        try {
            await api.closePosition(token, positionId);
            loadData(); // Reload data after closing
        } catch (err) {
            alert(`Error closing position: ${err.message}`);
        }
    };

    if (loading) return <div className="container">Loading...</div>;

    // Calculate unrealized PnL from open positions
    const unrealizedPnL = positions
        .filter(pos => pos.status === 'open')
        .reduce((sum, pos) => sum + (pos.pnl || 0), 0);
    
    const realizedProfit = stats?.total_profit || 0;
    const totalValue = realizedProfit + unrealizedPnL;

    return (
        <div className="container">
            {/* Header with Connection Status and Refresh */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h1>Trading Dashboard</h1>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <ConnectionStatus api={api} />
                    <button 
                        onClick={loadData} 
                        className="btn" 
                        style={{ padding: '0.5rem 1rem' }}
                        disabled={loading}
                    >
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {lastUpdate && (
                <div style={{ textAlign: 'right', fontSize: '0.85em', color: '#666', marginBottom: '1rem' }}>
                    Last update: {lastUpdate.toLocaleTimeString()}
                </div>
            )}

            {/* Main Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Trades</h3>
                    <div className="value">{stats?.total_trades || 0}</div>
                </div>
                <div className="stat-card">
                    <h3>Win Rate</h3>
                    <div className="value">{analytics?.win_rate || 0}%</div>
                    <div style={{ fontSize: '0.8em', color: '#666', marginTop: '0.25rem' }}>
                        {analytics?.winning_trades || 0}W / {analytics?.losing_trades || 0}L
                    </div>
                </div>
                <div className="stat-card">
                    <h3>💰 Realized Profit</h3>
                    <div className="value" style={{ 
                        color: realizedProfit >= 0 ? '#28a745' : '#dc3545',
                        fontWeight: 'bold' 
                    }}>
                        {realizedProfit >= 0 ? '+' : ''}${realizedProfit.toFixed(2)}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#666', marginTop: '0.25rem' }}>
                        From closed positions
                    </div>
                </div>
                <div className="stat-card">
                    <h3>📈 Unrealized PnL</h3>
                    <div className="value" style={{ 
                        color: unrealizedPnL >= 0 ? '#28a745' : '#dc3545',
                        fontWeight: 'bold' 
                    }}>
                        {unrealizedPnL >= 0 ? '+' : ''}${unrealizedPnL.toFixed(2)}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#666', marginTop: '0.25rem' }}>
                        From open positions
                    </div>
                </div>
            </div>

            {/* Portfolio Value + Equity Curve */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                <div className="stat-card" style={{ 
                    backgroundColor: totalValue >= 0 ? '#d4edda' : '#f8d7da',
                    border: `2px solid ${totalValue >= 0 ? '#28a745' : '#dc3545'}`
                }}>
                    <h3 style={{ color: totalValue >= 0 ? '#155724' : '#721c24' }}>
                        🎯 Total Portfolio Value
                    </h3>
                    <div className="value" style={{ 
                        color: totalValue >= 0 ? '#28a745' : '#dc3545',
                        fontWeight: 'bold',
                        fontSize: '2rem'
                    }}>
                        {totalValue >= 0 ? '+' : ''}${totalValue.toFixed(2)}
                    </div>
                    <div style={{ fontSize: '0.85em', color: totalValue >= 0 ? '#155724' : '#721c24', marginTop: '0.5rem' }}>
                        Realized + Unrealized
                    </div>
                </div>

                <div className="stat-card">
                    <h3>📊 Equity Curve (24h)</h3>
                    <EquityCurve api={api} token={token} />
                </div>
            </div>

            {/* Advanced Analytics */}
            {analytics && (
                <div className="stats-grid" style={{ marginTop: '1rem' }}>
                    <div className="stat-card">
                        <h3>Avg Profit</h3>
                        <div className="value" style={{ color: '#28a745' }}>
                            +${analytics.avg_profit?.toFixed(2) || '0.00'}
                        </div>
                    </div>
                    <div className="stat-card">
                        <h3>Avg Loss</h3>
                        <div className="value" style={{ color: '#dc3545' }}>
                            ${analytics.avg_loss?.toFixed(2) || '0.00'}
                        </div>
                    </div>
                    <div className="stat-card">
                        <h3>Max Drawdown</h3>
                        <div className="value" style={{ color: '#dc3545' }}>
                            {analytics.max_drawdown_percent?.toFixed(2) || '0'}%
                        </div>
                        <div style={{ fontSize: '0.8em', color: '#666' }}>
                            ${analytics.max_drawdown?.toFixed(2) || '0'}
                        </div>
                    </div>
                    <div className="stat-card">
                        <h3>Profit Factor</h3>
                        <div className="value" style={{ 
                            color: (analytics.profit_factor || 0) >= 1 ? '#28a745' : '#dc3545'
                        }}>
                            {analytics.profit_factor?.toFixed(2) || '0.00'}
                        </div>
                    </div>
                </div>
            )}

            {/* Open Positions Table */}
            <h2 style={{ marginTop: '2rem' }}>Open Positions</h2>
            <div className="table-container">
                <table className="positions-table">
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Side</th>
                            <th>Quantity</th>
                            <th>Entry Price</th>
                            <th>Current Price</th>
                            <th>P&L</th>
                            <th>Opened At</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {positions.filter(pos => pos.status === 'open').map(pos => {
                            const pnlPercent = pos.entry_price > 0 
                                ? ((pos.pnl || 0) / (pos.entry_price * (pos.remaining_quantity || pos.quantity))) * 100 
                                : 0;
                            
                            return (
                                <tr key={pos.id}>
                                    <td style={{ fontWeight: 'bold' }}>{pos.ticker}</td>
                                    <td>
                                        <span className={`badge ${pos.side === 'buy' ? 'badge-success' : 'badge-danger'}`}>
                                            {pos.side?.toUpperCase()}
                                        </span>
                                    </td>
                                    <td>{pos.remaining_quantity || pos.quantity}</td>
                                    <td>${pos.entry_price?.toFixed(2)}</td>
                                    <td>
                                        <PriceTicker ticker={pos.ticker} api={api} token={token} />
                                    </td>
                                    <td>
                                        <span style={{ 
                                            color: (pos.pnl || 0) >= 0 ? '#28a745' : '#dc3545',
                                            fontWeight: 'bold'
                                        }}>
                                            {(pos.pnl || 0) >= 0 ? '+' : ''}${(pos.pnl || 0).toFixed(2)}
                                            <br />
                                            <span style={{ fontSize: '0.85em' }}>
                                                ({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)
                                            </span>
                                        </span>
                                    </td>
                                    <td>{new Date(pos.opened_at).toLocaleString()}</td>
                                    <td>
                                        <button 
                                            onClick={() => handleClosePosition(pos.id)}
                                            className="btn btn-sm btn-danger"
                                        >
                                            Close
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                {positions.filter(pos => pos.status === 'open').length === 0 && (
                    <div style={{ padding: '2rem', textAlign: 'center', color: '#999' }}>
                        No open positions
                    </div>
                )}
            </div>

            {/* Recent Webhooks */}
            <h2 style={{ marginTop: '2rem' }}>Recent Webhooks</h2>
            <div className="table-container">
                <table className="positions-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Payload</th>
                            <th>Received At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {webhooks.slice(0, 10).map(webhook => (
                            <tr key={webhook.id}>
                                <td>{webhook.id}</td>
                                <td>
                                    <code style={{ 
                                        fontSize: '0.85em',
                                        backgroundColor: '#f5f5f5',
                                        padding: '0.25rem 0.5rem',
                                        borderRadius: '4px',
                                        display: 'inline-block',
                                        maxWidth: '600px',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap'
                                    }}>
                                        {webhook.payload}
                                    </code>
                                </td>
                                <td>{new Date(webhook.received_at).toLocaleString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
