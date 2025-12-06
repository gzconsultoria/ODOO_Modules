#!/bin/bash

# ============================================
# ODOO 19 - SCRIPT DE DEPLOY PARA CONTABO VPS
# ============================================
# Uso: bash deploy_to_contabo.sh
# ============================================

set -e

echo "🚀 ODOO 19 - Deploy para Produção (Contabo)"
echo "============================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Este script deve ser executado como root (sudo)${NC}"
    exit 1
fi

# Variáveis (EDITAR ANTES DE EXECUTAR)
DOMAIN="seu-dominio.com.br"
EMAIL="admin@seu-dominio.com.br"
SSH_PORT="22"  # Mude para porta customizada se configurou
DEPLOY_DIR="/opt/odoo"

echo -e "${YELLOW}📋 Configurações:${NC}"
echo "   Domínio: ${DOMAIN}"
echo "   Email: ${EMAIL}"
echo "   Diretório: ${DEPLOY_DIR}"
echo ""
read -p "Confirma as configurações acima? (s/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}Deploy cancelado${NC}"
    exit 1
fi

# ============================================
# PASSO 1: ATUALIZAR SISTEMA
# ============================================
echo -e "${GREEN}[1/10] Atualizando sistema operacional...${NC}"
apt update && apt upgrade -y
apt install -y curl wget git vim ufw fail2ban

# ============================================
# PASSO 2: CONFIGURAR FIREWALL
# ============================================
echo -e "${GREEN}[2/10] Configurando firewall (UFW)...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ${SSH_PORT}/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
ufw status

# ============================================
# PASSO 3: INSTALAR DOCKER
# ============================================
echo -e "${GREEN}[3/10] Instalando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
else
    echo "✅ Docker já instalado"
fi

# ============================================
# PASSO 4: INSTALAR DOCKER COMPOSE
# ============================================
echo -e "${GREEN}[4/10] Instalando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose já instalado"
fi
docker-compose --version

# ============================================
# PASSO 5: CRIAR ESTRUTURA DE DIRETÓRIOS
# ============================================
echo -e "${GREEN}[5/10] Criando estrutura de diretórios...${NC}"
mkdir -p ${DEPLOY_DIR}/{addons,backups,logs,ssl,scripts}
mkdir -p ${DEPLOY_DIR}/backups/{database,filestore}

# ============================================
# PASSO 6: CONFIGURAR VARIÁVEIS DE AMBIENTE
# ============================================
echo -e "${GREEN}[6/10] Configurando variáveis de ambiente...${NC}"
if [ ! -f ${DEPLOY_DIR}/.env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "   Copie .env.production.template e edite as senhas:"
    echo "   scp .env.production root@servidor:${DEPLOY_DIR}/.env"
    echo ""
    read -p "Deseja criar um .env básico agora? (s/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        cat > ${DEPLOY_DIR}/.env << EOF
POSTGRES_PASSWORD=$(openssl rand -base64 32)
ODOO_ADMIN_PASSWORD=$(openssl rand -base64 32)
DOMAIN=${DOMAIN}
EMAIL_ADMIN=${EMAIL}
EOF
        echo "✅ Arquivo .env criado com senhas aleatórias"
        echo "   IMPORTANTE: Anote as senhas em local seguro!"
        cat ${DEPLOY_DIR}/.env
        sleep 5
    else
        echo -e "${RED}❌ Deploy interrompido - configure .env primeiro${NC}"
        exit 1
    fi
fi

# ============================================
# PASSO 7: OBTER CERTIFICADO SSL (Let's Encrypt)
# ============================================
echo -e "${GREEN}[7/10] Configurando SSL com Let's Encrypt...${NC}"
read -p "Deseja configurar SSL agora? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    # Instalar certbot
    apt install -y certbot
    
    # Parar serviços que usam porta 80
    systemctl stop apache2 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true
    
    # Obter certificado
    certbot certonly --standalone \
        -d ${DOMAIN} \
        --email ${EMAIL} \
        --agree-tos \
        --non-interactive
    
    # Copiar certificados para diretório SSL
    cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${DEPLOY_DIR}/ssl/
    cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${DEPLOY_DIR}/ssl/
    
    echo "✅ Certificado SSL configurado"
else
    echo "⚠️  Usando HTTP (não recomendado para produção)"
fi

# ============================================
# PASSO 8: COPIAR MÓDULOS CUSTOMIZADOS
# ============================================
echo -e "${GREEN}[8/10] Aguardando upload dos módulos...${NC}"
echo "   Execute no seu computador local:"
echo "   scp -r gz_finance_* root@${DOMAIN}:${DEPLOY_DIR}/addons/"
echo ""
read -p "Pressione ENTER após copiar os módulos..."

# Verificar se módulos foram copiados
if [ ! -d "${DEPLOY_DIR}/addons/gz_finance_core" ]; then
    echo -e "${RED}❌ Módulos não encontrados em ${DEPLOY_DIR}/addons/${NC}"
    exit 1
fi
echo "✅ Módulos encontrados"

# ============================================
# PASSO 9: RESTAURAR BANCO DE DADOS
# ============================================
echo -e "${GREEN}[9/10] Restaurar banco de dados...${NC}"
read -p "Deseja restaurar backup do banco agora? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "   Execute no seu computador local:"
    echo "   scp gzcon_backup.dump root@${DOMAIN}:${DEPLOY_DIR}/backups/database/"
    echo ""
    read -p "Pressione ENTER após copiar o backup..."
    
    # Iniciar apenas o PostgreSQL
    cd ${DEPLOY_DIR}
    docker-compose up -d db
    sleep 10
    
    # Criar banco e restaurar
    BACKUP_FILE=$(ls -t ${DEPLOY_DIR}/backups/database/*.dump | head -1)
    docker exec -i postgres_production createdb -U odoo gzcon
    docker exec -i postgres_production pg_restore -U odoo -d gzcon < ${BACKUP_FILE}
    
    echo "✅ Banco de dados restaurado"
else
    echo "⚠️  Banco será criado vazio na primeira execução"
fi

# ============================================
# PASSO 10: INICIAR SERVIÇOS
# ============================================
echo -e "${GREEN}[10/10] Iniciando serviços Odoo...${NC}"
cd ${DEPLOY_DIR}
docker-compose up -d

# Aguardar inicialização
echo "⏳ Aguardando Odoo inicializar (60s)..."
sleep 60

# Verificar status
docker-compose ps

echo ""
echo -e "${GREEN}✅ DEPLOY CONCLUÍDO!${NC}"
echo "============================================"
echo "   🌐 Acesse: https://${DOMAIN}"
echo "   📧 Email Admin: ${EMAIL}"
echo "   📁 Diretório: ${DEPLOY_DIR}"
echo ""
echo "📋 Próximos passos:"
echo "   1. Testar acesso ao Odoo"
echo "   2. Instalar módulos gz_finance_*"
echo "   3. Configurar backup automático (cron)"
echo "   4. Monitorar logs: docker-compose logs -f"
echo ""
echo "🔐 Segurança:"
echo "   - Senhas estão em: ${DEPLOY_DIR}/.env"
echo "   - Configurar 2FA no Odoo"
echo "   - Revisar regras do firewall"
echo "============================================"
