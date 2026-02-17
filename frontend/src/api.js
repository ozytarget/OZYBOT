// Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : import.meta.env.VITE_API_URL || 'https://botz.up.railway.app';

export const api = {
    // Auth endpoints
    register: async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return response.json();
    },

    login: async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return response.json();
    },

    getMe: async (token) => {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    // Dashboard endpoints
    getStats: async (token) => {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    getPositions: async (token) => {
        const response = await fetch(`${API_BASE_URL}/dashboard/positions`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    toggleBot: async (token) => {
        const response = await fetch(`${API_BASE_URL}/dashboard/toggle-bot`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to toggle bot');
        }
        return response.json();
    },

    getWebhooks: async (token) => {
        const response = await fetch(`${API_BASE_URL}/dashboard/webhooks`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    closePosition: async (token, positionId) => {
        const response = await fetch(`${API_BASE_URL}/dashboard/close-position/${positionId}`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to close position');
        }
        return response.json();
    },

    // Settings endpoints
    getConfig: async (token) => {
        const response = await fetch(`${API_BASE_URL}/settings/config`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    updateConfig: async (token, config) => {
        const response = await fetch(`${API_BASE_URL}/settings/config`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        return response.json();
    },

    getBroker: async (token) => {
        const response = await fetch(`${API_BASE_URL}/settings/broker`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    updateBroker: async (token, broker) => {
        const response = await fetch(`${API_BASE_URL}/settings/broker`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(broker)
        });
        return response.json();
    }
};
