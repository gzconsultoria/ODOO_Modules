#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar estrutura de pastas e pastas de clientes existentes
"""
import xmlrpc.client
import subprocess

# Configuração de conexão
url = "http://localhost:8069"
db = "gzcon"
username = "admin"
password = "admin"

# Conectar
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print(f"✅ Conectado como UID {uid}")

# 1. Atualizar módulo para carregar pastas do XML
print("\n📦 Atualizando módulo gz_finance_docs...")
try:
    result = subprocess.run([
        'docker', 'exec', 'odoo_modules-web-1',
        'odoo', '-c', '/etc/odoo/odoo.conf', '-d', 'gzcon',
        '-u', 'gz_finance_docs', '--stop-after-init'
    ], capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("✅ Módulo atualizado - pastas Escritório e Clientes criadas!")
    else:
        print(f"⚠️  Update retornou código {result.returncode}")
        if "already exists" in result.stderr or "already exists" in result.stdout:
            print("   (Pastas provavelmente já existem)")
    
    # Reconectar após update
    uid = common.authenticate(db, username, password, {})
    
except subprocess.TimeoutExpired:
    print("⚠️  Timeout - mas pode ter funcionado. Reconectando...")
    uid = common.authenticate(db, username, password, {})
except Exception as e:
    print(f"❌ Erro: {e}")

# Verificar se pastas foram criadas
folders = models.execute_kw(db, uid, password,
    'document_hub.folder', 'search_read',
    [[]], {'fields': ['name', 'parent_folder_id']})

print(f"\n📁 Pastas existentes: {len(folders)}")
for folder in folders:
    parent = f" (filho de {folder['parent_folder_id'][1]})" if folder['parent_folder_id'] else " (RAIZ)"
    print(f"   - {folder['name']}{parent}")

# 2. Buscar clientes com perfil financeiro
print("\n👥 Buscando clientes com perfil financeiro...")
try:
    partners = models.execute_kw(db, uid, password,
        'res.partner', 'search_read',
        [[['is_finance_client', '=', True], ['finance_profile_id', '!=', False]]],
        {'fields': ['id', 'name', 'finance_profile_id', 'client_folder_id']})
    
    print(f"✅ Encontrados {len(partners)} clientes com perfil financeiro:")
    for p in partners:
        has_folder = "✅ Tem pasta" if p['client_folder_id'] else "❌ SEM pasta"
        print(f"   - {p['name']} ({p['finance_profile_id']}) - {has_folder}")
    
    if len(partners) == 0:
        print("⚠️  Nenhum cliente encontrado. Finalizando.")
        exit(0)
    
except Exception as e:
    print(f"❌ Erro ao buscar clientes: {e}")
    exit(1)

# 3. Criar pastas para clientes que ainda não têm
print("\n📁 Criando pastas para clientes sem pasta...")
created_count = 0
skipped_count = 0

for partner in partners:
    partner_id = partner['id']
    partner_name = partner['name']
    finance_profile_id = partner['finance_profile_id']
    client_folder_id = partner['client_folder_id']
    
    if client_folder_id:
        print(f"⏭️  {partner_name} - Já tem pasta")
        skipped_count += 1
        continue
    
    try:
        # Chamar método de criação de pasta diretamente
        models.execute_kw(db, uid, password,
            'res.partner', '_create_client_folder_structure',
            [[partner_id]])
        
        print(f"✅ {partner_name} ({finance_profile_id}) - Pasta criada!")
        created_count += 1
        
    except Exception as e:
        print(f"❌ {partner_name} - Erro: {e}")

print(f"\n📊 Resumo:")
print(f"   ✅ Criadas: {created_count}")
print(f"   ⏭️  Puladas: {skipped_count}")
print(f"   📁 Total: {len(partners)}")

print("\n🎉 Script finalizado!")
