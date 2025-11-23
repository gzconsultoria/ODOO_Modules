# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from passlib.context import CryptContext


class FinanceProfileDeleteWizard(models.TransientModel):
    _name = "finance.profile.delete.wizard"
    _description = "Wizard de Exclusão Segura de Perfil Financeiro"

    profile_id = fields.Many2one("finance.profile", required=True, ondelete="cascade")
    profile_name = fields.Char(string="Nome do Perfil", readonly=True)
    admin_password = fields.Char(string="Senha do Administrador", required=True)
    confirmation_text = fields.Char(string="Digite 'EXCLUIR' para confirmar")
    
    def action_confirm_delete(self):
        """Valida senha e exclui o perfil."""
        self.ensure_one()
        
        # Validação 1: Confirmar texto
        if self.confirmation_text != 'EXCLUIR':
            raise ValidationError(_("Você deve digitar exatamente 'EXCLUIR' para confirmar a exclusão."))
        
        # Validação 2: Verificar senha do admin
        user = self.env.user
        if not user.has_group('base.group_system'):
            raise UserError(_("Apenas administradores podem excluir perfis financeiros."))
        
        # Verifica senha usando o mesmo método do Odoo
        crypt_context = CryptContext(schemes=['pbkdf2_sha512', 'plaintext'], deprecated=['plaintext'])
        
        if not user.password or not crypt_context.verify(self.admin_password, user.password):
            raise ValidationError(_("❌ Senha incorreta! A exclusão foi cancelada por segurança."))
        
        # Registra no chatter antes de excluir
        profile_name = self.profile_id.display_name
        partner_name = self.profile_id.partner_id.name
        
        self.profile_id.message_post(
            body=_(
                "🗑️ <strong>PERFIL EXCLUÍDO PERMANENTEMENTE</strong><br/>"
                "Administrador: %s<br/>"
                "Data: %s<br/>"
                "Cliente: %s<br/>"
                "⚠️ Esta ação é irreversível."
            ) % (user.name, fields.Datetime.now(), partner_name)
        )
        
        # Exclui o perfil
        self.profile_id.unlink()
        
        # Notificação de sucesso
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('✅ Perfil Excluído'),
                'message': _('O perfil financeiro "%s" foi excluído permanentemente.') % profile_name,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }
