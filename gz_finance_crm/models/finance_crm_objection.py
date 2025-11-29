# -*- coding: utf-8 -*-

from odoo import models, fields


class FinanceCrmObjection(models.Model):
    _name = 'finance.crm.objection'
    _description = 'Objeção Comercial (CRM)'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Nome da Objeção',
        required=True,
        translate=True,
        help='Ex: Preço alto, Precisa consultar cônjuge'
    )
    
    sequence = fields.Integer(
        string='Sequência',
        default=10
    )
    
    color = fields.Integer(
        string='Cor',
        default=1,  # Vermelho por padrão
        help='Cor para exibição de tags'
    )
    
    active = fields.Boolean(
        string='Ativo',
        default=True
    )
    
    description = fields.Text(
        string='Descrição',
        translate=True
    )
    
    suggested_response = fields.Html(
        string='Resposta Sugerida',
        translate=True,
        help='Script ou argumentação para contornar esta objeção'
    )
