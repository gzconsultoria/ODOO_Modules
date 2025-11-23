# -*- coding: utf-8 -*-
from odoo import models, fields


class FinanceStrategyTag(models.Model):
    _name = 'finance.strategy.tag'
    _description = 'Tags de estratégias de investimento recomendadas'
    _order = 'name'
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Código da tag deve ser único!'),
    ]
    
    name = fields.Char(
        string='Estratégia',
        required=True,
        translate=True,
        help='Nome da estratégia de investimento'
    )
    code = fields.Char(
        string='Código',
        help='Código único para mapeamento com CRM (ex: BUY_HOLD, DIVIDENDOS)'
    )
    color = fields.Integer(
        string='Cor',
        default=0,
        help='Cor da tag na interface (0-11)'
    )
    active = fields.Boolean(
        default=True,
        help='Se desmarcado, a tag não ficará disponível'
    )
    description = fields.Text(
        string='Descrição',
        help='Descrição detalhada da estratégia'
    )
