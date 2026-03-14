from typing import Optional

class OrderManager:
    def __init__(self, client):
        self.client = client

    async def open_market_order(self, symbol: str, side: str, size: float) -> Optional[str]:
        """
        Envía orden de mercado. Retorna order_id si tiene éxito.
        """
        resp = await self.client.place_order(
            symbol=symbol,
            side=side,
            order_type='market',
            size=str(size)
        )
        if resp and resp.get('code') == '200000':
            order_id = resp['data']['orderId']
            return order_id
        return None

    async def close_position(self, symbol: str, size: float = None):
        """
        Cierra posición (asume que es de compra, vende). Si size=None, vende todo.
        """
        if size is None:
            # Obtener tamaño de la posición desde otro lado (portfolio)
            # Simplificado: requerir size explícito
            raise ValueError("Size required to close")
        return await self.open_market_order(symbol, 'sell', size)
