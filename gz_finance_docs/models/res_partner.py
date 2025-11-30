# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Nota: finance_profile_id já existe em gz_finance_core (ex: FIN-29.11.2025-0008)
    # Não precisamos criar outro código, vamos reutilizar
    
    client_folder_id = fields.Many2one(
        'document_hub.folder',
        string='Pasta de Documentos',
        readonly=True,
        help='Pasta principal onde ficam armazenados os documentos deste cliente.'
    )
    
    document_count = fields.Integer(
        string='Total de Documentos',
        compute='_compute_document_count'
    )
    
    @api.depends('client_folder_id')
    def _compute_document_count(self):
        """Conta documentos vinculados ao cliente"""
        for partner in self:
            if partner.client_folder_id:
                # Busca docs na pasta do cliente e subpastas
                partner.document_count = self.env['document_hub.document'].search_count([
                    '|',
                    ('folder_id', '=', partner.client_folder_id.id),
                    ('folder_id.parent_folder_id', '=', partner.client_folder_id.id)
                ])
            else:
                partner.document_count = 0
    
    def action_view_documents(self):
        """Abre lista de documentos do cliente"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Documentos - {self.name}',
            'res_model': 'document_hub.document',
            'view_mode': 'tree,form',
            'domain': [
                '|',
                ('folder_id', '=', self.client_folder_id.id),
                ('folder_id.parent_folder_id', '=', self.client_folder_id.id)
            ],
            'context': {
                'default_partner_id': self.id,
                'default_folder_id': self.client_folder_id.id
            }
        }
