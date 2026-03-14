import pandas as pd
from strategy.base import BaseStrategy
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmaCrossStrategy(BaseStrategy):
    def __init__(self, fast_period=9, slow_period=21):
        self.fast_period = fast_period
        self.slow_period = slow_period

    async def generate_signal(self, symbol: str, market_data) -> Optional[Dict[str, Any]]:
        # Obtener velas (se asume que market_data tiene método get_candles)
        candles = await market_data.get_candles(symbol, '3min')  # timeframe fijo o configurable
        if not candles or 'data' not in candles:
            return None

        df = pd.DataFrame(candles['data'], columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
        df['close'] = df['close'].astype(float)
        df['fast_ema'] = df['close'].ewm(span=self.fast_period).mean()
        df['slow_ema'] = df['close'].ewm(span=self.slow_period).mean()

        # Condición de compra: fast_ema cruza arriba slow_ema
        if df['fast_ema'].iloc[-2] <= df['slow_ema'].iloc[-2] and df['fast_ema'].iloc[-1] > df['slow_ema'].iloc[-1]:
            price = float(df['close'].iloc[-1])
            edge = 0.004  # ejemplo fijo, podría calcularse con ATR o volatilidad
            logger.info(f"Buy signal for {symbol} at {price}")
            return {
                'symbol': symbol,
                'side': 'buy',
                'price': price,
                'edge': edge,
                'metadata': {'fast_ema': df['fast_ema'].iloc[-1], 'slow_ema': df['slow_ema'].iloc[-1]}
            }
        return None
