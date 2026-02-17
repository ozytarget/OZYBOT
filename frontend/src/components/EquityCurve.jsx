import React, { useState, useEffect } from 'react';
import './EquityCurve.css';

/**
 * Equity Curve Sparkline
 * Muestra el crecimiento del balance en las últimas 24 horas
 */
export default function EquityCurve({ api, token }) {
    const [equityData, setEquityData] = useState([]);
    const [trend, setTrend] = useState('neutral');

    useEffect(() => {
        const fetchEquityCurve = async () => {
            try {
                const response = await api.getEquityCurve(token, 24);
                
                if (response.success && response.equity_curve.length > 0) {
                    setEquityData(response.equity_curve);
                    
                    // Determinar tendencia
                    const first = response.equity_curve[0].equity;
                    const last = response.equity_curve[response.equity_curve.length - 1].equity;
                    
                    if (last > first) {
                        setTrend('up');
                    } else if (last < first) {
                        setTrend('down');
                    } else {
                        setTrend('neutral');
                    }
                }
            } catch (err) {
                console.error('Error fetching equity curve:', err);
            }
        };

        fetchEquityCurve();
        const interval = setInterval(fetchEquityCurve, 60000); // Cada 1 minuto

        return () => clearInterval(interval);
    }, []);

    if (equityData.length === 0) {
        return <div className="equity-curve-empty">No data</div>;
    }

    // Normalizar datos para SVG
    const values = equityData.map(d => d.equity);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    const width = 200;
    const height = 50;
    const padding = 5;

    // Crear puntos para el path
    const points = values.map((value, index) => {
        const x = (index / (values.length - 1)) * (width - 2 * padding) + padding;
        const y = height - padding - ((value - min) / range) * (height - 2 * padding);
        return `${x},${y}`;
    }).join(' ');

    const pathD = `M ${points}`;

    return (
        <div className={`equity-curve ${trend}`}>
            <svg width={width} height={height}>
                <polyline
                    points={points}
                    fill="none"
                    stroke={trend === 'up' ? '#28a745' : trend === 'down' ? '#dc3545' : '#6c757d'}
                    strokeWidth="2"
                />
                
                {/* Puntos en cada medición */}
                {values.map((value, index) => {
                    const x = (index / (values.length - 1)) * (width - 2 * padding) + padding;
                    const y = height - padding - ((value - min) / range) * (height - 2 * padding);
                    return (
                        <circle
                            key={index}
                            cx={x}
                            cy={y}
                            r="2"
                            fill={trend === 'up' ? '#28a745' : trend === 'down' ? '#dc3545' : '#6c757d'}
                        />
                    );
                })}
            </svg>
            <div className="equity-info">
                <span className="equity-label">24h Change</span>
                <span className={`equity-change ${trend}`}>
                    {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '−'} 
                    ${(values[values.length - 1] - values[0]).toFixed(2)}
                </span>
            </div>
        </div>
    );
}
