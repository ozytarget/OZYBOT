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
                    
                    // Calcular color basado en precio anterior
                    setPrice(prevPriceValue => {
                        if (prevPriceValue !== null && prevPriceValue !== priceData.price) {
                            if (priceData.price > prevPriceValue) {
                                setColor('green');
                            } else if (priceData.price < prevPriceValue) {
                                setColor('red');
                            }
                        } else if (prevPriceValue === null) {
                            setColor('gray');
                        }
                        
                        setPrevPrice(priceData.price);
                        return priceData.price;
                    });
                } else {
                    console.warn(`No price data for ticker: ${ticker}`);
                }
            } catch (err) {
                console.error('Error fetching real-time price:', err);
            }
        };

        // Fetch inmediato
        fetchPrice();

        // Actualizar cada 2 segundos (más eficiente)
        const interval = setInterval(fetchPrice, 2000);

        return () => clearInterval(interval);
    }, [ticker, api, token]);

    if (!price) {
        return <span className="price-ticker loading">--</span>;
    }

    return (
        <span className={`price-ticker ${color}`}>
            ${price.toFixed(2)}
        </span>
    );
}
