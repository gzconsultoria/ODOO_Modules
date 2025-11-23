#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar o módulo finance_core via XML-RPC
Similar ao que a interface web faz
"""
import xmlrpc.client

# Configurações
url = 'http://localhost:8069'
db = 'gzcon'
username = 'admin'
password = 'admin'

# Autenticação
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Falha na autenticação!")
    exit(1)

print(f"✅ Autenticado como usuário ID: {uid}")

# Conexão com models
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Buscar módulo finance_core
try:
    module_ids = models.execute_kw(
        db, uid, password,
        'ir.module.module', 'search',
        [[('name', '=', 'finance_core')]]
    )
    
    if not module_ids:
        print("❌ Módulo finance_core não encontrado!")
        print("🔍 Atualizando lista de módulos...")
        models.execute_kw(
            db, uid, password,
            'ir.module.module', 'update_list', [[]]
        )
        print("✅ Lista atualizada, buscando novamente...")
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[('name', '=', 'finance_core')]]
        )
    
    if module_ids:
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids], {'fields': ['name', 'state', 'summary']}
        )
        
        print(f"\n📦 Módulo encontrado:")
        for mod in module_data:
            print(f"   Nome: {mod['name']}")
            print(f"   Estado: {mod['state']}")
            print(f"   Resumo: {mod.get('summary', 'N/A')}")
        
        current_state = module_data[0]['state']
        
        if current_state == 'installed':
            print("\n✅ Módulo já está instalado!")
        elif current_state in ['uninstalled', 'to install']:
            print("\n🚀 Iniciando instalação...")
            try:
                models.execute_kw(
                    db, uid, password,
                    'ir.module.module', 'button_immediate_install',
                    [module_ids]
                )
                print("✅ Instalação iniciada com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao instalar: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("❌ Módulo não encontrado após atualização!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
