import React, { useState, useEffect } from 'react';
import './ConnectionStatus.css';

/**
 * LED Indicator de conexión con Exchange
 * Verde: Conectado | Rojo: Desconectado | Amarillo: Reconectando
 */
export default function ConnectionStatus({ api }) {
    const [status, setStatus] = useState('disconnected');
    const [source, setSource] = useState('Unknown');
    const [latency, setLatency] = useState(0);

    useEffect(() => {
        const checkConnection = async () => {
            try {
                const response = await api.getConnectionStatus();
                
                if (response.success) {
                    setStatus(response.status);
                    setSource(response.source);
                    setLatency(response.latency_ms);
                } else {
                    setStatus('disconnected');
                }
            } catch (err) {
                setStatus('error');
            }
        };

        checkConnection();
        const interval = setInterval(checkConnection, 3000);

        return () => clearInterval(interval);
    }, []);

    const getStatusIcon = () => {
        switch (status) {
            case 'connected':
                return '🟢';
            case 'disconnected':
                return '🔴';
            case 'error':
                return '🟠';
            default:
                return '⚪';
        }
    };

    return (
        <div className={`connection-status ${status}`}>
            <span className="status-led">{getStatusIcon()}</span>
            <span className="status-text">
                {source} - {status === 'connected' ? `Connected (${latency}ms)` : 'Disconnected'}
            </span>
        </div>
    );
}
