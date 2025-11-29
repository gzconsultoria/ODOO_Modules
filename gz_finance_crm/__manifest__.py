# -*- coding: utf-8 -*-
{
    'name': 'GZ Finance CRM',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'CRM especializado para Consultoria Financeira integrado com Finance Core',
    'description': """
        GZ Finance CRM
        ==============
        
        Módulo CRM especializado para consultoria financeira e wealth management.
        
        Funcionalidades Principais:
        - Funil de vendas com 8 estágios customizados
        - Integração perfeita com gz_finance_core
        - Popup automático ao atingir estágio Onboarding
        - Botão inteligente "Perfil Financeiro" (cria ou abre)
        - Zero duplicação de dados
        - Campos específicos para qualificação comercial
        
        Novos Recursos (Sprint 1-4):
        ✅ LGPD & Compliance:
           - Gestão de consentimento LGPD
           - Audit log completo de todas ações
           - Rastreamento de IP e user agent
        
        ✅ Prevenção de Churn:
           - Detecção automática de risco de churn
           - Score baseado em AUM, engajamento, reuniões
           - Criação automática de leads de retenção
        
        ✅ Cross-Sell Intelligence:
           - Detecção de oportunidades baseada em crescimento AUM
           - Alertas de divergência entre patrimônio estimado e real
           - Criação automática de leads de cross-sell
        
        ✅ Sistema de Aprovações:
           - Workflow para fees acima do padrão
           - Aprovação de deals grandes
           - Descontos e exceções de regra
        
        ✅ Google Calendar (Sprint 4 - preparado):
           - Criação automática de reuniões Google Meet
           - Sincronização de eventos
           - Links diretos no CRM
    """,
    'author': 'GZ Consultoria',
    'website': 'https://www.gzconsultoria.com.br',
    'license': 'LGPL-3',
    'depends': [
        'crm',
        'gz_finance_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/finance_crm_demo_data.xml',
        'data/crm_cron_jobs.xml',
        'wizard/finance_profile_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/finance_crm_config_views.xml',
        'views/crm_compliance_views.xml',
        'views/crm_churn_views.xml',
        'views/crm_crosssell_views.xml',
        'views/crm_approval_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
