#!/usr/bin/env python3
"""
Script para corrigir XML IDs do document_hub_main após migração.

Força a recriação dos XML IDs com namespace correto (document_hub_main)
removendo referências antigas (document_hub).

USO:
1. Via linha de comando (Docker):
   docker exec odoo_modules-web-1 python3 /mnt/extra-addons/fix_document_hub_main_xmlids.py

2. Via Odoo Shell (web interface):
   Settings → Technical → Database Structure → Shell
   Copie e cole o código abaixo (seção ODOO SHELL CODE)
"""

import sys
import os

# === ODOO SHELL CODE (copiar daqui) ===
def fix_xmlids():
    """Corrige XML IDs document_hub → document_hub_main"""
    
    # Buscar XML IDs antigos
    old_xmlids = env['ir.model.data'].search([
        ('module', '=', 'document_hub'),
        ('name', 'like', 'folder_%')
    ])
    
    print(f"\n🔍 Encontrados {len(old_xmlids)} XML IDs antigos 'document_hub.*'")
    
    for xmlid in old_xmlids:
        # Verificar se já existe o novo XML ID
        new_xmlid = env['ir.model.data'].search([
            ('module', '=', 'document_hub_main'),
            ('name', '=', xmlid.name)
        ])
        
        if new_xmlid:
            print(f"✅ {xmlid.name}: novo XML ID já existe, removendo antigo")
            xmlid.unlink()
        else:
            print(f"🔄 {xmlid.name}: atualizando módulo para document_hub_main")
            xmlid.module = 'document_hub_main'
    
    env.cr.commit()
    print(f"\n✅ Correção concluída! Atualize o módulo document_hub_main agora.")

# Executar se for shell
if 'env' in dir():
    fix_xmlids()

# === FIM ODOO SHELL CODE ===

# Para execução via CLI (Docker)
if __name__ == '__main__':
    # Adicionar Odoo ao path
    sys.path.insert(0, '/usr/lib/python3/dist-packages')
    
    import odoo
    from odoo import api, SUPERUSER_ID
    
    # Conectar ao banco
    odoo.tools.config.parse_config(['-d', 'gzcon', '--db_host=db'])
    
    with odoo.api.Environment.manage():
        registry = odoo.registry('gzcon')
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Executar correção
            old_xmlids = env['ir.model.data'].search([
                ('module', '=', 'document_hub'),
                ('name', 'like', 'folder_%')
            ])
            
            print(f"\n🔍 Encontrados {len(old_xmlids)} XML IDs antigos 'document_hub.*'")
            
            for xmlid in old_xmlids:
                new_xmlid = env['ir.model.data'].search([
                    ('module', '=', 'document_hub_main'),
                    ('name', '=', xmlid.name)
                ])
                
                if new_xmlid:
                    print(f"✅ {xmlid.name}: novo XML ID já existe, removendo antigo")
                    xmlid.unlink()
                else:
                    print(f"🔄 {xmlid.name}: atualizando módulo para document_hub_main")
                    xmlid.module = 'document_hub_main'
            
            cr.commit()
            print(f"\n✅ Correção concluída! Atualize o módulo document_hub_main agora.")
