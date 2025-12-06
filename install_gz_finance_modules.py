#!/usr/bin/env python3
"""
Instalação limpa dos módulos gz_finance_core + gz_finance_docs
Ordem: core primeiro, docs depois
"""
import xmlrpc.client
import time

URL = 'http://localhost:8069'
DB = 'gzcon'
USERNAME = 'admin'
PASSWORD = 'admin'

def install_module(models, uid, module_name):
    """Instala um módulo e aguarda conclusão"""
    print(f"\n{'='*60}")
    print(f"📦 Instalando {module_name}...")
    print('='*60)
    
    # Buscar módulo
    module_ids = models.execute_kw(DB, uid, PASSWORD,
        'ir.module.module', 'search',
        [[('name', '=', module_name)]])
    
    if not module_ids:
        print(f"❌ Módulo {module_name} não encontrado!")
        return False
    
    module_id = module_ids[0]
    
    # Verificar estado
    module_data = models.execute_kw(DB, uid, PASSWORD,
        'ir.module.module', 'read',
        [module_id], {'fields': ['state', 'name']})
    
    print(f"Estado atual: {module_data[0]['state']}")
    
    if module_data[0]['state'] == 'installed':
        print(f"✅ {module_name} já está instalado")
        return True
    
    # Instalar
    try:
        models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'button_immediate_install',
            [[module_id]])
        
        print(f"✅ {module_name} instalado com sucesso!")
        time.sleep(2)  # Aguardar processamento
        return True
        
    except Exception as e:
        print(f"❌ Erro ao instalar {module_name}: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("🚀 INSTALAÇÃO LIMPA: gz_finance_core + gz_finance_docs")
    print("="*60)
    
    # Conectar
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Falha na autenticação!")
        return
    
    print(f"✅ Conectado como UID: {uid}")
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    # Atualizar lista de módulos primeiro
    print("\n🔄 Atualizando lista de módulos...")
    models.execute_kw(DB, uid, PASSWORD,
        'ir.module.module', 'update_list', [[]])
    
    # Instalar na ordem correta
    success = True
    
    # 1. gz_finance_core (base)
    if not install_module(models, uid, 'gz_finance_core'):
        success = False
    
    # 2. gz_finance_docs (depende de gz_finance_core)
    if success and not install_module(models, uid, 'gz_finance_docs'):
        success = False
    
    if success:
        print("\n" + "="*60)
        print("✅ TODOS OS MÓDULOS INSTALADOS COM SUCESSO!")
        print("="*60)
        print("\n📋 Menu 'Documentos Financeiros' disponível em:")
        print("   Consultoria → Documentos Financeiros")
    else:
        print("\n❌ Instalação falhou! Verifique os logs acima.")

if __name__ == '__main__':
    main()
