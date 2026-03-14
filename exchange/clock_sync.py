import aiohttp

async def get_server_time(base_url: str) -> int:
    """Obtiene el timestamp del servidor de KuCoin en milisegundos."""
    url = f"{base_url}/api/v1/timestamp"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return int(data['data'])
