# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CrmChurnIndicator(models.Model):
    _name = 'crm.churn.indicator'
    _description = 'Indicador de Risco de Churn'
    _order = 'churn_risk_score desc, last_check_date desc'
    _rec_name = 'partner_id'
    
    # ================================
    # CAMPOS PRINCIPAIS
    # ================================
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade',
        index=True,
        domain=[('is_finance_client', '=', True)]
    )
    
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead Relacionado',
        help='Lead/oportunidade que originou este cliente (se existir)'
    )
    
    # ================================
    # MÉTRICAS DE RISCO
    # ================================
    
    churn_risk_score = fields.Float(
        string='Score de Risco',
        compute='_compute_churn_risk_score',
        store=True,
        help='Score 0-100: quanto maior, maior o risco de churn'
    )
    
    risk_level = fields.Selection([
        ('low', 'Baixo Risco'),
        ('medium', 'Risco Médio'),
        ('high', 'Risco Alto'),
        ('critical', 'Risco Crítico'),
    ], string='Nível de Risco', compute='_compute_risk_level', store=True)
    
    # ================================
    # INDICADORES - AUM
    # ================================
    
    current_aum = fields.Monetary(
        string='AUM Atual',
        related='partner_id.aum',
        currency_field='currency_id',
        readonly=True
    )
    
    aum_3months_ago = fields.Monetary(
        string='AUM (3 meses atrás)',
        currency_field='currency_id',
        help='Valor do AUM há 3 meses'
    )
    
    aum_decline_percent = fields.Float(
        string='Queda AUM (%)',
        compute='_compute_aum_metrics',
        store=True,
        help='Percentual de queda do AUM nos últimos 3 meses'
    )
    
    # ================================
    # INDICADORES - ENGAJAMENTO
    # ================================
    
    last_meeting_date = fields.Date(
        string='Última Reunião',
        related='partner_id.suitability_last_review',
        readonly=True
    )
    
    days_since_last_meeting = fields.Integer(
        string='Dias desde última reunião',
        compute='_compute_engagement_metrics',
        store=True
    )
    
    meetings_last_6months = fields.Integer(
        string='Reuniões (6 meses)',
        help='Número de reuniões nos últimos 6 meses'
    )
    
    response_rate = fields.Float(
        string='Taxa de Resposta (%)',
        help='Percentual de e-mails/mensagens respondidas'
    )
    
    # ================================
    # AÇÕES E ALERTAS
    # ================================
    
    alert_created = fields.Boolean(
        string='Alerta Criado',
        default=False,
        help='Indica se já foi criado um lead de alerta'
    )
    
    alert_lead_id = fields.Many2one(
        'crm.lead',
        string='Lead de Alerta',
        readonly=True,
        help='Lead criado automaticamente para ação de retenção'
    )
    
    alert_date = fields.Datetime(
        string='Data do Alerta',
        readonly=True
    )
    
    # ================================
    # METADADOS
    # ================================
    
    last_check_date = fields.Datetime(
        string='Última Verificação',
        default=fields.Datetime.now,
        readonly=True
    )
    
    notes = fields.Text('Observações')
    
    currency_id = fields.Many2one(
        'res.currency',
        related='partner_id.currency_id',
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    @api.depends('current_aum', 'aum_3months_ago')
    def _compute_aum_metrics(self):
        """Calcular queda percentual do AUM"""
        for record in self:
            if record.aum_3months_ago and record.aum_3months_ago > 0:
                decline = ((record.aum_3months_ago - record.current_aum) / record.aum_3months_ago) * 100
                record.aum_decline_percent = decline if decline > 0 else 0.0
            else:
                record.aum_decline_percent = 0.0
    
    @api.depends('last_meeting_date')
    def _compute_engagement_metrics(self):
        """Calcular métricas de engajamento"""
        today = fields.Date.today()
        for record in self:
            if record.last_meeting_date:
                delta = today - record.last_meeting_date
                record.days_since_last_meeting = delta.days
            else:
                record.days_since_last_meeting = 9999  # Valor alto para indicar "nunca teve"
    
    @api.depends('aum_decline_percent', 'days_since_last_meeting', 
                 'meetings_last_6months', 'response_rate')
    def _compute_churn_risk_score(self):
        """
        Calcular score de risco de churn (0-100)
        
        Fatores:
        - Queda AUM: 40 pontos
        - Tempo desde última reunião: 30 pontos
        - Número de reuniões: 20 pontos
        - Taxa de resposta: 10 pontos
        """
        for record in self:
            score = 0.0
            
            # 1. Queda de AUM (0-40 pontos)
            if record.aum_decline_percent >= 30:
                score += 40
            elif record.aum_decline_percent >= 20:
                score += 30
            elif record.aum_decline_percent >= 10:
                score += 20
            elif record.aum_decline_percent > 0:
                score += 10
            
            # 2. Tempo desde última reunião (0-30 pontos)
            days = record.days_since_last_meeting
            if days >= 180:  # 6 meses
                score += 30
            elif days >= 120:  # 4 meses
                score += 25
            elif days >= 90:  # 3 meses
                score += 15
            elif days >= 60:  # 2 meses
                score += 5
            
            # 3. Número de reuniões últimos 6 meses (0-20 pontos)
            meetings = record.meetings_last_6months or 0
            if meetings == 0:
                score += 20
            elif meetings == 1:
                score += 15
            elif meetings == 2:
                score += 10
            elif meetings == 3:
                score += 5
            # 4+ reuniões = 0 pontos (bom engajamento)
            
            # 4. Taxa de resposta (0-10 pontos)
            response = record.response_rate or 0
            if response < 20:
                score += 10
            elif response < 40:
                score += 7
            elif response < 60:
                score += 4
            
            record.churn_risk_score = min(score, 100.0)
    
    @api.depends('churn_risk_score')
    def _compute_risk_level(self):
        """Classificar nível de risco"""
        for record in self:
            score = record.churn_risk_score
            if score >= 70:
                record.risk_level = 'critical'
            elif score >= 50:
                record.risk_level = 'high'
            elif score >= 30:
                record.risk_level = 'medium'
            else:
                record.risk_level = 'low'
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_create_retention_lead(self):
        """Criar lead de alerta para ação de retenção"""
        self.ensure_one()
        
        if self.alert_created:
            raise UserError(_("Alerta já foi criado para este cliente."))
        
        # Buscar estágio "Alerta de Churn" (criar se não existir)
        churn_stage = self.env['crm.stage'].search([
            ('name', '=', 'Alerta de Churn')
        ], limit=1)
        
        if not churn_stage:
            churn_stage = self.env['crm.stage'].create({
                'name': 'Alerta de Churn',
                'sequence': 99,
                'fold': False,
                'is_won': False
            })
        
        # Criar lead
        lead_vals = {
            'name': f'🚨 Risco Churn - {self.partner_id.name}',
            'partner_id': self.partner_id.id,
            'type': 'opportunity',
            'stage_id': churn_stage.id,
            'description': f"""
ALERTA DE RISCO DE CHURN
========================

Cliente: {self.partner_id.name}
Score de Risco: {self.churn_risk_score:.1f}/100
Nível de Risco: {dict(self._fields['risk_level'].selection).get(self.risk_level)}

INDICADORES:
- AUM Atual: R$ {self.current_aum:,.2f}
- Queda AUM (3 meses): {self.aum_decline_percent:.1f}%
- Dias desde última reunião: {self.days_since_last_meeting}
- Reuniões (6 meses): {self.meetings_last_6months}
- Taxa de resposta: {self.response_rate:.1f}%

AÇÃO NECESSÁRIA:
Entrar em contato com urgência para entender motivos e propor ações de retenção.
            """,
            'priority': '3',  # Alta prioridade
        }
        
        lead = self.env['crm.lead'].create(lead_vals)
        
        # Atualizar indicador
        self.write({
            'alert_created': True,
            'alert_lead_id': lead.id,
            'alert_date': fields.Datetime.now()
        })
        
        _logger.info(f"Lead de retenção criado: #{lead.id} para cliente {self.partner_id.name} (Risco: {self.churn_risk_score:.1f})")
        
        # Retornar action para abrir o lead
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead de Retenção',
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    # ================================
    # CRON JOB
    # ================================
    
    @api.model
    def _cron_detect_churn_risk(self):
        """
        Cron job diário: Detectar clientes em risco de churn
        
        Critérios:
        - Score >= 50 (risco alto ou crítico)
        - Ainda não tem alerta criado
        """
        _logger.info("=== INICIANDO DETECÇÃO DE RISCO DE CHURN ===")
        
        # Buscar indicadores de alto risco sem alerta
        high_risk_indicators = self.search([
            ('churn_risk_score', '>=', 50),
            ('alert_created', '=', False)
        ])
        
        _logger.info(f"Encontrados {len(high_risk_indicators)} clientes em risco alto/crítico")
        
        leads_created = 0
        for indicator in high_risk_indicators:
            try:
                indicator.action_create_retention_lead()
                leads_created += 1
            except Exception as e:
                _logger.error(f"Erro ao criar lead para {indicator.partner_id.name}: {str(e)}")
        
        _logger.info(f"=== DETECÇÃO CONCLUÍDA: {leads_created} leads de retenção criados ===")
        
        return True
