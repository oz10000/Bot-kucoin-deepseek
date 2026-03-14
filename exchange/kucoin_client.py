import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any
from utils.retry import async_retry
from utils.rate_limiter import RateLimiter
from exchange.auth import sign_request
import logging

logger = logging.getLogger(__name__)

class KucoinClient:
    def __init__(self, api_key: str, api_secret: str, passphrase: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = base_url
        # Límites de KuCoin: 30 requests/segundo para endpoints públicos, 45 para privados
        self.public_limiter = RateLimiter(max_calls=30, period=1)
        self.private_limiter = RateLimiter(max_calls=45, period=1)

    def _headers(self, method: str, endpoint: str, body: str = "") -> Dict[str, str]:
        timestamp = str(int(asyncio.get_event_loop().time() * 1000))
        signature = sign_request(self.api_secret, timestamp, method, endpoint, body)
        return {
            "KC-API-KEY": self.api_key,
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

    async def _request(self, method: str, endpoint: str, signed: bool = False, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = self.base_url + endpoint
        body = json.dumps(data) if data else ""
        headers = self._headers(method, endpoint, body) if signed else {}

        # Aplicar rate limiting
        limiter = self.private_limiter if signed else self.public_limiter
        await limiter.acquire()

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, data=body) as resp:
                response_data = await resp.json()
                # Verificar código de éxito de KuCoin (code == "200000")
                if response_data.get('code') != '200000':
                    logger.error(f"KuCoin API error: {response_data}")
                    raise Exception(f"KuCoin API error: {response_data.get('msg')}")
                return response_data

    @async_retry(max_retries=3, exceptions=(aiohttp.ClientError, asyncio.TimeoutError))
    async def get_candles(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        endpoint = f"/api/v1/market/candles?type={timeframe}&symbol={symbol}"
        return await self._request("GET", endpoint, signed=False)

    @async_retry(max_retries=3)
    async def place_order(self, symbol: str, side: str, order_type: str, size: str, **kwargs) -> Dict[str, Any]:
        endpoint = "/api/v1/orders"
        data = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "size": size,
            **kwargs
        }
        return await self._request("POST", endpoint, signed=True, data=data)

    @async_retry(max_retries=3)
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        endpoint = f"/api/v1/orders/{order_id}"
        return await self._request("GET", endpoint, signed=True)

    @async_retry(max_retries=3)
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        endpoint = f"/api/v1/orders/{order_id}"
        return await self._request("DELETE", endpoint, signed=True)

    @async_retry(max_retries=3)
    async def get_accounts(self) -> Dict[str, Any]:
        endpoint = "/api/v1/accounts"
        return await self._request("GET", endpoint, signed=True)
