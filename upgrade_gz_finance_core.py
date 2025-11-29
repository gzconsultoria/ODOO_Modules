#!/usr/bin/env python3
"""
Script para fazer UPGRADE do módulo gz_finance_core
Adiciona os novos campos ao banco de dados antes de carregar as views
"""

import xmlrpc.client

# Configurações
url = 'http://localhost:8069'
db = 'gzcon'
username = 'admin'
password = 'admin'

print("🔄 Conectando ao Odoo...")
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Falha na autenticação!")
    exit(1)

print(f"✅ Autenticado como UID: {uid}")

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("\n📦 Buscando módulo gz_finance_core...")
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[('name', '=', 'gz_finance_core')]]
)

if not module_ids:
    print("❌ Módulo gz_finance_core não encontrado!")
    exit(1)

module = models.execute_kw(db, uid, password,
    'ir.module.module', 'read',
    [module_ids[0]], {'fields': ['name', 'state']}
)

print(f"📊 Estado atual: {module['state']}")

print("\n🚀 Iniciando UPGRADE...")
try:
    # Método 1: Tentar upgrade direto
    result = models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids]
    )
    print("✅ UPGRADE concluído com sucesso!")
    print(f"   Resultado: {result}")
    
except Exception as e:
    print(f"❌ Erro durante upgrade: {str(e)}")
    
    # Método 2: Marcar para upgrade e reiniciar
    print("\n🔄 Tentando método alternativo...")
    try:
        models.execute_kw(db, uid, password,
            'ir.module.module', 'write',
            [module_ids, {'state': 'to upgrade'}]
        )
        print("✅ Módulo marcado para upgrade")
        print("⚠️  ATENÇÃO: Reinicie o servidor Odoo para aplicar as mudanças")
        print("   Comando: docker restart odoo_modules-web-1")
        
    except Exception as e2:
        print(f"❌ Erro ao marcar para upgrade: {str(e2)}")
        exit(1)

print("\n✅ Script finalizado!")
