#!/bin/bash

###############################################################################
# Script de Instalação - CRM Wealth Management para Odoo 19
# Autor: GZ Consultoria
###############################################################################

set -e  # Parar em caso de erro

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     CRM Wealth Management - Instalador Odoo 19            ║"
echo "║     GZ Consultoria                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se está executando como usuário odoo ou root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Executando como root. Recomenda-se usar usuário odoo.${NC}"
fi

# Função para verificar se o Odoo está instalado
check_odoo() {
    echo -e "${BLUE}🔍 Verificando instalação do Odoo...${NC}"
    
    if ! command -v odoo &> /dev/null; then
        echo -e "${RED}❌ Odoo não encontrado no PATH${NC}"
        echo -e "${YELLOW}Por favor, instale o Odoo 19 antes de continuar${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Odoo encontrado${NC}"
}

# Função para pedir o caminho dos addons
get_addons_path() {
    echo ""
    echo -e "${BLUE}📁 Configuração do diretório de addons${NC}"
    echo ""
    echo "Exemplos de caminhos comuns:"
    echo "  - /opt/odoo/addons"
    echo "  - /usr/lib/python3/dist-packages/odoo/addons"
    echo "  - ~/odoo/addons"
    echo ""
    
    read -p "Digite o caminho do diretório de addons do Odoo: " ADDONS_PATH
    
    # Expandir ~ se usado
    ADDONS_PATH="${ADDONS_PATH/#\~/$HOME}"
    
    if [ ! -d "$ADDONS_PATH" ]; then
        echo -e "${YELLOW}⚠️  Diretório não existe. Deseja criar? (s/n)${NC}"
        read -p "> " CREATE_DIR
        
        if [ "$CREATE_DIR" = "s" ] || [ "$CREATE_DIR" = "S" ]; then
            mkdir -p "$ADDONS_PATH"
            echo -e "${GREEN}✅ Diretório criado${NC}"
        else
            echo -e "${RED}❌ Instalação cancelada${NC}"
            exit 1
        fi
    fi
}

# Função para copiar o módulo
copy_module() {
    echo ""
    echo -e "${BLUE}📦 Copiando módulo CRM Wealth...${NC}"
    
    SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/crm_wealth"
    
    if [ ! -d "$SOURCE_DIR" ]; then
        echo -e "${RED}❌ Diretório crm_wealth não encontrado${NC}"
        echo "Certifique-se de executar este script do diretório raiz do projeto"
        exit 1
    fi
    
    TARGET_DIR="$ADDONS_PATH/crm_wealth"
    
    # Verificar se já existe
    if [ -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}⚠️  Módulo já existe em $TARGET_DIR${NC}"
        read -p "Deseja sobrescrever? (s/n) " OVERWRITE
        
        if [ "$OVERWRITE" != "s" ] && [ "$OVERWRITE" != "S" ]; then
            echo -e "${YELLOW}ℹ️  Instalação cancelada${NC}"
            exit 0
        fi
        
        rm -rf "$TARGET_DIR"
    fi
    
    cp -r "$SOURCE_DIR" "$TARGET_DIR"
    
    # Ajustar permissões
    chmod -R 755 "$TARGET_DIR"
    
    echo -e "${GREEN}✅ Módulo copiado para $TARGET_DIR${NC}"
}

# Função para exibir próximos passos
show_next_steps() {
    echo ""
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              ✅ Instalação Concluída!                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}📋 Próximos passos:${NC}"
    echo ""
    echo "1. Reinicie o serviço do Odoo:"
    echo -e "   ${YELLOW}sudo systemctl restart odoo${NC}"
    echo ""
    echo "2. Acesse o Odoo e ative o modo desenvolvedor:"
    echo "   Settings → Developer Tools → Activate Developer Mode"
    echo ""
    echo "3. Atualize a lista de aplicativos:"
    echo "   Apps → Update Apps List"
    echo ""
    echo "4. Instale o módulo:"
    echo "   Apps → Buscar 'CRM Wealth Management' → Install"
    echo ""
    echo "5. Configure os dados iniciais:"
    echo "   CRM → Configuration → Wealth Management"
    echo ""
    echo -e "${GREEN}🎉 Pronto! Seu CRM Wealth está configurado!${NC}"
    echo ""
}

# Executar instalação
main() {
    check_odoo
    get_addons_path
    copy_module
    show_next_steps
}

main
