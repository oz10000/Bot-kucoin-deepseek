import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MarketData:
    def __init__(self, rest_client):
        self.rest_client = rest_client
        self._candle_cache = {}  # symbol -> última vela

    async def get_candles(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Obtiene velas vía REST (últimas 100 por defecto)."""
        data = await self.rest_client.get_candles(symbol, timeframe)
        return data

    async def update_from_websocket(self, symbol: str, candle_data: Dict):
        """Actualiza caché con datos de WebSocket (opcional)."""
        self._candle_cache[symbol] = candle_data
