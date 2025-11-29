#!/usr/bin/env python3
"""Script para atualizar os módulos finance_core e finance_crm_integration via XML-RPC"""

import xmlrpc.client

# Configurações
url = 'http://localhost:8069'
db = 'gzcon'
username = 'admin'
password = 'Geovane7184#'

# Conectar
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

print(f"🔄 Tentando autenticar...")
print(f"   URL: {url}")
print(f"   DB: {db}")
print(f"   User: {username}")

try:
    uid = common.authenticate(db, username, password, {})
    if not uid:
        print("❌ Falha na autenticação! Credenciais inválidas.")
        exit(1)
except Exception as e:
    print(f"❌ Erro ao autenticar: {e}")
    exit(1)

print(f"✅ Autenticado como uid: {uid}")

# Conectar ao object
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Buscar os módulos
module_names = ['finance_core', 'finance_crm_integration']

for module_name in module_names:
    print(f"\n🔍 Buscando módulo: {module_name}")
    
    module_ids = models.execute_kw(db, uid, password,
        'ir.module.module', 'search',
        [[('name', '=', module_name)]])
    
    if not module_ids:
        print(f"❌ Módulo {module_name} não encontrado!")
        continue
    
    print(f"✅ Módulo encontrado: ID {module_ids[0]}")
    
    # Atualizar o módulo
    print(f"🔄 Atualizando {module_name}...")
    try:
        models.execute_kw(db, uid, password,
            'ir.module.module', 'button_immediate_upgrade',
            [module_ids])
        print(f"✅ {module_name} atualizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao atualizar {module_name}: {e}")

print("\n✨ Processo concluído!")
