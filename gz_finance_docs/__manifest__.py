# -*- coding: utf-8 -*-

{
    'name': 'GZ Finance - Gestão de Documentos',
    'version': '19.0.1.0.0',
    'author': 'GZ Consultoria (Adapted from Daniel Demedziuk)',
    'license': 'GPL-2',
    'sequence': 55,
    'category': 'Productivity/Documents',
    'summary': 'Sistema avançado de gestão de documentos financeiros',
    'description': """
Document hub
==================
An advanced document management module for Odoo 19 Community, inspired by the Odoo Enterprise "Documents" app. Enables centralized storage, categorization, sharing, and automation of document workflows within your company.

Key features:
- Store and organize files in folder structures and tags
- Share documents with users and groups
- Departmental document centralization (e.g., HR, Finance, Projects)
- Automatic tagging and classification on import
- Document versioning and change history
- Integration with other modules (Projects, Sales Orders, Contacts)
- Access rights per folder/tag
- Built-in preview for PDFs, images, videos
- Document template creation and management
- Advanced search and filtering
- Workflow automation: task assignment, notifications, validations
- Trash bin with restore capability
- Bulk operations on documents
- Extensions: OCR for text recognition from scans
- Extensions: e-signature integration (e.g., OCA Sign)
- Extensions: automatic import from email or network folders

This module is fully open source under the GPL-2 license.
""",
    'depends': [
        'base', 
        'mail',
        'project',
        'gz_finance_core',  # Menu Consultoria principal
        # 'sale_offer',  # Removido - módulo customizado não padrão
    ],
    'data': [
        # 1. SEGURANÇA (primeiro - define grupos e permissões)
        'security/document_hub_security.xml',
        'security/ir.model.access.csv',
        
        # 2. DADOS INICIAIS (sequências e dados padrão)
        'data/document_sequence.xml',
        'data/folders_data.xml',
        'data/tags_data.xml',
        'data/cron_data.xml',
        
        # 3. VIEWS QUE DEFINEM ACTIONS (ordem CRÍTICA)
        'views/document_hub_views.xml',           # Define: document_hub_mail_document_act, document_hub_company_document_act
        'views/config_views.xml',                 # Define: document_hub_folder_act, document_hub_tag_act
        'views/res_config_settings_views.xml',    # Define: document_hub_settings_action
        
        # 4. VIEWS SECUNDÁRIAS (dependem das anteriores)
        'views/project_views.xml',                # Usa actions definidas acima
        
        # 5. MENUS (ÚLTIMO - depende de TODOS os actions acima)
        'views/menu_views.xml',                   # Referencia todas as actions dos arquivos anteriores
    ],
    'assets': {
        'web.assets_backend': [
            'gz_finance_docs/static/src/css/document_hub.css',
        ],
    },
    'auto_install': False,
    'application': True,
    'installable': True,
}