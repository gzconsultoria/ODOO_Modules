# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FinanceCategory(models.Model):
    _name = 'finance.category'
    _description = 'Finance Client Category'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Nome da Categoria',
        required=True,
        translate=True
    )
    
    sequence = fields.Integer(
        default=10,
        string='Sequência',
        help='Usado para ordenar categorias'
    )
    
    color = fields.Integer(
        'Índice de Cor',
        default=0,
        help='Cor para exibição de tags'
    )
    
    active = fields.Boolean(
        default=True,
        string='Ativo',
        help='Se desmarcado, a categoria ficará oculta'
    )
    
    description = fields.Text(
        'Descrição',
        translate=True
    )
    
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_finance_category_rel',
        'category_id',
        'partner_id',
        string='Clientes'
    )
    
    partner_count = fields.Integer(
        'Quantidade de Clientes',
        compute='_compute_partner_count'
    )
    
    def _compute_partner_count(self):
        """Count clients in this category"""
        for category in self:
            category.partner_count = len(category.partner_ids)
    
    @api.constrains('name')
    def _check_name_unique(self):
        """Ensure category name is unique"""
        for category in self:
            if category.name:
                duplicate = self.search([
                    ('name', '=', category.name),
                    ('id', '!=', category.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        'Nome da categoria deve ser único! '
                        'Já existe uma categoria com o nome "%s".'
                    ) % category.name)
