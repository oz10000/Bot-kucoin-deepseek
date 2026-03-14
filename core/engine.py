import asyncio
import logging
from typing import Optional

from risk.trailing_stop import TrailingStop

logger = logging.getLogger(__name__)

class TradingEngine:
    def __init__(self, config, market_data, scanner, risk_manager, order_manager,
                 order_state, portfolio, trailing_stop: Optional[TrailingStop] = None):
        self.config = config
        self.market_data = market_data
        self.scanner = scanner
        self.risk = risk_manager
        self.orders = order_manager
        self.order_state = order_state
        self.portfolio = portfolio
        self.trailing_stop = trailing_stop
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Trading engine started")
        # Tareas concurrentes
        await asyncio.gather(
            self.scan_loop(),
            self.monitor_positions_loop(),
            self.trailing_stop_loop()
        )

    async def stop(self):
        self._running = False
        logger.info("Trading engine stopped")

    async def scan_loop(self):
        while self._running:
            try:
                signals = await self.scanner.scan()
                if signals:
                    # Ordenar por edge (mayor primero)
                    signals.sort(key=lambda x: x['edge'], reverse=True)
                    for signal in signals:
                        await self.process_signal(signal)
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
            await asyncio.sleep(self.config.scan_interval)

    async def process_signal(self, signal):
        symbol = signal['symbol']
        # Verificar si ya tenemos posición o orden pendiente
        if self.portfolio.has_position(symbol):
            logger.debug(f"Signal for {symbol} ignored: already in position")
            return
        if self.order_state.is_order_pending(symbol):
            logger.debug(f"Signal for {symbol} ignored: order pending")
            return

        entry = signal['price']
        edge = signal['edge']
        side = signal['side']

        # Calcular SL, TP y tamaño
        sl, tp, size = await self.risk.compute_levels(symbol, entry, edge, self.market_data)
        if size <= 0:
            logger.warning(f"Invalid size for {symbol}: {size}")
            return

        # Enviar orden
        order_id = await self.orders.open_market_order(symbol, side, size)
        if order_id:
            logger.info(f"Order placed for {symbol} {side} {size} @ market, order_id={order_id}")
            # Registrar en order state
            await self.order_state.track_order(order_id, symbol, side, size)
            # Registrar en portfolio (asumimos que se ejecutará pronto, pero el estado real vendrá después)
            self.portfolio.open(symbol, entry, size, sl, tp, order_id)
        else:
            logger.error(f"Failed to place order for {symbol}")

    async def monitor_positions_loop(self):
        """Verifica si alguna posición alcanzó SL o TP (simplificado)."""
        while self._running:
            for symbol in self.portfolio.symbols():
                pos = self.portfolio.get(symbol)
                # Obtener precio actual (de market_data o WebSocket)
                # Simplificado: usar última vela
                try:
                    candles = await self.market_data.get_candles(symbol, self.config.timeframe)
                    if candles and 'data' in candles:
                        current_price = float(candles['data'][-1][2])  # close price
                        # Verificar SL/TP
                        if current_price <= pos['sl']:
                            logger.info(f"Stop loss hit for {symbol} at {current_price}")
                            await self.close_position(symbol, pos['size'])
                        elif current_price >= pos['tp']:
                            logger.info(f"Take profit hit for {symbol} at {current_price}")
                            await self.close_position(symbol, pos['size'])
                except Exception as e:
                    logger.error(f"Error monitoring {symbol}: {e}")
            await asyncio.sleep(5)  # cada 5 segundos

    async def trailing_stop_loop(self):
        if not self.trailing_stop:
            return
        while self._running:
            for symbol in self.portfolio.symbols():
                pos = self.portfolio.get(symbol)
                # Obtener precio actual
                try:
                    candles = await self.market_data.get_candles(symbol, self.config.timeframe)
                    if candles and 'data' in candles:
                        current_price = float(candles['data'][-1][2])
                        # Actualizar highest price
                        self.portfolio.update_highest(symbol, current_price)
                        # Calcular nuevo SL
                        new_sl = self.trailing_stop.update(
                            pos['entry'],
                            current_price,
                            pos['sl']
                        )
                        if new_sl > pos['sl']:
                            logger.info(f"Updating trailing stop for {symbol}: {pos['sl']} -> {new_sl}")
                            self.portfolio.update_sl(symbol, new_sl)
                except Exception as e:
                    logger.error(f"Error in trailing stop for {symbol}: {e}")
            await asyncio.sleep(5)

    async def close_position(self, symbol: str, size: float):
        order_id = await self.orders.close_position(symbol, size)
        if order_id:
            logger.info(f"Close order placed for {symbol}, order_id={order_id}")
            # Eliminar de portfolio (o esperar confirmación)
            self.portfolio.close(symbol)
        else:
            logger.error(f"Failed to close position for {symbol}")
