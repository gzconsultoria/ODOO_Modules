#!/usr/bin/env python3
"""Script para atualizar módulo finance_core via XML-RPC"""
import xmlrpc.client

# Configurações
url = 'http://localhost:8069'
db = 'gzcon'
username = 'admin'
password = 'admin'

# Conectar
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Falha na autenticação")
    exit(1)

print(f"✅ Autenticado como UID: {uid}")

# Buscar módulo finance_core
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
module_id = models.execute_kw(
    db, uid, password,
    'ir.module.module', 'search',
    [[('name', '=', 'finance_core')]]
)

if not module_id:
    print("❌ Módulo finance_core não encontrado")
    exit(1)

print(f"✅ Módulo encontrado: ID {module_id[0]}")

# Atualizar módulo
try:
    models.execute_kw(
        db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_id]
    )
    print("✅ Módulo finance_core atualizado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao atualizar: {e}")
    exit(1)
