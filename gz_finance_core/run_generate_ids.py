#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para gerar Profile IDs via Odoo Shell
Uso: cat este_arquivo.py | docker exec -i odoo_modules-web-1 odoo shell -d gzcon
"""

# Executar método do modelo
result = env['res.partner'].action_generate_missing_profile_ids()

# Mostrar resultado
if result and 'params' in result:
    print("\n" + "="*60)
    print(result['params']['title'])
    print("="*60)
    print(result['params']['message'])
    print("="*60 + "\n")
else:
    print("Ação executada com sucesso")
