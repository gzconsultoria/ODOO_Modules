#!/usr/bin/env python3
# Executar via: docker exec -i odoo_modules-web-1 python3 < atualizar_ids.py

import xmlrpc.client

# Conectar ao Odoo
url = "http://localhost:8069"
db = "gzcon"
username = "admin"
password = "admin"

# Autenticar
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Falha na autenticação")
    exit(1)

print(f"✅ Autenticado como user ID: {uid}")

# Conectar aos modelos
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Buscar clientes sem Profile ID
partner_ids = models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[('is_finance_client', '=', True), ('finance_profile_id', '=', False)]])

print(f"🔍 Encontrados {len(partner_ids)} clientes sem Profile ID")

if not partner_ids:
    print("✅ Todos os clientes já possuem Profile ID")
    exit(0)

# Executar ação de geração
for partner_id in partner_ids:
    partner_data = models.execute_kw(db, uid, password,
        'res.partner', 'read',
        [partner_id], {'fields': ['name']})
    
    print(f"\n📝 Processando: {partner_data[0]['name']} (ID: {partner_id})")
    
    # Ativar/desativar toggle para forçar write()
    models.execute_kw(db, uid, password,
        'res.partner', 'write',
        [[partner_id], {'is_finance_client': True}])
    
    # Verificar se gerou
    updated = models.execute_kw(db, uid, password,
        'res.partner', 'read',
        [partner_id], {'fields': ['finance_profile_id']})
    
    if updated[0]['finance_profile_id']:
        print(f"  ✅ ID Gerado: {updated[0]['finance_profile_id']}")
    else:
        print(f"  ❌ Falha ao gerar ID")

print("\n" + "="*60)
print("CONCLUÍDO")
print("="*60)
