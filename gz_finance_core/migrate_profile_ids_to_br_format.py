#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migração: Converter Finance Profile IDs para formato brasileiro

ANTES: FIN-20251129-0009 (YYYYMMDD)
DEPOIS: FIN-29.11.2025-0009 (DD.MM.YYYY)

USO:
    docker exec -it odoo_modules-web-1 python3 /mnt/extra-addons/gz_finance_core/migrate_profile_ids_to_br_format.py
"""

import os
import sys
import re
from datetime import datetime

# Add Odoo to path
sys.path.append('/usr/lib/python3/dist-packages')

import odoo
from odoo import api, SUPERUSER_ID
from odoo.orm.registry import Registry

# Database configuration
DB_NAME = 'gzcon'
DB_HOST = 'db'
DB_USER = 'odoo'
DB_PASSWORD = 'odoo'
DB_PORT = 5432

def convert_profile_id_format(old_id):
    """
    Converter formato antigo para brasileiro
    
    Args:
        old_id (str): FIN-20251129-0009
        
    Returns:
        str: FIN-29.11.2025-0009
    """
    # Padrão: FIN-YYYYMMDD-XXXX
    pattern = r'FIN-(\d{4})(\d{2})(\d{2})-(\d+)'
    match = re.match(pattern, old_id)
    
    if not match:
        print(f"  ⚠️  ID não corresponde ao padrão antigo: {old_id}")
        return None
    
    year, month, day, seq = match.groups()
    
    # Validar data
    try:
        date_obj = datetime(int(year), int(month), int(day))
    except ValueError:
        print(f"  ⚠️  Data inválida em ID: {old_id}")
        return None
    
    # Formato brasileiro: FIN-DD.MM.YYYY-XXXX
    new_id = f"FIN-{day}.{month}.{year}-{seq}"
    
    return new_id


def migrate_profile_ids():
    """Executar migração de IDs"""
    
    print("=" * 70)
    print("MIGRAÇÃO: Finance Profile IDs → Formato Brasileiro")
    print("=" * 70)
    print()
    
    # Configurar Odoo
    odoo.tools.config.parse_config([
        '--db_host', DB_HOST,
        '--db_port', str(DB_PORT),
        '--db_user', DB_USER,
        '--db_password', DB_PASSWORD,
    ])
    
    # Conectar ao banco
    try:
        registry = Registry(DB_NAME)
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco '{DB_NAME}': {e}")
        sys.exit(1)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Buscar todos os perfis financeiros
        partners = env['res.partner'].search([
            ('is_finance_client', '=', True),
            ('finance_profile_id', '!=', False)
        ])
        
        print(f"📊 Total de perfis financeiros encontrados: {len(partners)}")
        print()
        
        if not partners:
            print("✅ Nenhum perfil para migrar.")
            return
        
        # Contadores
        migrated = 0
        skipped = 0
        errors = 0
        
        print("🔄 Iniciando conversão...\n")
        
        for partner in partners:
            old_id = partner.finance_profile_id
            
            # Verificar se já está no formato brasileiro
            if re.match(r'FIN-\d{2}\.\d{2}\.\d{4}-\d+', old_id):
                print(f"  ⏭️  {partner.name}: {old_id} (já no formato BR)")
                skipped += 1
                continue
            
            # Converter
            new_id = convert_profile_id_format(old_id)
            
            if not new_id:
                errors += 1
                continue
            
            # Verificar se novo ID já existe
            duplicate = env['res.partner'].search([
                ('finance_profile_id', '=', new_id),
                ('id', '!=', partner.id)
            ], limit=1)
            
            if duplicate:
                print(f"  ❌ {partner.name}: {old_id} → {new_id} (DUPLICADO! Já usado por {duplicate.name})")
                errors += 1
                continue
            
            # Atualizar
            try:
                # Desabilitar constraint temporariamente usando SQL direto
                cr.execute("""
                    UPDATE res_partner 
                    SET finance_profile_id = %s 
                    WHERE id = %s
                """, (new_id, partner.id))
                
                print(f"  ✅ {partner.name}: {old_id} → {new_id}")
                migrated += 1
                
            except Exception as e:
                print(f"  ❌ {partner.name}: Erro ao atualizar - {str(e)}")
                errors += 1
        
        # Commit das mudanças
        if migrated > 0:
            cr.commit()
            print()
            print("💾 Alterações commitadas no banco de dados.")
        
        # Resumo
        print()
        print("=" * 70)
        print("RESUMO DA MIGRAÇÃO")
        print("=" * 70)
        print(f"✅ Migrados:  {migrated}")
        print(f"⏭️  Ignorados:  {skipped} (já no formato BR)")
        print(f"❌ Erros:      {errors}")
        print(f"📊 Total:      {len(partners)}")
        print("=" * 70)
        
        if migrated > 0:
            print()
            print("🎉 Migração concluída com sucesso!")
            print()
            print("PRÓXIMOS PASSOS:")
            print("1. Verifique alguns registros no Odoo para confirmar")
            print("2. Teste criar um novo perfil financeiro")
            print("3. Confirme que novos IDs seguem o formato DD.MM.YYYY")
        elif errors > 0:
            print()
            print("⚠️  Migração concluída com erros. Revise os logs acima.")
        else:
            print()
            print("✅ Todos os IDs já estavam no formato correto!")


if __name__ == '__main__':
    try:
        migrate_profile_ids()
    except KeyboardInterrupt:
        print("\n\n❌ Migração cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
