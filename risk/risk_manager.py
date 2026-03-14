import numpy as np
import pandas as pd
from typing import Tuple

class RiskManager:
    def __init__(self, risk_per_trade: float, atr_multiplier: float, tp_ratio: float, initial_capital: float):
        self.risk_per_trade = risk_per_trade
        self.atr_multiplier = atr_multiplier
        self.tp_ratio = tp_ratio
        self.capital = initial_capital  # podría actualizarse dinámicamente

    async def compute_atr(self, symbol: str, market_data, period: int = 14) -> float:
        """Calcula ATR usando velas recientes."""
        candles = await market_data.get_candles(symbol, '3min')  # timeframe fijo
        if not candles or 'data' not in candles:
            return 0.0

        df = pd.DataFrame(candles['data'], columns=['time', 'open', 'close', 'high', 'low', 'volume', 'turnover'])
        df[['high', 'low', 'close']] = df[['high', 'low', 'close']].astype(float)
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        atr = df['tr'].rolling(period).mean().iloc[-1]
        return atr

    async def compute_position_size(self, symbol: str, entry: float, sl: float) -> float:
        """
        Calcula tamaño de posición basado en riesgo.
        risk_amount = capital * risk_per_trade
        size = risk_amount / abs(entry - sl)
        """
        risk_amount = self.capital * self.risk_per_trade
        price_risk = abs(entry - sl)
        if price_risk == 0:
            return 0.0
        size = risk_amount / price_risk
        # Ajustar a decimales según símbolo (simplificado)
        return round(size, 6)

    async def compute_levels(self, symbol: str, entry: float, edge: float, market_data) -> Tuple[float, float, float]:
        """
        Retorna (stop_loss, take_profit, size)
        Usa ATR para SL y TP basado en edge.
        """
        atr = await self.compute_atr(symbol, market_data)
        if atr == 0:
            # fallback a porcentaje
            sl = entry - edge
            tp = entry + edge * self.tp_ratio
        else:
            sl = entry - self.atr_multiplier * atr
            tp = entry + self.atr_multiplier * atr * self.tp_ratio

        size = await self.compute_position_size(symbol, entry, sl)
        return sl, tp, size
