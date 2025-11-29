# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FinanceProfileWizard(models.TransientModel):
    _name = 'finance.profile.wizard'
    _description = 'Assistente de Criação de Perfil Financeiro'
    
    lead_id = fields.Many2one(
        'crm.lead',
        string='Oportunidade',
        required=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente'
    )
    
    # Preview de informações
    lead_name = fields.Char(
        related='lead_id.name',
        readonly=True,
        string='Nome do Lead'
    )
    
    company_currency = fields.Many2one(
        related='lead_id.company_currency',
        readonly=True
    )
    
    expected_revenue = fields.Monetary(
        related='lead_id.expected_revenue',
        readonly=True,
        string='Receita Esperada',
        currency_field='company_currency'
    )
    
    estimated_wealth = fields.Monetary(
        related='lead_id.estimated_wealth',
        readonly=True,
        string='Patrimônio Estimado',
        currency_field='company_currency'
    )
    
    # Opção de criação
    create_now = fields.Boolean(
        string='Criar Perfil Agora',
        default=True,
        help='Marque para criar o perfil financeiro imediatamente'
    )
    
    def action_confirm(self):
        """Criar perfil financeiro ou adiar"""
        self.ensure_one()
        
        if self.create_now:
            # CRIAR PERFIL FINANCEIRO
            return self._create_finance_profile()
        else:
            # NÃO CRIAR AGORA (usuário clicou "Não")
            # Apenas fechar o popup
            return {'type': 'ir.actions.act_window_close'}
    
    def _create_finance_profile(self):
        """Criar perfil financeiro e abrir formulário"""
        
        try:
            # 1. Garantir que existe res.partner
            if not self.partner_id:
                self.partner_id = self.lead_id._create_customer()
                self.lead_id.partner_id = self.partner_id
            
            # 2. ATIVAR perfil financeiro
            self.partner_id.write({'is_finance_client': True})
            _logger.info(f"Perfil financeiro ativado para {self.partner_id.name} (Lead #{self.lead_id.id})")
            
            # 3. Transferir dados do CRM usando método do lead
            self.lead_id._transfer_crm_data_to_finance()
            
            # 4. ABRIR formulário do perfil financeiro
            return {
                'type': 'ir.actions.act_window',
                'name': f'Perfil Financeiro - {self.partner_id.name}',
                'res_model': 'res.partner',
                'res_id': self.partner_id.id,
                'view_mode': 'form',
                'target': 'current',  # Tela cheia (não popup)
                'context': {
                    'form_view_initial_mode': 'edit',  # Abrir em modo edição
                }
            }
        except Exception as e:
            _logger.error(f"Erro ao criar perfil financeiro: {str(e)}", exc_info=True)
            raise UserError(_(
                "Erro ao criar perfil financeiro.\n\n"
                "Detalhes: %s\n\n"
                "Entre em contato com o administrador se o problema persistir."
            ) % str(e))
