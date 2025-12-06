#!/bin/bash
# ============================================================
# Setup Google Drive API para Sincronização de Documentos
# ============================================================

set -e

echo "🔧 Instalando rclone..."

# Instalar rclone no container Odoo
docker exec odoo_modules-web-1 bash -c "
    apt-get update && \
    apt-get install -y curl unzip && \
    curl https://rclone.org/install.sh | bash
"

echo "✅ Rclone instalado!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PRÓXIMOS PASSOS MANUAIS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Acesse: https://console.cloud.google.com/"
echo "2. Crie novo projeto: 'GZ Consultoria Documentos'"
echo "3. Ative Google Drive API"
echo "4. Crie credenciais OAuth 2.0:"
echo "   - Tipo: Desktop app"
echo "   - Baixe JSON de credenciais"
echo ""
echo "5. Configure rclone:"
echo "   docker exec -it odoo_modules-web-1 rclone config"
echo ""
echo "   - Escolha: n (new remote)"
echo "   - Nome: gzdrive"
echo "   - Storage: 15 (Google Drive)"
echo "   - client_id: (cole do JSON baixado)"
echo "   - client_secret: (cole do JSON baixado)"
echo "   - scope: 1 (Full access)"
echo "   - root_folder_id: (deixe vazio)"
echo "   - service_account_file: (deixe vazio)"
echo "   - Edit advanced config: n"
echo "   - Use web browser: n (use token manual)"
echo ""
echo "6. Teste a conexão:"
echo "   docker exec odoo_modules-web-1 rclone lsd gzdrive:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
