# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    # ================================
    # CAMPOS - Qualificação Comercial
    # ================================
    
    estimated_wealth = fields.Monetary(
        string='Patrimônio Estimado',
        currency_field='company_currency',
        help='Estimativa aproximada para qualificação comercial (não é o AUM real do Finance Core)'
    )
    
    estimated_income_range = fields.Selection([
        ('0-10k', 'Até R$ 10 mil/mês'),
        ('10k-30k', 'R$ 10 mil - R$ 30 mil/mês'),
        ('30k-100k', 'R$ 30 mil - R$ 100 mil/mês'),
        ('100k+', 'Acima R$ 100 mil/mês'),
    ], string='Faixa de Renda Estimada')
    
    # ================================
    # CAMPOS - Interesses e Objeções
    # ================================
    
    investment_interest_ids = fields.Many2many(
        'finance.crm.interest',
        string='Interesses de Investimento',
        help='Áreas de interesse mencionadas durante prospecção'
    )
    
    preliminary_risk_profile = fields.Selection([
        ('conservative', 'Conservador'),
        ('moderate', 'Moderado'),
        ('aggressive', 'Arrojado'),
    ], string='Perfil Preliminar (CRM)', 
       help='Avaliação inicial - o perfil definitivo fica no Finance Core')
    
    main_pain_point = fields.Selection([
        ('no_time', 'Não tem tempo para gerenciar'),
        ('no_knowledge', 'Falta conhecimento técnico'),
        ('poor_results', 'Resultados ruins atuais'),
        ('organization', 'Desorganização financeira'),
        ('fear', 'Medo de investir errado'),
    ], string='Dor Principal')
    
    urgency_level = fields.Selection([
        ('low', 'Baixa - Explorando opções'),
        ('medium', 'Média - Quer decidir em 30 dias'),
        ('high', 'Alta - Urgente'),
    ], string='Nível de Urgência')
    
    objection_ids = fields.Many2many(
        'finance.crm.objection',
        string='Objeções Levantadas'
    )
    
    objection_notes = fields.Html(
        string='Notas sobre Objeções',
        help='Descreva como as objeções foram tratadas, argumentos utilizados, estratégias aplicadas'
    )
    
    competitor_comparison = fields.Char(
        string='Concorrentes Mencionados',
        help='Ex: XP, BTG, Genial'
    )
    
    # ================================
    # CAMPOS - Proposta Comercial
    # ================================
    
    proposal_sent_date = fields.Date('Data Envio Proposta')
    proposed_fee = fields.Float('Fee Proposto (%)', digits=(5, 2))
    
    # ================================
    # CAMPOS - Status de Perfil Financeiro
    # ================================
    
    has_finance_profile = fields.Boolean(
        string='Tem Perfil Financeiro',
        compute='_compute_has_finance_profile',
        store=True,  # Performance: usado em domains e views
        help='Indica se o cliente já possui perfil financeiro ativo'
    )
    
    finance_profile_id = fields.Char(
        string='ID Perfil',
        related='partner_id.finance_profile_id',
        readonly=True
    )
    
    # ================================
    # CAMPOS - Score e Temperatura
    # ================================
    
    lead_score = fields.Integer(
        string='Score do Lead',
        compute='_compute_lead_score',
        store=True,
        help='0-100 baseado em: patrimônio, urgência, interesse'
    )
    
    lead_temperature = fields.Selection([
        ('cold', '🔵 Frio'),
        ('warm', '🟡 Morno'),
        ('hot', '🔴 Quente'),
    ], string='Temperatura', compute='_compute_lead_temperature', store=True)
    
    # ================================
    # CAMPOS - Sprint 3: Divergência AUM
    # ================================
    
    aum_divergence = fields.Float(
        string='Divergência AUM (%)',
        compute='_compute_aum_divergence',
        store=True,
        help='Diferença percentual entre patrimônio estimado (CRM) e AUM real (Finance Core)'
    )
    
    aum_divergence_alert = fields.Selection([
        ('none', 'Sem Alerta'),
        ('minor', 'Divergência Pequena'),
        ('moderate', 'Divergência Moderada'),
        ('critical', 'Divergência Crítica'),
    ], string='Alerta de Divergência', compute='_compute_aum_divergence', store=True)
    
    # ================================
    # CAMPOS - Sprint 4: Google Calendar
    # ================================
    
    google_event_id = fields.Char(
        string='ID do Evento Google',
        readonly=True,
        help='ID do evento no Google Calendar'
    )
    
    meeting_link = fields.Char(
        string='Link da Reunião',
        help='Link do Google Meet gerado automaticamente'
    )
    
    meeting_scheduled_date = fields.Datetime(
        string='Data/Hora da Reunião',
        help='Data e hora agendada para reunião'
    )
    
    auto_create_meeting = fields.Boolean(
        string='Criar Reunião Automaticamente',
        default=False,
        help='Se marcado, cria reunião Google Meet ao mover para estágio "Reunião"'
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('partner_id', 'partner_id.is_finance_client')
    def _compute_has_finance_profile(self):
        """Verificar se o cliente já tem perfil financeiro"""
        for lead in self:
            lead.has_finance_profile = (
                lead.partner_id and 
                lead.partner_id.is_finance_client
            )
    
    @api.depends('estimated_wealth', 'urgency_level', 'investment_interest_ids', 'preliminary_risk_profile')
    def _compute_lead_score(self):
        """Calcular score do lead (0-100)"""
        for lead in self:
            score = 0
            
            # Patrimônio estimado (40 pontos)
            if lead.estimated_wealth:
                if lead.estimated_wealth >= 5000000:  # R$ 5M+
                    score += 40
                elif lead.estimated_wealth >= 1000000:  # R$ 1M+
                    score += 30
                elif lead.estimated_wealth >= 500000:  # R$ 500k+
                    score += 20
                else:
                    score += 10
            
            # Urgência (30 pontos)
            if lead.urgency_level == 'high':
                score += 30
            elif lead.urgency_level == 'medium':
                score += 20
            elif lead.urgency_level == 'low':
                score += 10
            
            # Interesses definidos (20 pontos)
            if len(lead.investment_interest_ids) >= 3:
                score += 20
            elif len(lead.investment_interest_ids) >= 1:
                score += 10
            
            # Perfil de risco definido (10 pontos)
            if lead.preliminary_risk_profile:
                score += 10
            
            lead.lead_score = min(score, 100)
    
    @api.depends('lead_score')
    def _compute_lead_temperature(self):
        """Calcular temperatura do lead baseado no score"""
        for lead in self:
            if lead.lead_score >= 70:
                lead.lead_temperature = 'hot'
            elif lead.lead_score >= 40:
                lead.lead_temperature = 'warm'
            else:
                lead.lead_temperature = 'cold'
    
    @api.depends('estimated_wealth', 'partner_id.aum')
    def _compute_aum_divergence(self):
        """Calcular divergência entre patrimônio estimado e AUM real"""
        for lead in self:
            if lead.estimated_wealth and lead.partner_id and lead.partner_id.aum:
                # Se AUM real for maior que zero
                if lead.partner_id.aum > 0:
                    divergence = ((lead.estimated_wealth - lead.partner_id.aum) / lead.partner_id.aum) * 100
                    lead.aum_divergence = abs(divergence)
                    
                    # Classificar alerta
                    if abs(divergence) >= 50:
                        lead.aum_divergence_alert = 'critical'
                    elif abs(divergence) >= 30:
                        lead.aum_divergence_alert = 'moderate'
                    elif abs(divergence) >= 15:
                        lead.aum_divergence_alert = 'minor'
                    else:
                        lead.aum_divergence_alert = 'none'
                else:
                    lead.aum_divergence = 0.0
                    lead.aum_divergence_alert = 'none'
            else:
                lead.aum_divergence = 0.0
                lead.aum_divergence_alert = 'none'
    
    # ================================
    # OVERRIDE METHODS
    # ================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para registrar audit log"""
        leads = super().create(vals_list)
        
        # Registrar criação no audit log
        for lead in leads:
            if 'crm.audit.log' in self.env:
                self.env['crm.audit.log'].log_action(
                    model_name='crm.lead',
                    res_id=lead.id,
                    action_type='create',
                    severity='low',
                    notes=f'Lead criado: {lead.name}'
                )
        
        return leads
    
    def write(self, vals):
        """Detectar mudança para estágio Onboarding (ganho) e registrar audit log"""
        
        # Guardar estágios antigos
        old_stages = {lead.id: lead.stage_id for lead in self}
        
        # Executar write padrão
        res = super().write(vals)
        
        # Registrar mudanças importantes no audit log
        if 'crm.audit.log' in self.env:
            for lead in self:
                # Log mudança de estágio
                if 'stage_id' in vals:
                    old_stage = old_stages.get(lead.id)
                    if old_stage:
                        self.env['crm.audit.log'].log_action(
                            model_name='crm.lead',
                            res_id=lead.id,
                            action_type='stage_change',
                            field_name='stage_id',
                            old_value=old_stage.name,
                            new_value=lead.stage_id.name,
                            severity='medium',
                            notes=f'Mudança de estágio: {old_stage.name} → {lead.stage_id.name}'
                        )
        
        # Verificar se mudou de estágio
        if 'stage_id' in vals:
            popup_action = None
            for lead in self:
                old_stage = old_stages.get(lead.id)
                new_stage = lead.stage_id
                
                # Chegou no estágio Onboarding (is_won=True)
                if new_stage.is_won and (not old_stage or not old_stage.is_won):
                    _logger.info(f"Lead #{lead.id} '{lead.name}' movido para Onboarding (Ganho)")
                    
                    # Se ainda NÃO tem perfil financeiro, preparar popup
                    if not lead.has_finance_profile:
                        popup_action = lead._trigger_finance_profile_creation()
                        _logger.info(f"Popup de perfil financeiro preparado para Lead #{lead.id}")
            
            # Retornar popup apenas uma vez (para o último lead sem perfil)
            if popup_action:
                return popup_action
        
        return res
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def _trigger_finance_profile_creation(self):
        """Mostrar popup de criação de perfil financeiro"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Criar Perfil Financeiro',
            'res_model': 'finance.profile.wizard',
            'view_mode': 'form',
            'target': 'new',  # Modal popup
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
            }
        }
    
    def action_open_finance_profile(self):
        """Botão inteligente PERFIL FINANCEIRO
        
        Comportamento:
        - Se JÁ TEM perfil: abre o perfil existente
        - Se NÃO TEM perfil: cria e abre para preenchimento
        """
        self.ensure_one()
        
        # Garantir que existe res.partner
        if not self.partner_id:
            self.partner_id = self._create_customer()
        
        # CASO 1: JÁ TEM PERFIL - Abrir existente
        if self.partner_id.is_finance_client:
            return {
                'type': 'ir.actions.act_window',
                'name': f'Perfil Financeiro - {self.partner_id.name}',
                'res_model': 'res.partner',
                'res_id': self.partner_id.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'form_view_initial_mode': 'readonly',
                }
            }
        
        # CASO 2: NÃO TEM PERFIL - Criar e abrir
        else:
            # Ativar perfil financeiro
            self.partner_id.write({'is_finance_client': True})
            
            # Transferir dados básicos do CRM
            self._transfer_crm_data_to_finance()
            
            # Abrir em modo edição para preenchimento
            return {
                'type': 'ir.actions.act_window',
                'name': f'Novo Perfil Financeiro - {self.partner_id.name}',
                'res_model': 'res.partner',
                'res_id': self.partner_id.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'form_view_initial_mode': 'edit',
                }
            }
    
    def _transfer_crm_data_to_finance(self):
        """Transferir dados do CRM para Finance Core (quando aplicável)"""
        self.ensure_one()
        
        if not self.partner_id:
            _logger.warning(f"Tentativa de transferência sem partner_id para Lead #{self.id}")
            return
        
        transfer_data = {}
        
        # Transferir perfil de risco preliminar
        if self.preliminary_risk_profile:
            transfer_data['risk_profile'] = self.preliminary_risk_profile
        
        # Transferir proposta comercial
        if self.expected_revenue:
            transfer_data['proposal_amount'] = self.expected_revenue
        
        if self.proposed_fee:
            transfer_data['management_fee'] = self.proposed_fee
        
        # Data da proposta
        if self.proposal_sent_date:
            transfer_data['proposal_date'] = self.proposal_sent_date
        
        # Aplicar transferência
        if transfer_data:
            self.partner_id.write(transfer_data)
            _logger.info(f"Dados transferidos CRM→Finance para {self.partner_id.name}: {list(transfer_data.keys())}")
        
        # Criar snapshot inicial se tiver estimativa de patrimônio
        if self.estimated_wealth and self.estimated_wealth > 0:
            # Validar se modelo existe
            if 'finance.patrimony' in self.env:
                self.env['finance.patrimony'].create({
                    'partner_id': self.partner_id.id,
                    'date': fields.Date.today(),
                    'total_value': self.estimated_wealth,
                    'source': 'crm_estimate',
                    'notes': f'Estimativa inicial do CRM\nLead: {self.name} (#{self.id})\nData conversão: {fields.Date.today()}'
                })
                _logger.info(f"Snapshot patrimônio criado: R$ {self.estimated_wealth:,.2f} para {self.partner_id.name}")
            else:
                _logger.warning("Modelo finance.patrimony não encontrado - snapshot não criado")
