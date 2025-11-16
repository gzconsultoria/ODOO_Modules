# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmWealthAcompanhamento(models.Model):
    _name = 'crm.wealth.acompanhamento'
    _description = 'Acompanhamento Mensal do Cliente'
    _order = 'data_reuniao desc'

    name = fields.Char(
        string='Título da Reunião',
        required=True,
        default='Acompanhamento Mensal'
    )
    
    lead_id = fields.Many2one(
        'crm.lead',
        string='Oportunidade',
        required=True,
        ondelete='cascade'
    )
    
    data_reuniao = fields.Date(
        string='Data da Reunião',
        required=True,
        default=fields.Date.context_today
    )
    
    valor_portfolio = fields.Monetary(
        string='Valor do Portfólio',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moeda',
        default=lambda self: self.env.company.currency_id
    )
    
    rentabilidade_periodo = fields.Float(
        string='Rentabilidade no Período (%)',
        digits=(16, 2)
    )
    
    mudancas_realizadas = fields.Text(
        string='Mudanças Realizadas',
        help='Rebalanceamento, novos aportes, mudança de estratégia'
    )
    
    proximos_passos = fields.Text(
        string='Próximos Passos'
    )
    
    observacoes = fields.Text(
        string='Observações'
    )
    
    satisfacao_cliente = fields.Selection([
        ('muito_insatisfeito', 'Muito Insatisfeito'),
        ('insatisfeito', 'Insatisfeito'),
        ('neutro', 'Neutro'),
        ('satisfeito', 'Satisfeito'),
        ('muito_satisfeito', 'Muito Satisfeito'),
    ], string='Satisfação do Cliente')
