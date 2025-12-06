#!/bin/bash
# ============================================================
# Cron Job - Sincronização Automática com Google Drive
# Executa a cada 6 horas
# ============================================================

set -e

LOG_FILE="/var/log/odoo/gdrive_sync_cron.log"

echo "========================================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Iniciando sync job" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Executar script Python de sincronização
python3 /opt/odoo/scripts/sync_to_gdrive.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ Sync concluído com sucesso" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ Sync falhou com código $EXIT_CODE" >> "$LOG_FILE"
fi

# Rotacionar logs (manter últimos 30 dias)
find /var/log/odoo -name "gdrive_sync*.log" -mtime +30 -delete

echo "" >> "$LOG_FILE"
