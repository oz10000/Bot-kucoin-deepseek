from typing import Dict, Optional

class PositionManager:
    def __init__(self):
        self.positions: Dict[str, Dict] = {}  # symbol -> {entry, size, sl, tp, order_id, ...}

    def open(self, symbol: str, entry: float, size: float, sl: float, tp: float, order_id: str = None):
        self.positions[symbol] = {
            'entry': entry,
            'size': size,
            'sl': sl,
            'tp': tp,
            'order_id': order_id,
            'highest_price': entry  # para trailing stop
        }

    def close(self, symbol: str):
        if symbol in self.positions:
            del self.positions[symbol]

    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions

    def get(self, symbol: str) -> Optional[Dict]:
        return self.positions.get(symbol)

    def update_sl(self, symbol: str, new_sl: float):
        if symbol in self.positions:
            self.positions[symbol]['sl'] = new_sl

    def update_highest(self, symbol: str, price: float):
        if symbol in self.positions and price > self.positions[symbol]['highest_price']:
            self.positions[symbol]['highest_price'] = price

    def symbols(self) -> list:
        return list(self.positions.keys())
