#!/usr/bin/env python3
"""
Script para atualizar gz_finance_core com limpeza de views órfãs.
Deleta views antigas de finance.profile e reinstala o módulo.
"""

import xmlrpc.client

# Configurações
url = "http://localhost:8069"
db = "gzcon"
username = "admin"
password = "admin"

# Conectar
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

print(f"✅ Conectado como user ID: {uid}")

# 1. Desinstalar módulo (força limpeza completa)
print("\n🗑️  Desinstalando módulo gz_finance_core...")
module_ids = models.execute_kw(
    db, uid, password,
    'ir.module.module', 'search',
    [[('name', '=', 'gz_finance_core')]]
)

if module_ids:
    module = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'read',
        [module_ids], {'fields': ['name', 'state']}
    )[0]
    
    print(f"   Módulo: {module['name']} (state: {module['state']})")
    
    if module['state'] == 'installed':
        print("   Executando button_immediate_uninstall...")
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'button_immediate_uninstall',
            [module_ids]
        )
        print("   ✅ Módulo desinstalado")
    else:
        print(f"   ⚠️  Módulo já está em state: {module['state']}")
else:
    print("   ⚠️  Módulo não encontrado")

# 2. Deletar views órfãs de finance.profile
print("\n🧹 Deletando views órfãs de finance.profile...")
orphan_views = models.execute_kw(
    db, uid, password,
    'ir.ui.view', 'search',
    [[('model', '=', 'finance.profile')]]
)

if orphan_views:
    print(f"   Encontradas {len(orphan_views)} views órfãs")
    models.execute_kw(
        db, uid, password,
        'ir.ui.view', 'unlink',
        [orphan_views]
    )
    print("   ✅ Views deletadas")
else:
    print("   ℹ️  Nenhuma view órfã encontrada")

# 3. Deletar actions órfãs
print("\n🧹 Deletando actions órfãs...")
orphan_actions = models.execute_kw(
    db, uid, password,
    'ir.actions.act_window', 'search',
    [[('res_model', '=', 'finance.profile')]]
)

if orphan_actions:
    print(f"   Encontradas {len(orphan_actions)} actions órfãs")
    models.execute_kw(
        db, uid, password,
        'ir.actions.act_window', 'unlink',
        [orphan_actions]
    )
    print("   ✅ Actions deletadas")
else:
    print("   ℹ️  Nenhuma action órfã encontrada")

# 4. Deletar menus órfãos
print("\n🧹 Deletando menus órfãos...")
orphan_menus = models.execute_kw(
    db, uid, password,
    'ir.ui.menu', 'search',
    [[('name', 'in', ['Financial Profiles', 'Finance Profile'])]]
)

if orphan_menus:
    print(f"   Encontrados {len(orphan_menus)} menus órfãos")
    models.execute_kw(
        db, uid, password,
        'ir.ui.menu', 'unlink',
        [orphan_menus]
    )
    print("   ✅ Menus deletados")
else:
    print("   ℹ️  Nenhum menu órfão encontrado")

# 5. Reinstalar módulo
print("\n📦 Instalando módulo gz_finance_core...")
module_ids = models.execute_kw(
    db, uid, password,
    'ir.module.module', 'search',
    [[('name', '=', 'gz_finance_core')]]
)

if module_ids:
    # Marcar para instalação
    models.execute_kw(
        db, uid, password,
        'ir.module.module', 'button_immediate_install',
        [module_ids]
    )
    print("   ✅ Módulo instalado com sucesso!")
else:
    print("   ❌ Módulo não encontrado no sistema")

print("\n✨ Processo completo!")
