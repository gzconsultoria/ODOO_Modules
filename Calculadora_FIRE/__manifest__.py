# -*- coding: utf-8 -*-
{
    'name': 'Calculadora FIRE',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Calculadora de Independência Financeira (FIRE) para Website',
    'description': """
        Calculadora FIRE - Financial Independence, Retire Early
        ========================================================
        
        Adiciona um snippet arrastável ao Website Builder do Odoo que permite 
        aos visitantes calcular:
        
        * 🔥 FIRE Tradicional - Independência financeira total
        * ☕ Barista FIRE - Independência parcial com trabalho leve
        * 🌊 Coast FIRE - Piloto automático (parar de aportar)
        
        Características:
        * ✅ Cálculos em tempo real (100% client-side)
        * ✅ Interface responsiva e moderna
        * ✅ Salva preferências no localStorage
        * ✅ Validações inteligentes
        * ✅ Badges de conquista (milestones)
        * ✅ Modo real vs nominal (considera inflação)
        
        Uso: Website → Editar → Arrastar "Calculadora FIRE" para a página
    """,
    'author': 'Geovane Zomer - GZ Consultoria',
    'website': 'https://www.gzconsultoria.com.br',
    'license': 'LGPL-3',
    'depends': [
        'website',
    ],
    'data': [
        'views/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'Calculadora_FIRE/static/src/css/fire_calculator.css',
            'Calculadora_FIRE/static/src/js/fire_calculator.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
