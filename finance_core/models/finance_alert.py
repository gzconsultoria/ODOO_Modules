# -*- coding: utf-8 -*-
from odoo import fields, models


class FinanceAlert(models.Model):
    _name = "finance.alert"
    _description = "Alerta inteligente de consultoria"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "state, trigger_date desc"

    name = fields.Char(string="Nome", required=True)
    profile_id = fields.Many2one("finance.profile", string="Perfil", required=True, ondelete="cascade", index=True)
    trigger_date = fields.Date(string="Data", default=fields.Date.context_today, index=True)
    resolved_date = fields.Date(string="Data de resolução", readonly=True)
    state = fields.Selection(
        [("open", "Aberto"), ("in_progress", "Em andamento"), ("done", "Concluído")],
        default="open",
        required=True,
        index=True,
        tracking=True,
    )
    category = fields.Selection(
        [
            ("goal", "Meta"),
            ("portfolio", "Carteira"),
            ("cashflow", "Fluxo de caixa"),
            ("compliance", "Compliance"),
            ("document", "Documento"),
            ("meeting", "Reunião"),
        ],
        string="Categoria",
        required=True,
        default="goal",
        index=True,
    )
    description = fields.Text(string="Descrição")
    action_required = fields.Text(string="Ação necessária")
    responsible_id = fields.Many2one("res.users", string="Responsável", default=lambda self: self.env.user)
    company_id = fields.Many2one(
        "res.company",
        string="Empresa",
        related="profile_id.company_id",
        store=True,
        readonly=True,
    )

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            for alert in self:
                if alert.state == "done" and not alert.resolved_date:
                    alert.resolved_date = fields.Date.context_today(alert)
                elif alert.state != "done" and alert.resolved_date:
                    alert.resolved_date = False
        return res

