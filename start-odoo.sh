#!/bin/bash

###############################################################################
# Script para Iniciar Odoo 19 com Docker
# CRM Wealth Management
###############################################################################

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Odoo 19 + CRM Wealth Management - Docker           ║"
echo "║        Iniciando ambiente de desenvolvimento...           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado!${NC}"
    echo "Instale o Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não está instalado!${NC}"
    echo "Instale o Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar se a porta 8069 está livre
if lsof -Pi :8069 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Porta 8069 já está em uso!${NC}"
    read -p "Deseja parar o processo? (s/n) " STOP_PROCESS
    if [ "$STOP_PROCESS" = "s" ]; then
        PID=$(lsof -t -i:8069)
        kill -9 $PID 2>/dev/null || sudo kill -9 $PID
        echo -e "${GREEN}✅ Processo parado${NC}"
    else
        echo -e "${RED}❌ Não é possível continuar com a porta ocupada${NC}"
        exit 1
    fi
fi

# Criar diretório de config se não existir
mkdir -p config

echo ""
echo -e "${BLUE}🐳 Iniciando containers...${NC}"
echo ""

# Iniciar Docker Compose
docker compose up -d

echo ""
echo -e "${BLUE}⏳ Aguardando containers iniciarem...${NC}"
sleep 5

# Verificar status
if docker compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              ✅ Odoo 19 Iniciado com Sucesso!             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}📋 Informações de Acesso:${NC}"
    echo ""
    echo -e "  🌐 URL:              ${GREEN}http://localhost:8069${NC}"
    echo -e "  👤 Usuário:          ${GREEN}admin${NC}"
    echo -e "  🔑 Senha Master:     ${GREEN}admin${NC}"
    echo ""
    echo -e "${BLUE}📦 Banco de Dados:${NC}"
    echo -e "  🗄️  Host:             ${GREEN}localhost${NC}"
    echo -e "  📊 Porta:            ${GREEN}5432${NC}"
    echo -e "  👤 Usuário:          ${GREEN}odoo${NC}"
    echo -e "  🔑 Senha:            ${GREEN}odoo${NC}"
    echo ""
    echo -e "${BLUE}🚀 Próximos Passos:${NC}"
    echo ""
    echo "1. Acesse: http://localhost:8069"
    echo ""
    echo "2. Crie um banco de dados:"
    echo "   - Nome: crm_wealth_db"
    echo "   - Email admin: admin@example.com"
    echo "   - Senha: admin (ou outra de sua escolha)"
    echo "   - Idioma: Portuguese (BR) / pt_BR"
    echo "   - País: Brazil"
    echo ""
    echo "3. Após criar o banco, ative o modo desenvolvedor:"
    echo "   Settings → Developer Tools → Activate Developer Mode"
    echo ""
    echo "4. Instale o módulo CRM Wealth:"
    echo "   Apps → Update Apps List → Buscar 'Wealth' → Install"
    echo ""
    echo -e "${BLUE}🛠️  Comandos Úteis:${NC}"
    echo ""
    echo "  Ver logs em tempo real:"
    echo -e "    ${YELLOW}docker compose logs -f odoo${NC}"
    echo ""
    echo "  Parar containers:"
    echo -e "    ${YELLOW}docker compose stop${NC}"
    echo ""
    echo "  Reiniciar Odoo:"
    echo -e "    ${YELLOW}docker compose restart odoo${NC}"
    echo ""
    echo "  Parar e remover tudo:"
    echo -e "    ${YELLOW}docker compose down${NC}"
    echo ""
    echo "  Parar e remover tudo (incluindo volumes/dados):"
    echo -e "    ${YELLOW}docker compose down -v${NC}"
    echo ""
    echo "  Acessar terminal do container Odoo:"
    echo -e "    ${YELLOW}docker exec -it odoo_app bash${NC}"
    echo ""
    echo "  Atualizar módulo após mudanças:"
    echo -e "    ${YELLOW}docker compose restart odoo${NC}"
    echo -e "    ${YELLOW}# Depois no Odoo: Apps → CRM Wealth → Upgrade${NC}"
    echo ""
    echo -e "${GREEN}🎉 Ambiente pronto para desenvolvimento!${NC}"
    echo ""
    
    # Abrir navegador automaticamente (opcional)
    read -p "Deseja abrir o navegador automaticamente? (s/n) " OPEN_BROWSER
    if [ "$OPEN_BROWSER" = "s" ]; then
        sleep 3
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:8069
        elif command -v open &> /dev/null; then
            open http://localhost:8069
        else
            echo "Abra manualmente: http://localhost:8069"
        fi
    fi
    
else
    echo -e "${RED}❌ Erro ao iniciar containers!${NC}"
    echo "Verifique os logs:"
    docker compose logs
    exit 1
fi
