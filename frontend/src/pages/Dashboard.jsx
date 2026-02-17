import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard({ token }) {
    const [stats, setStats] = useState(null);
    const [positions, setPositions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [statsData, positionsData] = await Promise.all([
                api.getStats(token),
                api.getPositions(token)
            ]);
            setStats(statsData);
            setPositions(positionsData.positions || []);
        } catch (err) {
            console.error('Error loading data:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleBot = async () => {
        try {
            const result = await api.toggleBot(token);
            setStats({ ...stats, bot_active: result.is_active });
        } catch (err) {
            console.error('Error toggling bot:', err);
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
