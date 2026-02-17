import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard({ token }) {
    const [stats, setStats] = useState(null);
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
            const [statsData, positionsData, webhooksData] = await Promise.all([
                api.getStats(token),
                api.getPositions(token),
                api.getWebhooks(token)
            ]);
            setStats(statsData);
            setPositions(positionsData.positions || []);
            setWebhooks(webhooksData.webhooks || []);
            setLastUpdate(new Date());
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

    const handleClosePosition = async (positionId, symbol) => {
        if (!confirm(`Close position ${symbol}?`)) {
            return;
        }
        
        try {
            await api.closePosition(token, positionId);
            await loadData(); // Reload positions
        } catch (err) {
            alert(err.message || 'Failed to close position');
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h1>Dashboard</h1>
                <div style={{ textAlign: 'right' }}>
                    <button 
                        onClick={loadData} 
                        className="btn" 
                        style={{ padding: '0.5rem 1rem', marginBottom: '0.5rem' }}
                        disabled={loading}
                    >
                        🔄 Refresh
                    </button>
                    {lastUpdate && (
                        <div style={{ fontSize: '0.85em', color: '#666' }}>
                            Last update: {lastUpdate.toLocaleTimeString()}
                        </div>
                    )}
                </div>
            </div>

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

            <div className="stats-grid" style={{ marginTop: '1rem' }}>
                <div className="stat-card" style={{ 
                    gridColumn: 'span 2',
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
                    <h3>Open Positions</h3>
                    <div className="value">{stats?.open_positions || 0}</div>
                </div>
                <div className="stat-card">
                    <h3>Closed Positions</h3>
                    <div className="value">{positions.filter(p => p.status === 'closed').length}</div>
                </div>
            </div>

            <div className="card">
                <h2>Bot Status</h2>
                <p style={{ marginBottom: '1rem' }}>
                    Bot is currently: <strong>{stats?.bot_active ? 'Active' : 'Inactive'}</strong>
                    {stats?.demo_mode && (
                        <span style={{ 
                            marginLeft: '1rem',
                            padding: '0.25rem 0.75rem',
                            background: '#fff3cd',
                            color: '#856404',
                            borderRadius: '4px',
                            fontSize: '0.9em',
                            fontWeight: 'bold'
                        }}>
                            📊 DEMO MODE
                        </span>
                    )}
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
                <h2>Active Positions</h2>
                {positions.length === 0 ? (
                    <p>No positions yet</p>
                ) : (
                    <table className="positions-table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Side</th>
                                <th>Qty</th>
                                <th>Entry</th>
                                <th>Current</th>
                                <th>PnL</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {positions.map((pos) => {
                                const pnl = pos.pnl || 0;
                                const pnlPercent = pos.entry_price ? ((pos.current_price - pos.entry_price) / pos.entry_price * 100) : 0;
                                const isOpen = pos.status === 'open';
                                
                                return (
                                    <tr key={pos.id} style={{ backgroundColor: isOpen ? 'transparent' : '#f5f5f5' }}>
                                        <td><strong>{pos.symbol}</strong></td>
                                        <td>
                                            <span style={{
                                                color: pos.side === 'BUY' ? '#28a745' : '#dc3545',
                                                fontWeight: 'bold'
                                            }}>
                                                {pos.side}
                                            </span>
                                        </td>
                                        <td>{pos.quantity}</td>
                                        <td>${pos.entry_price?.toFixed(2)}</td>
                                        <td>${pos.current_price?.toFixed(2)}</td>
                                        <td>
                                            <div>
                                                <div style={{ 
                                                    color: pnl >= 0 ? '#28a745' : '#dc3545',
                                                    fontWeight: 'bold'
                                                }}>
                                                    {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
                                                </div>
                                                <div style={{ fontSize: '0.85em', color: pnl >= 0 ? '#28a745' : '#dc3545' }}>
                                                    ({pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%)
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`status ${pos.status}`} style={{
                                                padding: '4px 8px',
                                                borderRadius: '4px',
                                                fontSize: '0.85em',
                                                backgroundColor: isOpen ? '#28a745' : '#666',
                                                color: 'white'
                                            }}>
                                                {pos.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            {isOpen ? (
                                                <button
                                                    onClick={() => handleClosePosition(pos.id, pos.symbol)}
                                                    className="btn"
                                                    style={{
                                                        padding: '4px 12px',
                                                        fontSize: '0.85em',
                                                        backgroundColor: '#dc3545',
                                                        color: 'white',
                                                        border: 'none',
                                                        cursor: 'pointer',
                                                        borderRadius: '4px'
                                                    }}
                                                >
                                                    Close
                                                </button>
                                            ) : (
                                                <span style={{ color: '#999', fontSize: '0.85em' }}>-</span>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
