import React, { useState, useEffect } from 'react';
import './PriceTicker.css';

/**
 * Price Ticker con colores en tiempo real
 * Verde si sube, Rojo si baja, Gris si sin cambio
 */
export default function PriceTicker({ ticker, api, token }) {
    const [price, setPrice] = useState(null);
    const [color, setColor] = useState('gray');
    const [prevPrice, setPrevPrice] = useState(null);

    useEffect(() => {
        const fetchPrice = async () => {
            try {
                const response = await api.getRealtimePrices(token);
                if (response.success && response.prices[ticker]) {
                    const priceData = response.prices[ticker];
                    
                    if (prevPrice !== null) {
                        if (priceData.price > prevPrice) {
                            setColor('green');
                        } else if (priceData.price < prevPrice) {
                            setColor('red');
                        } else {
                            setColor('gray');
                        }
                    }
                    
                    setPrevPrice(priceData.price);
                    setPrice(priceData.price);
                }
            } catch (err) {
                console.error('Error fetching real-time price:', err);
            }
        };

        // Fetch inmediato
        fetchPrice();

        // Actualizar cada 1 segundo
        const interval = setInterval(fetchPrice, 1000);

        return () => clearInterval(interval);
    }, [ticker, prevPrice]);

    if (!price) {
        return <span className="price-ticker loading">--</span>;
    }

    return (
        <span className={`price-ticker ${color}`}>
            ${price.toFixed(2)}
        </span>
    );
}
