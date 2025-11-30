# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Folder(models.Model):
    _name = 'document_hub.folder'
    _description = 'Document hub: Folder'
    _rec_name = 'parent_path'

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(string='Active', default=True)
    description = fields.Html(string='Description', translate=True)
    sequence = fields.Integer('Sequence', default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda lm: lm.env.company)
    parent_folder_id = fields.Many2one('document_hub.folder', string='Parent folder', ondelete='cascade')
    children_folder_ids = fields.One2many('document_hub.folder', 'parent_folder_id', string='Sub folder')
    document_ids = fields.One2many('document_hub.document', 'folder_id', string='Documents')
    parent_path = fields.Char(index=True, unaccent=False, compute='_compute_parent_path', store=True, translate=True)

    visibility_administration = fields.Boolean(string='Administration', default=False)
    visibility_purchasing_and_logistics = fields.Boolean(string='Purchasing and logistics', default=False)
    visibility_marketing = fields.Boolean(string='Marketing', default=False)
    visibility_accounting = fields.Boolean(string='Accounting', default=False)
    visibility_pm = fields.Boolean(string='PM', default=False)
    visibility_hr = fields.Boolean(string='HR', default=False)
    visibility_salesman = fields.Boolean(string='Sales', default=False)
    is_project = fields.Boolean(string="Is project", default=False, help='Mark this option if you are sure this folder is for projects.')
    
    # Campos para automação de pastas de clientes
    client_folder = fields.Boolean(
        string='Pasta de Cliente', 
        default=False, 
        index=True,
        help='Indica que esta pasta foi criada automaticamente para um cliente específico.'
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Cliente Vinculado', 
        index=True,
        help='Cliente ao qual esta pasta está vinculada (se aplicável).'
    )
    client_code = fields.Char(
        string='Código do Cliente',
        related='partner_id.finance_profile_id',
        store=True,
        help='ID único do perfil financeiro (ex: FIN-29.11.2025-0008).'
    )
    is_client_subfolder = fields.Boolean(
        string='É Subpasta de Cliente',
        compute='_compute_is_client_subfolder',
        store=True,
        help='Indica se esta pasta é uma subpasta de uma pasta de cliente.'
    )

    @api.depends('parent_folder_id', 'name', 'client_folder')
    def _compute_parent_path(self):
        for rec in self:
            name = _(rec.name)
            
            if rec.parent_folder_id:
                parent_folder = _(rec.parent_folder_id.name)
                
                # Se a pasta PAI é "Clientes" e esta é uma pasta de cliente,
                # não adicionar prefixo (evita "Clientes: Nome Cliente")
                if rec.parent_folder_id.name == '📁 Clientes' and rec.client_folder:
                    rec.parent_path = name
                else:
                    rec.parent_path = F"{parent_folder}: {name}"
            else:
                rec.parent_path = name
    
    @api.depends('parent_folder_id', 'parent_folder_id.client_folder')
    def _compute_is_client_subfolder(self):
        """Identifica se a pasta é subpasta de uma pasta de cliente"""
        for rec in self:
            if rec.parent_folder_id and rec.parent_folder_id.client_folder:
                rec.is_client_subfolder = True
            else:
                rec.is_client_subfolder = False

