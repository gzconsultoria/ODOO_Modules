# -*- coding: utf-8 -*-
{
    'name': 'GZ Finance Core',
    'version': '19.0.1.0.0',
    'category': 'Finance',
    'sequence': 1,
    'summary': 'Core module for investment advisory - SSOT for financial data',
    'description': """
        Finance Core - Single Source of Truth (SSOT)
        ==============================================
        
        Core module for investment advisory operations.
        
        Features:
        ---------
        * Client profiles and financial data management
        * AUM (Assets Under Management) calculation and tracking
        * KYC and compliance status tracking
        * Risk profile management
        * Client segmentation (Retail, Affluent, HNW, UHNW)
        * Patrimony tracking over time
        * Multi-advisor support
        * Automated KYC expiry notifications
        * Scheduled AUM updates
        
        This module serves as the foundation for all finance-related modules
        in the ecosystem, providing centralized data and business rules.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    
    'depends': [
        'base',
        'contacts',
        'mail',           # Chatter and notifications
        'web',            # Web interface
        'crm',            # Necessário para origin_lead_id
    ],
    
    # Módulos opcionais (auto_install se disponíveis)
    'external_dependencies': {
        'odoo': ['gz_finance_docs'],  # Sistema de documentos (opcional)
    },
    
    'data': [
        # Security - ALWAYS FIRST
        'security/finance_security.xml',
        'security/ir.model.access.csv',
        
        # Data - Seed data and sequences
        'data/finance_data.xml',
        'data/finance_cron.xml',
        'data/finance_actions.xml',
        'data/finance_aum_snapshot_cron.xml',
        
        # Views com Actions (ANTES do menu!)
        'views/res_partner_views.xml',
        'views/res_partner_search_views.xml',
        'views/finance_patrimony_views.xml',  # Contém action_finance_patrimony
        'views/finance_category_views.xml',   # Contém action_finance_categories
        'views/finance_aum_snapshot_views.xml',  # Contém action_finance_aum_snapshots
        
        # Menu POR ÚLTIMO (depende das actions acima)
        'views/finance_menu.xml',
    ],
    
    'demo': [],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
