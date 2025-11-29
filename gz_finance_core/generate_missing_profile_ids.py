#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar Profile IDs para clientes existentes que não possuem
Executa via odoo shell para garantir acesso ao ORM
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def generate_missing_profile_ids(env):
    """Generate Profile IDs for existing finance clients without one"""
    
    # Find finance clients without profile ID
    partners_without_id = env['res.partner'].search([
        ('is_finance_client', '=', True),
        ('finance_profile_id', '=', False)
    ])
    
    if not partners_without_id:
        _logger.info("✅ Todos os clientes já possuem Profile ID")
        return
    
    _logger.info(f"🔍 Encontrados {len(partners_without_id)} clientes sem Profile ID")
    
    updated_count = 0
    for partner in partners_without_id:
        try:
            # Generate unique ID
            profile_id = partner._generate_profile_id()
            partner.write({'finance_profile_id': profile_id})
            updated_count += 1
            _logger.info(f"  ✅ {partner.name}: {profile_id}")
        except Exception as e:
            _logger.error(f"  ❌ Erro ao gerar ID para {partner.name}: {e}")
    
    _logger.info(f"\n📊 RESUMO:")
    _logger.info(f"  Total de clientes processados: {len(partners_without_id)}")
    _logger.info(f"  Profile IDs gerados: {updated_count}")
    _logger.info(f"  Falhas: {len(partners_without_id) - updated_count}")
    
    return updated_count

if __name__ == '__main__':
    # This script should be run via odoo shell:
    # docker exec -it odoo_modules-web-1 odoo shell -d gzcon --db_host db --db_user odoo --db_password odoo -c /etc/odoo/odoo.conf < generate_missing_profile_ids.py
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  Script de Geração de Profile IDs para Clientes Existentes    ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Este script deve ser executado via Odoo Shell:
    
    docker exec -it odoo_modules-web-1 odoo shell -d gzcon \\
        --db_host db --db_user odoo --db_password odoo \\
        -c /etc/odoo/odoo.conf \\
        < /mnt/extra-addons/gz_finance_core/generate_missing_profile_ids.py
    
    Ou via Python direto no container:
    
    docker exec -it odoo_modules-web-1 python3 \\
        /mnt/extra-addons/gz_finance_core/generate_missing_profile_ids.py
    """)
