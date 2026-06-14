"""
Configuração centralizada de logs da aplicação.

Em produção, é fundamental ter logs persistidos em arquivo (para
diagnosticar problemas depois) e também no console (para acompanhar
em tempo real via `docker logs`, por exemplo).

Usamos RotatingFileHandler para que os arquivos de log não cresçam
indefinidamente: ao atingir 5MB, um novo arquivo é iniciado e os
antigos são mantidos até o limite de `backupCount`.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from app.core.config import settings

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging() -> None:
    """Configura o logger raiz da aplicação. Deve ser chamado uma única
    vez, na inicialização do app (em main.py)."""

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Reduz o ruído de logs de acesso do uvicorn em produção
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
