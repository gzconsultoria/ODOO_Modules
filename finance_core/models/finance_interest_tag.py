# -*- coding: utf-8 -*-
from odoo import models, fields


class FinanceInterestTag(models.Model):
    _name = 'finance.interest.tag'
    _description = 'Tags de interesses do investidor'
    _order = 'name'
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Código da tag deve ser único!'),
    ]
    
    name = fields.Char(
        string='Interesse',
        required=True,
        translate=True,
        help='Tipo de investimento ou interesse financeiro'
    )
    code = fields.Char(
        string='Código',
        help='Código único para mapeamento com CRM (ex: RENDA_FIXA, ACOES)'
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
        help='Descrição detalhada do tipo de investimento'
    )
