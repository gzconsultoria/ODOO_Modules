#!/usr/bin/env python3
"""
Desinstalar e Reinstalar GZ Finance Modules
Processo completo: uninstall → update list → install
"""
import xmlrpc.client
import time

URL = 'http://localhost:8069'
DB = 'gzcon'
USERNAME = 'contato@geovanezomer.com.br'
PASSWORD = input("Digite a senha do usuário contato@geovanezomer.com.br: ")

def wait_for_odoo(max_attempts=30):
    """Aguarda Odoo ficar disponível"""
    print("⏳ Aguardando Odoo ficar disponível...")
    for i in range(max_attempts):
        try:
            common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
            version = common.version()
            print(f"✅ Odoo disponível (versão {version['server_version']})")
            return True
        except Exception as e:
            print(f"   Tentativa {i+1}/{max_attempts}... aguardando...")
            time.sleep(2)
    print("❌ Timeout aguardando Odoo")
    return False

def uninstall_modules():
    """Desinstala gz_finance_crm e gz_finance_core"""
    
    if not wait_for_odoo():
        return False
    
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Falha na autenticação")
        return False
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print("\n" + "=" * 80)
    print("🗑️  DESINSTALAÇÃO GZ Finance Modules")
    print("=" * 80)
    
    # Ordem importa: desinstalar primeiro o módulo dependente (CRM), depois o core
    modules_to_uninstall = ['gz_finance_crm', 'gz_finance_core']
    
    for module_name in modules_to_uninstall:
        print(f"\n📦 Processando {module_name}...")
        
        # Buscar módulo
        module_ids = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', module_name)]]
        )
        
        if not module_ids:
            print(f"   ⚠️ Módulo {module_name} não encontrado")
            continue
        
        module = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_ids[0]],
            {'fields': ['name', 'state']}
        )[0]
        
        print(f"   Estado atual: {module['state']}")
        
        if module['state'] == 'installed':
            print(f"   🗑️  Desinstalando {module_name}...")
            try:
                models.execute_kw(DB, uid, PASSWORD,
                    'ir.module.module', 'button_immediate_uninstall',
                    [module_ids]
                )
                print(f"   ✅ {module_name} desinstalado!")
                
                # Aguardar um pouco entre desinstalações
                time.sleep(3)
                
            except Exception as e:
                print(f"   ❌ Erro na desinstalação: {e}")
                return False
        else:
            print(f"   ℹ️  Módulo não está instalado (estado: {module['state']})")
    
    print("\n✅ Desinstalação concluída!")
    return True

def update_module_list():
    """Atualiza lista de módulos"""
    
    if not wait_for_odoo():
        return False
    
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Falha na autenticação")
        return False
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print("\n" + "=" * 80)
    print("🔄 ATUALIZANDO LISTA DE MÓDULOS")
    print("=" * 80)
    
    try:
        models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'update_list', [[]]
        )
        print("✅ Lista de módulos atualizada!")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar lista: {e}")
        return False

def install_modules():
    """Instala gz_finance_core e gz_finance_crm"""
    
    if not wait_for_odoo():
        return False
    
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Falha na autenticação")
        return False
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print("\n" + "=" * 80)
    print("📥 INSTALAÇÃO GZ Finance Modules")
    print("=" * 80)
    
    # Ordem importa: instalar primeiro o core, depois o CRM
    modules_to_install = ['gz_finance_core', 'gz_finance_crm']
    
    for module_name in modules_to_install:
        print(f"\n📦 Processando {module_name}...")
        
        # Buscar módulo
        module_ids = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', module_name)]]
        )
        
        if not module_ids:
            print(f"   ❌ Módulo {module_name} não encontrado após update_list!")
            return False
        
        module = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_ids[0]],
            {'fields': ['name', 'state', 'installable']}
        )[0]
        
        print(f"   Estado: {module['state']}")
        print(f"   Instalável: {module['installable']}")
        
        if not module['installable']:
            print(f"   ❌ Módulo marcado como não instalável!")
            return False
        
        if module['state'] == 'uninstalled':
            print(f"   📥 Instalando {module_name}...")
            try:
                models.execute_kw(DB, uid, PASSWORD,
                    'ir.module.module', 'button_immediate_install',
                    [module_ids]
                )
                print(f"   ✅ {module_name} instalado com sucesso!")
                
                # Aguardar Odoo processar
                print("   ⏳ Aguardando Odoo processar instalação...")
                time.sleep(5)
                
                # Verificar se Odoo ainda está disponível
                if not wait_for_odoo(max_attempts=10):
                    print("   ⚠️ Odoo pode ter reiniciado, continuando...")
                
            except Exception as e:
                print(f"   ❌ Erro na instalação: {e}")
                return False
        else:
            print(f"   ℹ️  Módulo já está instalado (estado: {module['state']})")
    
    return True

def verify_installation():
    """Verifica se módulos foram instalados corretamente"""
    
    if not wait_for_odoo():
        return False
    
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Falha na autenticação")
        return False
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print("\n" + "=" * 80)
    print("✅ VERIFICAÇÃO FINAL")
    print("=" * 80)
    
    modules = ['gz_finance_core', 'gz_finance_crm']
    all_ok = True
    
    for module_name in modules:
        module_ids = models.execute_kw(DB, uid, PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', module_name)]]
        )
        
        if module_ids:
            module = models.execute_kw(DB, uid, PASSWORD,
                'ir.module.module', 'read',
                [module_ids[0]],
                {'fields': ['name', 'state', 'installable']}
            )[0]
            
            status = "✅" if module['state'] == 'installed' else "❌"
            print(f"{status} {module_name}: {module['state']}")
            
            if module['state'] != 'installed':
                all_ok = False
        else:
            print(f"❌ {module_name}: NÃO ENCONTRADO")
            all_ok = False
    
    # Verificar se campo origin_lead_id foi criado
    print("\n📊 Verificando criação de campos no banco...")
    try:
        fields = models.execute_kw(DB, uid, PASSWORD,
            'ir.model.fields', 'search_read',
            [[('model', '=', 'res.partner'), ('name', 'in', ['origin_lead_id', 'aum_3months_ago', 'meetings_last_6months', 'response_rate'])]],
            {'fields': ['name', 'ttype', 'state']}
        )
        
        for field in fields:
            print(f"   ✅ {field['name']} ({field['ttype']}) - {field['state']}")
        
        if len(fields) < 4:
            print(f"   ⚠️ Esperado 4 campos, encontrado {len(fields)}")
    
    except Exception as e:
        print(f"   ⚠️ Não foi possível verificar campos: {e}")
    
    return all_ok

def main():
    """Processo completo"""
    print("\n" + "=" * 80)
    print("🔧 REINSTALAÇÃO COMPLETA GZ FINANCE MODULES")
    print("=" * 80)
    print("\nProcesso:")
    print("1. Desinstalar gz_finance_crm")
    print("2. Desinstalar gz_finance_core")
    print("3. Atualizar lista de módulos")
    print("4. Instalar gz_finance_core")
    print("5. Instalar gz_finance_crm")
    print("6. Verificar instalação")
    print("\n" + "=" * 80)
    
    input("\nPressione ENTER para continuar...")
    
    # Passo 1: Desinstalar
    if not uninstall_modules():
        print("\n❌ FALHA na desinstalação")
        return
    
    # Passo 2: Atualizar lista
    if not update_module_list():
        print("\n❌ FALHA ao atualizar lista")
        return
    
    # Passo 3: Instalar
    if not install_modules():
        print("\n❌ FALHA na instalação")
        return
    
    # Passo 4: Verificar
    if verify_installation():
        print("\n" + "=" * 80)
        print("🎉 SUCESSO! Módulos reinstalados corretamente!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("⚠️ ATENÇÃO: Alguns problemas foram detectados")
        print("=" * 80)

if __name__ == '__main__':
    main()
