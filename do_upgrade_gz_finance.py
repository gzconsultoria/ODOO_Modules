#!/usr/bin/env python3
"""
Script FINAL para UPGRADE do gz_finance_core
Carrega todas as views de uma vez
"""

import xmlrpc.client
import sys

url = 'http://localhost:8069'
db = 'gzcon'
username = 'admin'
password = 'admin'

print("🚀 UPGRADE FINAL - Carregando TODAS as views...")
print("="*60)

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Falha na autenticação!")
        print("\n💡 FAÇA MANUALMENTE:")
        print("   Apps → gz_finance_core → Upgrade")
        sys.exit(1)
    
    print(f"✅ Autenticado (UID: {uid})")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n💡 FAÇA MANUALMENTE:")
    print("   Apps → gz_finance_core → Upgrade")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

try:
    module_ids = models.execute_kw(db, uid, password,
        'ir.module.module', 'search',
        [[('name', '=', 'gz_finance_core')]]
    )
    
    if not module_ids:
        print("❌ Módulo não encontrado!")
        sys.exit(1)
    
    print("📦 Módulo encontrado, iniciando upgrade...")
    
    models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [module_ids]
    )
    
    print("\n" + "="*60)
    print("✅ UPGRADE CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\n🎉 PRÓXIMOS PASSOS:")
    print("   1. Atualize a página (F5)")
    print("   2. Vá em: Contatos")
    print("   3. Abra um contato")
    print("   4. Marque: 'Cliente Financeiro'")
    print("   5. A aba '💰 Financeiro' com 8 sub-abas deve aparecer!")
    print("\n")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ ERRO durante upgrade:")
    print(f"{error_msg[:1000]}")
    print("\n💡 FAÇA MANUALMENTE:")
    print("   Apps → gz_finance_core → Upgrade")
    sys.exit(1)
