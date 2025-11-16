#!/usr/bin/env python3
"""
Script de teste para verificar a visibilidade das abas do CRM Wealth
"""

import xmlrpc.client

# Configurações
url = 'http://localhost:8069'
db = 'consultoria'
username = 'admin'
password = 'admin'

# Conecta ao Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✓ Autenticado como admin (uid: {uid})")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Busca stages do Wealth Management
    stages = models.execute_kw(db, uid, password,
        'crm.stage', 'search_read',
        [[['sequence', 'in', [10, 20, 30, 40, 50, 60]]]],
        {'fields': ['name', 'sequence']})
    
    print("\n📊 Estágios Wealth Management:")
    for stage in stages:
        print(f"  - {stage['name']} (seq: {stage['sequence']})")
    
    # Busca um lead de exemplo
    leads = models.execute_kw(db, uid, password,
        'crm.lead', 'search_read',
        [[]],
        {'fields': ['name', 'stage_id', 'stage_sequence', 'show_captacao', 
                    'show_qualificacao', 'show_reuniao', 'show_proposta', 
                    'show_onboarding', 'show_execucao'],
         'limit': 1})
    
    if leads:
        lead = leads[0]
        print(f"\n📝 Lead: {lead['name']}")
        print(f"  Stage: {lead['stage_id'][1] if lead['stage_id'] else 'N/A'}")
        print(f"  Stage Sequence: {lead.get('stage_sequence', 'N/A')}")
        print("\n  Visibilidade das Abas:")
        print(f"    🔵 Captação: {lead.get('show_captacao', False)}")
        print(f"    🟢 Qualificação: {lead.get('show_qualificacao', False)}")
        print(f"    🟣 Reunião: {lead.get('show_reuniao', False)}")
        print(f"    🟠 Proposta: {lead.get('show_proposta', False)}")
        print(f"    🟡 Onboarding: {lead.get('show_onboarding', False)}")
        print(f"    🟤 Execução: {lead.get('show_execucao', False)}")
    else:
        print("\n⚠️  Nenhum lead encontrado")
else:
    print("✗ Falha na autenticação")
