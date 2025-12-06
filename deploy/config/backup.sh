#!/bin/bash

# ============================================
# ODOO PRODUCTION BACKUP SCRIPT
# ============================================
# Uso: ./backup.sh
# Cron: 0 2 * * * /opt/odoo/scripts/backup.sh
# ============================================

set -e

# Configurações
BACKUP_DIR="/opt/odoo/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="gzcon"
CONTAINER_NAME="postgres_production"

# Criar diretório de backup
mkdir -p ${BACKUP_DIR}/database ${BACKUP_DIR}/filestore

echo "🔄 Iniciando backup - $(date)"

# 1. Backup do Banco de Dados PostgreSQL
echo "📦 Backup do banco de dados ${DB_NAME}..."
docker exec -t ${CONTAINER_NAME} pg_dump -U odoo -Fc ${DB_NAME} > \
    ${BACKUP_DIR}/database/${DB_NAME}_${TIMESTAMP}.dump

# 2. Backup do Filestore (arquivos enviados)
echo "📁 Backup do filestore..."
docker run --rm --volumes-from odoo_production \
    -v ${BACKUP_DIR}/filestore:/backup \
    alpine tar czf /backup/filestore_${TIMESTAMP}.tar.gz /var/lib/odoo/filestore

# 3. Verificar tamanho dos backups
DB_SIZE=$(du -h ${BACKUP_DIR}/database/${DB_NAME}_${TIMESTAMP}.dump | cut -f1)
FS_SIZE=$(du -h ${BACKUP_DIR}/filestore/filestore_${TIMESTAMP}.tar.gz | cut -f1)

echo "✅ Backup concluído:"
echo "   - Banco: ${DB_SIZE}"
echo "   - Filestore: ${FS_SIZE}"

# 4. Remover backups antigos
echo "🗑️  Limpando backups com mais de ${RETENTION_DAYS} dias..."
find ${BACKUP_DIR}/database -name "*.dump" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR}/filestore -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# 5. Listar backups disponíveis
echo "📋 Backups disponíveis:"
ls -lh ${BACKUP_DIR}/database/ | tail -5
ls -lh ${BACKUP_DIR}/filestore/ | tail -5

# 6. (Opcional) Enviar para cloud storage
# aws s3 sync ${BACKUP_DIR} s3://seu-bucket/odoo-backups/
# rclone sync ${BACKUP_DIR} gdrive:odoo-backups/

echo "✅ Backup finalizado - $(date)"
