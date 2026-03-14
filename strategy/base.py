from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStrategy(ABC):
    @abstractmethod
    async def generate_signal(self, symbol: str, market_data: Any) -> Optional[Dict[str, Any]]:
        """
        Retorna una señal con al menos:
        - symbol: str
        - side: 'buy' or 'sell'
        - price: float (precio de entrada aproximado)
        - size: float (cantidad a operar)
        - edge: float (confianza o ganancia esperada, para ranking)
        - metadata: dict (opcional)
        """
        pass
