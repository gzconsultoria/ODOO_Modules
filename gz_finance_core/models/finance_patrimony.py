# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FinancePatrimony(models.Model):
    _name = 'finance.patrimony'
    _description = 'Finance Client Patrimony Snapshot'
    _order = 'date desc'
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    date = fields.Date(
        string='Data',
        required=True,
        default=fields.Date.today,
        index=True
    )
    
    # Asset breakdown by class
    fixed_income = fields.Monetary(
        'Renda Fixa',
        currency_field='currency_id',
        help='Títulos, CDBs, LCIs, etc.'
    )
    
    equities = fields.Monetary(
        'Ações',
        currency_field='currency_id',
        help='Ações, ETFs'
    )
    
    funds = fields.Monetary(
        'Fundos',
        currency_field='currency_id',
        help='Fundos de investimento'
    )
    
    real_estate = fields.Monetary(
        'Imóveis',
        currency_field='currency_id',
        help='Investimentos imobiliários, FIIs'
    )
    
    alternatives = fields.Monetary(
        'Alternativos',
        currency_field='currency_id',
        help='Private equity, hedge funds, cripto'
    )
    
    cash = fields.Monetary(
        'Caixa',
        currency_field='currency_id',
        help='Caixa e equivalentes'
    )
    
    total_value = fields.Monetary(
        'Valor Total',
        compute='_compute_total_value',
        store=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    # Variation tracking
    previous_total = fields.Monetary(
        'Total Anterior',
        currency_field='currency_id',
        readonly=True
    )
    
    variation_amount = fields.Monetary(
        'Variação (R$)',
        compute='_compute_variation',
        currency_field='currency_id'
    )
    
    variation_percent = fields.Float(
        'Variação %',
        compute='_compute_variation',
        digits=(16, 2)
    )
    
    source = fields.Selection([
        ('manual', 'Entrada Manual'),
        ('custody_integration', 'Integração Custodiante'),
        ('advisor_report', 'Relatório do Assessor'),
        ('client_declaration', 'Declaração do Cliente'),
    ], default='manual', required=True, string='Origem', index=True)
    
    notes = fields.Text('Observações')
    
    @api.depends('fixed_income', 'equities', 'funds', 'real_estate', 
                 'alternatives', 'cash')
    def _compute_total_value(self):
        """Calculate total patrimony value"""
        for patrimony in self:
            patrimony.total_value = (
                patrimony.fixed_income +
                patrimony.equities +
                patrimony.funds +
                patrimony.real_estate +
                patrimony.alternatives +
                patrimony.cash
            )
    
    @api.depends('total_value', 'previous_total')
    def _compute_variation(self):
        """Calculate variation from previous snapshot"""
        for patrimony in self:
            patrimony.variation_amount = patrimony.total_value - patrimony.previous_total
            if patrimony.previous_total:
                patrimony.variation_percent = (
                    (patrimony.variation_amount / patrimony.previous_total) * 100
                )
            else:
                patrimony.variation_percent = 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-fill previous_total from last snapshot"""
        for vals in vals_list:
            if 'partner_id' in vals:
                last_patrimony = self.search([
                    ('partner_id', '=', vals['partner_id'])
                ], limit=1, order='date desc')
                if last_patrimony:
                    vals['previous_total'] = last_patrimony.total_value
        
        return super().create(vals_list)
