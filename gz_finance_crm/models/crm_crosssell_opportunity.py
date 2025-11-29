# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CrmCrosssellOpportunity(models.Model):
    _name = 'crm.crosssell.opportunity'
    _description = 'Oportunidade de Cross-Sell'
    _order = 'opportunity_score desc, detection_date desc'
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
    
    # ================================
    # DADOS DA OPORTUNIDADE
    # ================================
    
    opportunity_type = fields.Selection([
        ('aum_growth', 'Crescimento de AUM'),
        ('new_service', 'Novo Serviço'),
        ('upsell_fee', 'Aumento de Fee'),
        ('portfolio_review', 'Revisão de Carteira'),
        ('tax_planning', 'Planejamento Tributário'),
    ], string='Tipo de Oportunidade', required=True, index=True)
    
    opportunity_score = fields.Float(
        string='Score da Oportunidade',
        help='Score 0-100: quanto maior, maior o potencial'
    )
    
    detection_date = fields.Datetime(
        string='Data de Detecção',
        default=fields.Datetime.now,
        readonly=True
    )
    
    # ================================
    # INDICADORES - AUM
    # ================================
    
    current_aum = fields.Monetary(
        string='AUM Atual',
        related='partner_id.aum',
        currency_field='currency_id',
        readonly=True
    )
    
    aum_growth_percent = fields.Float(
        string='Crescimento AUM (%)',
        related='partner_id.aum_growth_percent',
        readonly=True
    )
    
    estimated_wealth = fields.Monetary(
        string='Patrimônio Estimado (CRM)',
        currency_field='currency_id',
        help='Patrimônio estimado durante prospecção'
    )
    
    aum_divergence = fields.Float(
        string='Divergência AUM (%)',
        compute='_compute_aum_divergence',
        store=True,
        help='Diferença percentual entre patrimônio estimado e AUM real'
    )
    
    # ================================
    # POTENCIAL FINANCEIRO
    # ================================
    
    estimated_additional_aum = fields.Monetary(
        string='AUM Adicional Estimado',
        currency_field='currency_id',
        help='Potencial de captação adicional'
    )
    
    estimated_additional_revenue = fields.Monetary(
        string='Receita Adicional Estimada',
        currency_field='currency_id',
        compute='_compute_estimated_revenue',
        store=True
    )
    
    # ================================
    # AÇÕES
    # ================================
    
    status = fields.Selection([
        ('new', 'Nova'),
        ('contacted', 'Contato Realizado'),
        ('proposal_sent', 'Proposta Enviada'),
        ('won', 'Ganha'),
        ('lost', 'Perdida'),
        ('postponed', 'Adiada'),
    ], string='Status', default='new', required=True)
    
    lead_created = fields.Boolean(
        string='Lead Criado',
        default=False
    )
    
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead Relacionado',
        readonly=True
    )
    
    lead_creation_date = fields.Datetime(
        string='Data Criação Lead',
        readonly=True
    )
    
    # ================================
    # DETALHES
    # ================================
    
    description = fields.Text(
        string='Descrição',
        help='Descrição detalhada da oportunidade'
    )
    
    suggested_actions = fields.Text(
        string='Ações Sugeridas',
        help='Ações recomendadas para aproveitar a oportunidade'
    )
    
    notes = fields.Text('Observações')
    
    # ================================
    # METADADOS
    # ================================
    
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
    
    @api.depends('estimated_wealth', 'current_aum')
    def _compute_aum_divergence(self):
        """Calcular divergência entre patrimônio estimado e AUM real"""
        for record in self:
            if record.estimated_wealth and record.current_aum:
                if record.current_aum > 0:
                    divergence = ((record.estimated_wealth - record.current_aum) / record.current_aum) * 100
                    record.aum_divergence = divergence
                else:
                    record.aum_divergence = 100.0  # 100% se AUM atual é zero
            else:
                record.aum_divergence = 0.0
    
    @api.depends('estimated_additional_aum', 'partner_id.management_fee')
    def _compute_estimated_revenue(self):
        """Calcular receita adicional estimada"""
        for record in self:
            if record.estimated_additional_aum and record.partner_id.management_fee:
                # Receita anual = AUM * Fee%
                record.estimated_additional_revenue = (
                    record.estimated_additional_aum * record.partner_id.management_fee / 100
                )
            else:
                record.estimated_additional_revenue = 0.0
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_create_crosssell_lead(self):
        """Criar lead de cross-sell"""
        self.ensure_one()
        
        if self.lead_created:
            # Se já existe, apenas abrir
            return {
                'type': 'ir.actions.act_window',
                'name': 'Lead de Cross-Sell',
                'res_model': 'crm.lead',
                'res_id': self.lead_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Buscar estágio "Cross-Sell" (criar se não existir)
        crosssell_stage = self.env['crm.stage'].search([
            ('name', '=', 'Cross-Sell')
        ], limit=1)
        
        if not crosssell_stage:
            crosssell_stage = self.env['crm.stage'].create({
                'name': 'Cross-Sell',
                'sequence': 15,
                'fold': False,
                'is_won': False
            })
        
        # Montar descrição
        opportunity_types = dict(self._fields['opportunity_type'].selection)
        description = f"""
OPORTUNIDADE DE CROSS-SELL
===========================

Cliente: {self.partner_id.name}
Tipo: {opportunity_types.get(self.opportunity_type)}
Score: {self.opportunity_score:.1f}/100

INDICADORES:
- AUM Atual: R$ {self.current_aum:,.2f}
- Crescimento AUM: {self.aum_growth_percent:.1f}%
- Potencial Adicional: R$ {self.estimated_additional_aum:,.2f}
- Receita Adicional Estimada: R$ {self.estimated_additional_revenue:,.2f}/ano

{self.description or ''}

AÇÕES SUGERIDAS:
{self.suggested_actions or 'A definir'}
        """
        
        # Criar lead
        lead_vals = {
            'name': f'💰 Cross-Sell: {opportunity_types.get(self.opportunity_type)} - {self.partner_id.name}',
            'partner_id': self.partner_id.id,
            'type': 'opportunity',
            'stage_id': crosssell_stage.id,
            'description': description,
            'expected_revenue': self.estimated_additional_revenue,
            'priority': '2' if self.opportunity_score >= 70 else '1',
        }
        
        lead = self.env['crm.lead'].create(lead_vals)
        
        # Atualizar oportunidade
        self.write({
            'lead_created': True,
            'lead_id': lead.id,
            'lead_creation_date': fields.Datetime.now(),
            'status': 'contacted'
        })
        
        _logger.info(f"Lead de cross-sell criado: #{lead.id} para cliente {self.partner_id.name} (Score: {self.opportunity_score:.1f})")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead de Cross-Sell',
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    # ================================
    # CRON JOB
    # ================================
    
    @api.model
    def _cron_detect_crosssell_opportunities(self):
        """
        Cron job diário: Detectar oportunidades de cross-sell
        
        Critérios:
        1. AUM cresceu >20% nos últimos 3 meses
        2. Divergência entre patrimônio estimado e AUM real >30%
        3. Clientes com alto AUM mas fee baixo
        """
        _logger.info("=== INICIANDO DETECÇÃO DE CROSS-SELL ===")
        
        # Critério 1: Crescimento de AUM
        high_growth_clients = self.env['res.partner'].search([
            ('is_finance_client', '=', True),
            ('aum_growth_percent', '>=', 20.0)
        ])
        
        _logger.info(f"Encontrados {len(high_growth_clients)} clientes com crescimento AUM >20%")
        
        opportunities_created = 0
        for client in high_growth_clients:
            # Verificar se já existe oportunidade ativa
            existing = self.search([
                ('partner_id', '=', client.id),
                ('opportunity_type', '=', 'aum_growth'),
                ('status', 'in', ['new', 'contacted', 'proposal_sent'])
            ], limit=1)
            
            if existing:
                continue
            
            # Calcular score (baseado em crescimento)
            score = min(client.aum_growth_percent * 2, 100)
            
            # Estimar AUM adicional (assumir que vai crescer mais 50% do crescimento atual)
            additional_aum = client.aum * (client.aum_growth_percent / 100) * 0.5
            
            # Criar oportunidade
            self.create({
                'partner_id': client.id,
                'opportunity_type': 'aum_growth',
                'opportunity_score': score,
                'estimated_additional_aum': additional_aum,
                'description': f'Cliente apresentou crescimento de {client.aum_growth_percent:.1f}% no AUM nos últimos 3 meses.',
                'suggested_actions': 'Entrar em contato para entender origem dos novos recursos e oferecer produtos adicionais.'
            })
            opportunities_created += 1
        
        _logger.info(f"=== DETECÇÃO CONCLUÍDA: {opportunities_created} oportunidades de cross-sell criadas ===")
        
        return True
