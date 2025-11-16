# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # ============================================================
    # CONFIGURAÇÕES DE CÁLCULO FINANCEIRO
    # ============================================================
    
    wealth_taxa_padrao = fields.Float(
        string='Taxa de Retorno Padrão (% a.a.)',
        default=10.0,
        config_parameter='crm_wealth.taxa_padrao',
        help='Taxa anual usada para cálculos de aporte necessário. Ex: 10 = 10% ao ano'
    )
    
    wealth_taxa_conservadora = fields.Float(
        string='Taxa Conservadora (% a.a.)',
        default=6.0,
        config_parameter='crm_wealth.taxa_conservadora',
        help='Cenário conservador para simulações'
    )
    
    wealth_taxa_moderada = fields.Float(
        string='Taxa Moderada (% a.a.)',
        default=10.0,
        config_parameter='crm_wealth.taxa_moderada',
        help='Cenário moderado para simulações'
    )
    
    wealth_taxa_agressiva = fields.Float(
        string='Taxa Agressiva (% a.a.)',
        default=15.0,
        config_parameter='crm_wealth.taxa_agressiva',
        help='Cenário agressivo para simulações'
    )
    
    # ============================================================
    # CONFIGURAÇÕES DE SLA E NOTIFICAÇÕES
    # ============================================================
    
    wealth_sla_captacao = fields.Integer(
        string='SLA Captação (dias)',
        default=7,
        config_parameter='crm_wealth.sla_captacao',
        help='Número de dias antes de alertar sobre lead parado em Captação'
    )
    
    wealth_sla_qualificacao = fields.Integer(
        string='SLA Qualificação (dias)',
        default=5,
        config_parameter='crm_wealth.sla_qualificacao',
        help='Número de dias antes de alertar sobre lead parado em Qualificação'
    )
    
    wealth_sla_reuniao = fields.Integer(
        string='SLA Pós-Reunião (dias)',
        default=3,
        config_parameter='crm_wealth.sla_reuniao',
        help='Número de dias após reunião para enviar follow-up'
    )
    
    wealth_sla_proposta = fields.Integer(
        string='SLA Proposta (dias)',
        default=5,
        config_parameter='crm_wealth.sla_proposta',
        help='Número de dias antes de alertar sobre proposta sem resposta'
    )
    
    wealth_sla_onboarding = fields.Integer(
        string='SLA Onboarding (dias)',
        default=15,
        config_parameter='crm_wealth.sla_onboarding',
        help='Número de dias antes de alertar sobre onboarding atrasado'
    )
    
    # Habilitar/desabilitar SLAs
    wealth_sla_enabled = fields.Boolean(
        string='Habilitar SLAs Automáticos',
        default=True,
        config_parameter='crm_wealth.sla_enabled',
        help='Ativa o sistema de notificações e alertas de SLA'
    )
