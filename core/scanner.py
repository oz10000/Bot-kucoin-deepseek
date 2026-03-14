import asyncio
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, symbols: List[str], market_data, strategy):
        self.symbols = symbols
        self.market_data = market_data
        self.strategy = strategy

    async def scan(self) -> List[Dict[str, Any]]:
        signals = []
        for symbol in self.symbols:
            try:
                signal = await self.strategy.generate_signal(symbol, self.market_data)
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        return signals
