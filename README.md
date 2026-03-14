# KuCoin Trading Bot (Profesional)

Bot asíncrono para operar en KuCoin con soporte para estrategias personalizadas, trailing stop, y manejo robusto de errores.

## Características
- Arquitectura modular y orientada a objetos.
- Cliente REST asíncrono con reintentos y rate limiting.
- WebSockets para datos en tiempo real (opcional).
- Gestión de estado de órdenes para evitar duplicados.
- Cálculo de SL/TP basado en ATR y riesgo por operación.
- Trailing stop automático.
- Logging completo.
- Configuración mediante variables de entorno.

## Requisitos
- Python 3.9+
- Instalar dependencias: `pip install -r requirements.txt`

## Configuración
1. Copiar `.env.example` a `.env` y completar credenciales.
2. Ajustar parámetros según preferencias.

## Ejecución
```bash
python main.py
