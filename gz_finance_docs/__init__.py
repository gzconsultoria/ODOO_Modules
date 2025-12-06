import logging

_logger = logging.getLogger(__name__)

_logger.info("=" * 80)
_logger.info("🔵 INICIANDO CARREGAMENTO DO MÓDULO gz_finance_docs")
_logger.info("=" * 80)

from . import models

_logger.info("✅ Modelos carregados com sucesso")