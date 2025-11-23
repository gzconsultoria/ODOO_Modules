# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    finance_profile_ids = fields.One2many(
        "finance.profile",
        "partner_id",
        string="Perfis Financeiros"
    )
    finance_profile_count = fields.Integer(
        compute="_compute_finance_profile_count",
        string="Nº Perfis Financeiros"
    )

    @api.depends('finance_profile_ids')
    def _compute_finance_profile_count(self):
        for partner in self:
            partner.finance_profile_count = len(partner.finance_profile_ids)

    def action_open_finance_profile(self):
        """Abre o perfil financeiro do cliente"""
        self.ensure_one()
        
        # Se já existe perfil, abre ele
        if self.finance_profile_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Perfil Financeiro',
                'res_model': 'finance.profile',
                'res_id': self.finance_profile_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Senão, cria novo perfil
        return {
            'type': 'ir.actions.act_window',
            'name': 'Novo Perfil Financeiro',
            'res_model': 'finance.profile',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': self.id,
            },
        }
