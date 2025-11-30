# -*- coding: utf-8 -*-
{
    "name": "Finance CRM Integration",
    "summary": "Sincronização automática entre CRM e Finance Core",
    "description": """
Finance CRM Integration
========================

Sincronização automática entre CRM nativo do Odoo e Finance Core:

* Visibilidade de abas sincronizada com estágio do Lead no CRM
* Finance Profile criado automaticamente quando Lead chega em 'Execução'
* Dados do Lead copiados para Finance Profile
* Relacionamento bidirecional: Lead ↔ Finance Profile

**Regras de Visibilidade (baseadas em stage.sequence):**

* Estágio seq >= 10 → 👤 Dados Pessoais
* Estágio seq >= 20 → + 🎯 Objetivos  
* Estágio seq >= 30 → + 🔍 Diagnóstico
* Estágio seq >= 40 → + 💼 Proposta
* Estágio seq >= 50 → + 🟡 Onboarding
* Estágio seq >= 60 → + 🟤 Execução & Acompanhamento

**Nota:** Funciona com QUALQUER estágio do CRM que tenha sequence configurada.
    """,
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "GZ Consultoria",
    "website": "https://gzconsultoria.com.br",
    "category": "Sales/Financial Planning",
    "depends": [
        "crm",          # CRM nativo do Odoo
        "finance_core", # Perfis financeiros
        "gz_finance_docs", # Sistema de documentos
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/finance_tag_mapping.xml",  # Tags padrão (Interesses, Estratégias, Objeções)
        "views/finance_crm_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
