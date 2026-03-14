import asyncio
import json
import logging
import websockets
from typing import Callable, Dict, Any, Optional

logger = logging.getLogger(__name__)

class KuCoinWebSocket:
    def __init__(self, base_url: str, token: str, endpoint: str):
        """
        :param base_url: Ej. wss://ws-api-sandbox.kucoin.com
        :param token: Token obtenido de /api/v1/bullet-public o /api/v1/bullet-private
        :param endpoint: Ej. "/endpoint" (se concatena)
        """
        self.base_url = base_url
        self.token = token
        self.endpoint = endpoint
        self.ws = None
        self.listeners = {}  # topic -> callback
        self._running = False

    async def connect(self):
        url = f"{self.base_url}{self.endpoint}?token={self.token}"
        self.ws = await websockets.connect(url)
        self._running = True
        logger.info(f"WebSocket connected to {url}")

    async def subscribe(self, topic: str, callback: Callable, private: bool = False):
        """
        Envía mensaje de suscripción.
        :param topic: Ej. "/market/ticker:BTC-USDT" o "/spotMarket/tradeOrders"
        :param callback: Función asíncrona que recibe el mensaje.
        :param private: Si es True, requiere autenticación (se maneja en el token).
        """
        if topic not in self.listeners:
            self.listeners[topic] = []
        self.listeners[topic].append(callback)

        subscribe_msg = {
            "id": str(asyncio.get_event_loop().time()),
            "type": "subscribe",
            "topic": topic,
            "privateChannel": private,
            "response": True
        }
        await self.ws.send(json.dumps(subscribe_msg))
        # Esperar confirmación (opcional)
        resp = await self.ws.recv()
        logger.info(f"Subscription response: {resp}")

    async def listen(self):
        while self._running:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                # Verificar si es mensaje de datos
                if 'topic' in data and 'data' in data:
                    topic = data['topic']
                    if topic in self.listeners:
                        for callback in self.listeners[topic]:
                            asyncio.create_task(callback(data['data']))
                elif data.get('type') == 'pong':
                    # ignorar
                    pass
                else:
                    logger.debug(f"Unhandled WebSocket message: {data}")
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting...")
                await self.reconnect()
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)

    async def reconnect(self):
        self._running = False
        if self.ws:
            await self.ws.close()
        await asyncio.sleep(2)
        await self.connect()
        # Re-suscribir a todos los topics
        for topic in self.listeners.keys():
            # No podemos reenviar callbacks, pero podemos re-suscribir
            await self.subscribe(topic, lambda x: None)  # Placeholder, luego se maneja con listeners
        self._running = True
        asyncio.create_task(self.listen())

    async def close(self):
        self._running = False
        if self.ws:
            await self.ws.close()

    @staticmethod
    async def get_public_token(base_url: str) -> str:
        """Obtiene token público para WebSocket."""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/api/v1/bullet-public") as resp:
                data = await resp.json()
                return data['data']['token']

    @staticmethod
    async def get_private_token(api_key, api_secret, passphrase, base_url: str) -> str:
        """Obtiene token privado (requiere autenticación)."""
        # Similar a bullet-public pero con headers de autenticación
        # Implementación simplificada: usar cliente REST para obtener token
        from exchange.kucoin_client import KucoinClient
        client = KucoinClient(api_key, api_secret, passphrase, base_url)
        resp = await client._request("POST", "/api/v1/bullet-private", signed=True)
        return resp['data']['token']
