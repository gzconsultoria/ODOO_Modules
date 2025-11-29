# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CrmLgpdConsent(models.Model):
    _name = 'crm.lgpd.consent'
    _description = 'Registro de Consentimento LGPD'
    _order = 'consent_date desc, id desc'
    _rec_name = 'lead_id'
    
    # ================================
    # CAMPOS PRINCIPAIS
    # ================================
    
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead/Oportunidade',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='lead_id.partner_id',
        store=True,
        readonly=True
    )
    
    # ================================
    # DADOS DO CONSENTIMENTO
    # ================================
    
    consent_date = fields.Datetime(
        string='Data/Hora do Consentimento',
        required=True,
        default=fields.Datetime.now,
        index=True
    )
    
    consent_type = fields.Selection([
        ('explicit', 'Consentimento Explícito'),
        ('implicit', 'Consentimento Implícito'),
        ('legitimate_interest', 'Interesse Legítimo'),
    ], string='Tipo de Consentimento', required=True, default='explicit')
    
    consent_purpose = fields.Selection([
        ('prospecting', 'Prospecção Comercial'),
        ('service_provision', 'Prestação de Serviços'),
        ('marketing', 'Marketing e Comunicação'),
        ('analytics', 'Análise e Estatísticas'),
        ('legal_obligation', 'Obrigação Legal'),
    ], string='Finalidade', required=True, default='prospecting')
    
    consent_granted = fields.Boolean(
        string='Consentimento Concedido',
        default=True,
        help='Se False, indica que o consentimento foi negado ou revogado'
    )
    
    # ================================
    # DADOS TÉCNICOS
    # ================================
    
    ip_address = fields.Char(
        string='Endereço IP',
        help='IP de onde o consentimento foi registrado'
    )
    
    user_agent = fields.Text(
        string='User Agent',
        help='Navegador/dispositivo usado'
    )
    
    consent_method = fields.Selection([
        ('web_form', 'Formulário Web'),
        ('phone_call', 'Ligação Telefônica'),
        ('email', 'E-mail'),
        ('in_person', 'Presencial'),
        ('crm_manual', 'Manual no CRM'),
    ], string='Método de Captura', default='crm_manual')
    
    # ================================
    # GESTÃO DE REVOGAÇÃO
    # ================================
    
    revoked_date = fields.Datetime(
        string='Data Revogação',
        readonly=True
    )
    
    revoked_reason = fields.Text(
        string='Motivo da Revogação'
    )
    
    is_active = fields.Boolean(
        string='Consentimento Ativo',
        compute='_compute_is_active',
        store=True
    )
    
    # ================================
    # CAMPOS COMPLEMENTARES
    # ================================
    
    notes = fields.Text('Observações')
    
    user_id = fields.Many2one(
        'res.users',
        string='Registrado por',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.company,
        required=True
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    @api.depends('consent_granted', 'revoked_date')
    def _compute_is_active(self):
        """Consentimento ativo = concedido E não revogado"""
        for record in self:
            record.is_active = record.consent_granted and not record.revoked_date
    
    # ================================
    # METHODS
    # ================================
    
    def action_revoke_consent(self):
        """Revogar consentimento"""
        for record in self:
            record.write({
                'revoked_date': fields.Datetime.now(),
                'consent_granted': False
            })
            _logger.info(f"Consentimento LGPD revogado para Lead #{record.lead_id.id}")
    
    @api.model
    def check_consent_for_lead(self, lead_id, purpose='prospecting'):
        """Verificar se existe consentimento ativo para um lead"""
        return self.search([
            ('lead_id', '=', lead_id),
            ('consent_purpose', '=', purpose),
            ('is_active', '=', True)
        ], limit=1)
