#!/bin/bash

# ============================================
# DEPLOY AUTOMÁTICO ODOO 19 - CONTABO
# ============================================

set -e

SERVER_IP="84.247.177.153"
SERVER_USER="root"
SERVER_PASS="Geovane7184#"
DEPLOY_DIR="/opt/odoo"

echo "🚀 Iniciando deploy para Contabo: $SERVER_IP"

# Função para executar comando no servidor
remote_exec() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "$@"
}

# Função para copiar arquivos
remote_copy() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -r "$@"
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 1: Preparar servidor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    echo '✅ Atualizando sistema...'
    apt update -qq
    apt install -y sshpass curl wget git
    echo '✅ Sistema atualizado'
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 2: Instalar Docker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    if ! command -v docker &> /dev/null; then
        echo '📦 Instalando Docker...'
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
        rm get-docker.sh
        echo '✅ Docker instalado'
    else
        echo '✅ Docker já instalado'
    fi
    docker --version
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 3: Instalar Docker Compose"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    if ! command -v docker-compose &> /dev/null; then
        echo '📦 Instalando Docker Compose...'
        curl -L 'https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64' \
            -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        echo '✅ Docker Compose instalado'
    else
        echo '✅ Docker Compose já instalado'
    fi
    docker-compose --version
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 4: Criar estrutura de diretórios"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    mkdir -p $DEPLOY_DIR/{addons,backups,logs,scripts}
    echo '✅ Diretórios criados'
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 5: Copiar arquivos de configuração"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📤 Copiando .env..."
remote_copy deploy/config/.env.production $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/.env

echo "📤 Copiando docker-compose.yml..."
remote_copy deploy/config/docker-compose.production.yml $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/docker-compose.yml

echo "📤 Copiando odoo.conf..."
remote_copy deploy/config/odoo.conf $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/

echo "📤 Copiando backup.sh..."
remote_copy deploy/config/backup.sh $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/scripts/
remote_exec "chmod +x $DEPLOY_DIR/scripts/backup.sh"

echo "✅ Arquivos de configuração copiados"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 6: Copiar módulos customizados"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📤 Copiando gz_finance_core..."
remote_copy gz_finance_core/ $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/addons/

echo "📤 Copiando gz_finance_crm..."
remote_copy gz_finance_crm/ $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/addons/

echo "📤 Copiando gz_finance_docs..."
remote_copy gz_finance_docs/ $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/addons/

echo "✅ Módulos copiados"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 7: Copiar backup do banco de dados"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BACKUP_FILE=$(ls -t deploy/backups/*.dump | head -1)
echo "📤 Copiando backup: $(basename $BACKUP_FILE)"
remote_copy "$BACKUP_FILE" $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/backups/gzcon.dump

echo "✅ Backup copiado"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 8: Ajustar docker-compose para IP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    cd $DEPLOY_DIR
    # Remover nginx e certbot (usar IP direto na porta 8069)
    sed -i '/nginx:/,/^$/d' docker-compose.yml
    sed -i '/certbot:/,/^$/d' docker-compose.yml
    echo '✅ Docker Compose ajustado para acesso direto via IP'
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 9: Iniciar PostgreSQL e restaurar banco"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    cd $DEPLOY_DIR
    echo '🐘 Iniciando PostgreSQL...'
    docker-compose up -d db
    sleep 15
    
    echo '📊 Restaurando banco de dados...'
    docker exec -i postgres_production createdb -U odoo gzcon 2>/dev/null || true
    cat backups/gzcon.dump | docker exec -i postgres_production pg_restore -U odoo -d gzcon -v 2>&1 | tail -5
    
    echo '✅ Banco de dados restaurado'
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASSO 10: Iniciar Odoo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

remote_exec "
    cd $DEPLOY_DIR
    echo '🚀 Iniciando Odoo 19...'
    docker-compose up -d web
    sleep 20
    
    echo ''
    echo '📊 Status dos containers:'
    docker-compose ps
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Acesse o Odoo em:"
echo "   http://84.247.177.153:8069"
echo ""
echo "🔐 Credenciais:"
echo "   Database: gzcon"
echo "   Email: admin@gzconsultoria.com.br"
echo "   Password: (veja no arquivo .env.production)"
echo ""
echo "📋 Comandos úteis:"
echo "   Ver logs: ssh root@$SERVER_IP 'cd $DEPLOY_DIR && docker-compose logs -f web'"
echo "   Reiniciar: ssh root@$SERVER_IP 'cd $DEPLOY_DIR && docker-compose restart web'"
echo "   Status: ssh root@$SERVER_IP 'cd $DEPLOY_DIR && docker-compose ps'"
echo ""
