#!/usr/bin/env python3
"""
Upgrade GZ Finance Modules via XML-RPC
"""
import xmlrpc.client

URL = 'http://localhost:8069'
DB = 'gzcon'
USERNAME = 'admin'
PASSWORD = 'admin'

def upgrade_modules():
    """Upgrade gz_finance_core e gz_finance_crm"""
    
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Falha na autenticação")
        return
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print("=" * 80)
    print("🔧 UPGRADE GZ Finance Modules")
    print("=" * 80)
    
    modules_to_upgrade = ['gz_finance_core', 'gz_finance_crm']
    
    for module_name in modules_to_upgrade:
        print(f"\n📦 Processando {module_name}...")
        
        # Buscar módulo
        module_ids = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', module_name)]]
        )
        
        if not module_ids:
            print(f"   ⚠️ Módulo {module_name} não encontrado no banco")
            continue
        
        module = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_ids[0]],
            {'fields': ['name', 'state', 'installable']}
        )[0]
        
        print(f"   Estado atual: {module['state']}")
        print(f"   Instalável: {module['installable']}")
        
        if module['state'] == 'installed':
            print(f"   🔄 Fazendo upgrade...")
            try:
                models.execute_kw(DB, uid, PASSWORD,
                    'ir.module.module', 'button_immediate_upgrade',
                    [module_ids]
                )
                print(f"   ✅ Upgrade de {module_name} iniciado com sucesso!")
            except Exception as e:
                print(f"   ❌ Erro no upgrade: {e}")
        
        elif module['state'] == 'uninstalled':
            print(f"   📥 Instalando módulo...")
            try:
                models.execute_kw(DB, uid, PASSWORD,
                    'ir.module.module', 'button_immediate_install',
                    [module_ids]
                )
                print(f"   ✅ Instalação de {module_name} iniciada!")
            except Exception as e:
                print(f"   ❌ Erro na instalação: {e}")
        
        else:
            print(f"   ⚠️ Estado inesperado: {module['state']}")
    
    print("\n" + "=" * 80)
    print("✅ PROCESSO CONCLUÍDO")
    print("=" * 80)
    print("\n⚠️ IMPORTANTE: O Odoo pode ter reiniciado. Aguarde alguns segundos.")
    print("   Depois verifique em Apps se os módulos estão com estado 'Installed'")

if __name__ == '__main__':
    upgrade_modules()
