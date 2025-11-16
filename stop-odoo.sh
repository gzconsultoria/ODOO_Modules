#!/bin/bash

###############################################################################
# Script para Parar Odoo 19 Docker
###############################################################################

echo "🛑 Parando containers Odoo..."

docker compose stop

echo "✅ Containers parados!"
echo ""
echo "Para iniciar novamente: ./start-odoo.sh"
echo "Para remover completamente: docker compose down"
echo "Para remover com dados: docker compose down -v"
