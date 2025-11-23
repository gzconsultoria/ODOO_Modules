# -*- coding: utf-8 -*-
{
    "name": "Finance Compliance",
    "summary": "Compliance integrado com Documents e Sign - Documentos, assinaturas digitais e checklist",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "author": "Finance Suite",
    "depends": ["finance_core", "finance_planning", "finance_investments", "mail"],
    "external_dependencies": {
        "python": [],
    },
    # Módulos Enterprise OPCIONAIS (funcionam sem eles, mas com menos recursos)
    # Se tiver 'documents' instalado: integração DMS completa com pastas auto-criadas
    # Se tiver 'sign' instalado: assinaturas digitais certificadas
    # Para instalar: precisa de licença Odoo Enterprise
    "data": [
        "security/ir.model.access.csv",
        "data/finance_compliance_data.xml",
        "data/finance_brokerage_data.xml",
        "views/finance_recommendation_views.xml",
        "views/finance_compliance_views.xml",
        "views/finance_compliance_integrated_views.xml",
        "views/finance_profile_views.xml",
        "wizard/finance_recommendation_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
