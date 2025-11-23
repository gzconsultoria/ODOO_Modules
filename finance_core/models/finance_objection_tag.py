# -*- coding: utf-8 -*-
from odoo import models, fields


class FinanceObjectionTag(models.Model):
    _name = 'finance.objection.tag'
    _description = 'Tags de objeções apresentadas pelo cliente'
    _order = 'name'
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Código da tag deve ser único!'),
    ]
    
    name = fields.Char(
        string='Objeção',
        required=True,
        translate=True,
        help='Tipo de objeção apresentada'
    )
    code = fields.Char(
        string='Código',
        help='Código único para mapeamento com CRM (ex: PRECO_ALTO, SEM_TEMPO)'
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
        help='Descrição e estratégia para tratar essa objeção'
    )
