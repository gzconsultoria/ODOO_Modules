#!/usr/bin/env python3
"""
Script para atualizar módulo finance_core via XML-RPC
"""
import xmlrpc.client

# Configurações
url = 'http://localhost:8069'
db = 'gzcon'
username = 'admin'
password = 'admin'

print("🔐 Autenticando...")
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Falha na autenticação")
    exit(1)

print(f"✅ Autenticado como UID: {uid}")

# Conectar ao endpoint de objetos
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Buscar módulo finance_core
print("\n📦 Buscando módulo finance_core...")
module_ids = models.execute_kw(
    db, uid, password,
    'ir.module.module', 'search',
    [[('name', '=', 'finance_core')]]
)

if not module_ids:
    print("❌ Módulo finance_core não encontrado")
    exit(1)

module_id = module_ids[0]
print(f"✅ Módulo encontrado (ID: {module_id})")

# Atualizar módulo
print("\n🔄 Atualizando módulo...")
models.execute_kw(
    db, uid, password,
    'ir.module.module', 'button_immediate_upgrade',
    [[module_id]]
)

print("\n" + "="*60)
print("✅ MÓDULO ATUALIZADO COM SUCESSO!")
print("="*60)
print("\n📋 Novas permissões aplicadas:")
print("   - base.group_user → acesso total a finance.profile")
print("   - base.group_user → acesso total a finance.alert")
print("   - base.group_user → acesso total a finance.onboarding.wizard")
print("\n💡 Agora todos os usuários internos têm acesso ao módulo")
print("   Atualize a página (F5) para ver as mudanças")
