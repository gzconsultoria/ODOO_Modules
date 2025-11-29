#!/usr/bin/env python3
"""
Script para fazer SAFE UPGRADE do módulo gz_finance_core
Desativa views temporariamente para permitir criação de campos no banco
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

# ========================================
# PASSO 1: Desativar views problemáticas
# ========================================
print("\n📦 Buscando views do módulo gz_finance_core...")
view_ids = models.execute_kw(db, uid, password,
    'ir.ui.view', 'search',
    [[('model', '=', 'res.partner'), ('name', 'ilike', 'finance')]]
)

if view_ids:
    print(f"   Encontradas {len(view_ids)} views finance do res.partner")
    print("🔒 Desativando views temporariamente...")
    
    try:
        models.execute_kw(db, uid, password,
            'ir.ui.view', 'write',
            [view_ids, {'active': False}]
        )
        print("   ✅ Views desativadas")
    except Exception as e:
        print(f"   ⚠️  Aviso ao desativar views: {str(e)}")
else:
    print("   ℹ️  Nenhuma view encontrada (primeira instalação?)")

# ========================================
# PASSO 2: Fazer UPGRADE do módulo
# ========================================
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

print("\n🚀 Fase 1: UPGRADE do módulo (criando campos no banco)...")
try:
    # Marcar para upgrade
    models.execute_kw(db, uid, password,
        'ir.module.module', 'write',
        [module_ids, {'state': 'to upgrade'}]
    )
    print("   ✅ Módulo marcado para upgrade")
    
    # Tentar fazer upgrade imediato
    result = models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids]
    )
    print("   ✅ UPGRADE Fase 1 concluído - Campos criados no banco!")
    
except Exception as e:
    error_msg = str(e)
    if "não existe no modelo" in error_msg or "does not exist" in error_msg:
        print(f"   ⚠️  Erro esperado: {error_msg[:200]}...")
        print("   ℹ️  Isso é normal - views ainda referenciam campos novos")
    else:
        print(f"   ❌ Erro inesperado: {error_msg}")
        # Não abortar - continuar para reativar views

# ========================================
# PASSO 3: Reativar views
# ========================================
print("\n🔓 Reativando views...")
if view_ids:
    try:
        models.execute_kw(db, uid, password,
            'ir.ui.view', 'write',
            [view_ids, {'active': True}]
        )
        print("   ✅ Views reativadas")
    except Exception as e:
        print(f"   ⚠️  Aviso ao reativar views: {str(e)}")

# ========================================
# PASSO 4: Segundo upgrade (com views)
# ========================================
print("\n🚀 Fase 2: UPGRADE final (com views ativas)...")
try:
    result = models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids]
    )
    print("   ✅ UPGRADE Fase 2 concluído!")
    print("\n✅ SUCESSO TOTAL! Módulo atualizado com todos os campos e views.")
    
except Exception as e:
    print(f"   ❌ Erro na Fase 2: {str(e)}")
    print("\n⚠️  AÇÃO NECESSÁRIA:")
    print("   1. Reinicie o servidor Odoo: docker restart odoo_modules-web-1")
    print("   2. Tente fazer upgrade manualmente pela interface")
    exit(1)

print("\n" + "="*60)
print("✅ Script finalizado com sucesso!")
print("="*60)
