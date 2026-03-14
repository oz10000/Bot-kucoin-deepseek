import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

class Settings(BaseModel):
    kucoin_api_key: str = Field(..., env='KUCOIN_API_KEY')
    kucoin_api_secret: str = Field(..., env='KUCOIN_API_SECRET')
    kucoin_api_passphrase: str = Field(..., env='KUCOIN_API_PASSPHRASE')
    kucoin_base_url: str = Field('https://openapi-sandbox.kucoin.com', env='KUCOIN_BASE_URL')
    
    symbols: List[str] = Field(default_factory=lambda: ['BTC-USDT', 'ETH-USDT'], env='SYMBOLS')
    timeframe: str = Field('3min', env='TIMEFRAME')
    scan_interval: int = Field(60, env='SCAN_INTERVAL')
    
    risk_per_trade: float = Field(0.01, env='RISK_PER_TRADE')
    atr_period: int = Field(14, env='ATR_PERIOD')
    atr_multiplier: float = Field(1.5, env='ATR_MULTIPLIER')
    tp_ratio: float = Field(0.3, env='TP_RATIO')
    trailing_stop_activation: float = Field(0.01, env='TRAILING_STOP_ACTIVATION')
    trailing_stop_distance: float = Field(0.005, env='TRAILING_STOP_DISTANCE')
    
    initial_capital: float = Field(1000, env='INITIAL_CAPITAL')

    class Config:
        env_file = '.env'
        extra = 'ignore'

settings = Settings()
