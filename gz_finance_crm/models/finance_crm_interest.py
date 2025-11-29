# -*- coding: utf-8 -*-

from odoo import models, fields


class FinanceCrmInterest(models.Model):
    _name = 'finance.crm.interest'
    _description = 'Interesse de Investimento (CRM)'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Nome do Interesse',
        required=True,
        translate=True,
        help='Ex: Renda Fixa, Ações, FIIs, Fundos'
    )
    
    sequence = fields.Integer(
        string='Sequência',
        default=10,
        help='Usado para ordenar interesses'
    )
    
    color = fields.Integer(
        string='Cor',
        default=0,
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
