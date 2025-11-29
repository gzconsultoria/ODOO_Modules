# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CrmApproval(models.Model):
    _name = 'crm.approval'
    _description = 'Sistema de Aprovações CRM'
    _order = 'request_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'approval_type'
    
    # ================================
    # CAMPOS PRINCIPAIS
    # ================================
    
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead/Oportunidade',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='lead_id.partner_id',
        store=True,
        readonly=True
    )
    
    # ================================
    # TIPO DE APROVAÇÃO
    # ================================
    
    approval_type = fields.Selection([
        ('high_fee', 'Fee Acima do Padrão'),
        ('large_deal', 'Deal Acima do Limite'),
        ('special_discount', 'Desconto Especial'),
        ('exception_rule', 'Exceção de Regra'),
        ('custom_contract', 'Contrato Customizado'),
    ], string='Tipo de Aprovação', required=True, tracking=True)
    
    # ================================
    # DADOS DA SOLICITAÇÃO
    # ================================
    
    request_date = fields.Datetime(
        string='Data da Solicitação',
        default=fields.Datetime.now,
        required=True,
        readonly=True
    )
    
    requested_by = fields.Many2one(
        'res.users',
        string='Solicitado por',
        default=lambda self: self.env.user,
        required=True,
        readonly=True,
        tracking=True
    )
    
    reason = fields.Text(
        string='Justificativa',
        required=True,
        help='Explicação detalhada do motivo da solicitação'
    )
    
    # ================================
    # VALORES (para aprovações financeiras)
    # ================================
    
    proposed_fee = fields.Float(
        string='Fee Proposto (%)',
        digits=(5, 2),
        help='Fee proposto que necessita aprovação'
    )
    
    standard_fee = fields.Float(
        string='Fee Padrão (%)',
        digits=(5, 2),
        help='Fee padrão da empresa para comparação'
    )
    
    deal_value = fields.Monetary(
        string='Valor do Deal',
        currency_field='currency_id',
        help='Valor total do deal/AUM envolvido'
    )
    
    approval_threshold = fields.Monetary(
        string='Limite de Aprovação',
        currency_field='currency_id',
        help='Limite acima do qual é necessária aprovação'
    )
    
    # ================================
    # WORKFLOW DE APROVAÇÃO
    # ================================
    
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('pending', 'Aguardando Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('cancelled', 'Cancelado'),
    ], string='Status', default='draft', required=True, tracking=True, index=True)
    
    approver_id = fields.Many2one(
        'res.users',
        string='Aprovador',
        domain=[('groups_id', 'in', [])],  # Será configurado para group_manager
        tracking=True
    )
    
    approval_date = fields.Datetime(
        string='Data da Aprovação/Rejeição',
        readonly=True,
        tracking=True
    )
    
    approval_notes = fields.Text(
        string='Observações do Aprovador',
        help='Comentários do aprovador sobre a decisão'
    )
    
    # ================================
    # PRIORIDADE E SLA
    # ================================
    
    priority = fields.Selection([
        ('0', 'Baixa'),
        ('1', 'Normal'),
        ('2', 'Alta'),
        ('3', 'Urgente'),
    ], string='Prioridade', default='1')
    
    deadline = fields.Datetime(
        string='Prazo para Aprovação',
        help='Data limite para decisão'
    )
    
    is_overdue = fields.Boolean(
        string='Atrasado',
        compute='_compute_is_overdue',
        store=True
    )
    
    # ================================
    # METADADOS
    # ================================
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        """Verificar se aprovação está atrasada"""
        now = fields.Datetime.now()
        for record in self:
            if record.state == 'pending' and record.deadline:
                record.is_overdue = record.deadline < now
            else:
                record.is_overdue = False
    
    # ================================
    # VALIDATIONS
    # ================================
    
    @api.constrains('proposed_fee', 'standard_fee')
    def _check_fee_values(self):
        """Validar valores de fee"""
        for record in self:
            if record.approval_type == 'high_fee':
                if not record.proposed_fee or not record.standard_fee:
                    raise ValidationError(_("Para aprovação de fee, informe o fee proposto e o padrão."))
                if record.proposed_fee <= record.standard_fee:
                    raise ValidationError(_("O fee proposto deve ser maior que o padrão."))
    
    @api.constrains('deal_value', 'approval_threshold')
    def _check_deal_values(self):
        """Validar valores de deal"""
        for record in self:
            if record.approval_type == 'large_deal':
                if not record.deal_value or not record.approval_threshold:
                    raise ValidationError(_("Para aprovação de deal, informe o valor e o limite."))
                if record.deal_value <= record.approval_threshold:
                    raise ValidationError(_("O valor do deal deve ser maior que o limite."))
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_submit_for_approval(self):
        """Enviar para aprovação"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Apenas solicitações em rascunho podem ser enviadas."))
            
            # Definir aprovador padrão (manager do sales team)
            if not record.approver_id:
                # Buscar manager do lead
                if record.lead_id.team_id and record.lead_id.team_id.user_id:
                    record.approver_id = record.lead_id.team_id.user_id
                else:
                    # Buscar primeiro usuário do grupo manager
                    managers = self.env.ref('sales_team.group_sale_manager').users
                    if managers:
                        record.approver_id = managers[0]
            
            # Calcular deadline (2 dias úteis)
            deadline = fields.Datetime.now()
            # Simplificação: adicionar 48h
            from datetime import timedelta
            deadline = deadline + timedelta(hours=48)
            
            record.write({
                'state': 'pending',
                'deadline': deadline
            })
            
            # Criar atividade para o aprovador
            record.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=record.approver_id.id,
                summary=f'Aprovar: {dict(record._fields["approval_type"].selection).get(record.approval_type)}',
                note=f'Solicitação de aprovação para Lead: {record.lead_id.name}\n\nJustificativa: {record.reason}'
            )
            
            _logger.info(f"Aprovação #{record.id} enviada para {record.approver_id.name}")
    
    def action_approve(self):
        """Aprovar solicitação"""
        for record in self:
            if record.state != 'pending':
                raise UserError(_("Apenas solicitações pendentes podem ser aprovadas."))
            
            if self.env.user != record.approver_id:
                raise UserError(_("Apenas o aprovador designado pode aprovar esta solicitação."))
            
            record.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now()
            })
            
            # Marcar atividades como concluídas
            record.activity_ids.action_feedback(feedback='Aprovado')
            
            # Notificar solicitante
            record.message_post(
                body=f"✅ Aprovação concedida por {self.env.user.name}",
                subject="Aprovação Concedida",
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )
            
            _logger.info(f"Aprovação #{record.id} aprovada por {self.env.user.name}")
    
    def action_reject(self):
        """Rejeitar solicitação"""
        for record in self:
            if record.state != 'pending':
                raise UserError(_("Apenas solicitações pendentes podem ser rejeitadas."))
            
            if self.env.user != record.approver_id:
                raise UserError(_("Apenas o aprovador designado pode rejeitar esta solicitação."))
            
            record.write({
                'state': 'rejected',
                'approval_date': fields.Datetime.now()
            })
            
            # Marcar atividades como concluídas
            record.activity_ids.action_feedback(feedback='Rejeitado')
            
            # Notificar solicitante
            record.message_post(
                body=f"❌ Aprovação rejeitada por {self.env.user.name}\n\nMotivo: {record.approval_notes or 'Não especificado'}",
                subject="Aprovação Rejeitada",
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )
            
            _logger.info(f"Aprovação #{record.id} rejeitada por {self.env.user.name}")
    
    def action_cancel(self):
        """Cancelar solicitação"""
        for record in self:
            if record.state in ['approved', 'rejected']:
                raise UserError(_("Solicitações já decididas não podem ser canceladas."))
            
            record.write({'state': 'cancelled'})
            record.activity_ids.unlink()
            
            _logger.info(f"Aprovação #{record.id} cancelada")
