import asyncio
import logging
from config.settings import settings
from config.constants import TIMEFRAME_TO_SECONDS
from utils.logger import setup_logger

from exchange.kucoin_client import KucoinClient
from exchange.websocket_client import KuCoinWebSocket
from market.market_data import MarketData
from strategy.ema_cross import EmaCrossStrategy
from risk.risk_manager import RiskManager
from risk.trailing_stop import TrailingStop
from portfolio.position_manager import PositionManager
from execution.order_manager import OrderManager
from execution.order_state import OrderStateManager
from core.scanner import Scanner
from core.engine import TradingEngine

logger = setup_logger(__name__)

async def main():
    logger.info("Starting KuCoin trading bot")

    # Inicializar cliente REST
    rest_client = KucoinClient(
        api_key=settings.kucoin_api_key,
        api_secret=settings.kucoin_api_secret,
        passphrase=settings.kucoin_api_passphrase,
        base_url=settings.kucoin_base_url
    )

    # Inicializar market data
    market_data = MarketData(rest_client)

    # Inicializar estrategia
    strategy = EmaCrossStrategy()

    # Inicializar scanner
    scanner = Scanner(settings.symbols, market_data, strategy)

    # Inicializar risk manager
    risk_manager = RiskManager(
        risk_per_trade=settings.risk_per_trade,
        atr_multiplier=settings.atr_multiplier,
        tp_ratio=settings.tp_ratio,
        initial_capital=settings.initial_capital
    )

    # Inicializar order manager y order state
    order_manager = OrderManager(rest_client)
    order_state = OrderStateManager(rest_client)

    # Inicializar portfolio
    portfolio = PositionManager()

    # Inicializar trailing stop (opcional)
    trailing_stop = TrailingStop(
        activation_pct=settings.trailing_stop_activation,
        distance_pct=settings.trailing_stop_distance
    )

    # Crear motor
    engine = TradingEngine(
        config=settings,
        market_data=market_data,
        scanner=scanner,
        risk_manager=risk_manager,
        order_manager=order_manager,
        order_state=order_state,
        portfolio=portfolio,
        trailing_stop=trailing_stop
    )

    # Opcional: iniciar WebSocket para datos en tiempo real (mejora)
    # Aquí solo mostramos cómo se haría, pero no lo integramos completamente en este ejemplo
    # ws_token = await KuCoinWebSocket.get_public_token(settings.kucoin_base_url)
    # ws = KuCoinWebSocket(settings.kucoin_base_url.replace('https', 'wss'), ws_token, '/endpoint')
    # await ws.connect()
    # asyncio.create_task(ws.listen())
    # await ws.subscribe(f"/market/candle:{settings.symbols[0]}_{settings.timeframe}", market_data.update_from_websocket)

    try:
        await engine.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())
