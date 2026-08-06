"""
Kozponti logging beallitas a projekthez.

A print() helyett ezt a modult hasznaljuk mindenhol:

    from honeypot.logger import get_logger
    logger = get_logger(__name__)

    logger.info("Csatlakozva a brokerhez")
    logger.warning("Gyanus uzenet erkezett: %s", topic)

Minden log egyszerre kerul kiirasra a konzolra ES a logs/honeypot.log fajlba.
"""

import logging
import sys

from honeypot.config import LOG_DIR, LOG_FILE

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "honeypot") -> logging.Logger:
    """Letrehoz (vagy visszaad, ha mar letezik) egy konfiguralt loggert.

    Console handler: minden INFO es afolotti szintu uzenet megjelenik a terminalban.
    File handler: ugyanezek az uzenetek bekerulnek a logs/honeypot.log fajlba is.
    """
    logger = logging.getLogger(name)

    # Ha a loggernek mar vannak handlerei, ne adjunk hozza ujakat
    # (elkeruljuk a duplikalt naploejegyzeseket tobb import eseten).
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
