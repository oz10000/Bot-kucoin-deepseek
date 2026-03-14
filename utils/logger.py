import logging
import sys

def setup_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Handler para archivo (opcional)
    fh = logging.FileHandler('bot.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
