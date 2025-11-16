# -*- coding: utf-8 -*-
{
    'name': 'CRM Wealth Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'CRM personalizado para Consultoria e Gestão de Investimentos',
    'description': """
        CRM Wealth Management
        =====================
        Módulo para gestão de consultoria financeira e wealth management com:
        
        - 6 etapas customizadas do funil de vendas
        - Abas dinâmicas que aparecem conforme progressão do lead
        - Campos específicos para cada etapa:
            * Captação
            * Qualificação
            * Reunião Estratégica
            * Proposta
            * Onboarding
            * Execução & Acompanhamento
        
        Ideal para consultorias financeiras, gestoras de patrimônio e assessorias de investimento.
    """,
    'author': 'GZ Consultoria',
    'website': 'https://www.gzconsultoria.com.br',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'sale_crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'views/crm_lead_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
