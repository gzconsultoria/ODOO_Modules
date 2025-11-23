# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FinanceProfile(models.Model):
    _inherit = "finance.profile"

    def _compute_pending_documents(self):
        super()._compute_pending_documents()

    # ============================================================
    # COMPLIANCE INTEGRADO (Novo Sistema)
    # ============================================================
    compliance_id = fields.Many2one(
        "finance.compliance",
        string="Compliance",
        help="Gestão de documentos e compliance regulatório integrado com Documents + Sign",
    )
    compliance_score = fields.Integer(
        related="compliance_id.compliance_score",
        string="Score de Compliance (%)",
        store=True,
    )
    compliance_state = fields.Selection(
        related="compliance_id.compliance_state",
        string="Status Compliance",
        store=True,
    )
    pending_signatures_count = fields.Integer(
        related="compliance_id.pending_signatures_count",
        string="Assinaturas Pendentes",
    )
    document_count = fields.Integer(
        related="compliance_id.document_count",
        string="Total de Documentos",
    )
    
    # ============================================================
    # LEGACY (Sistema Antigo de Compliance - será migrado)
    # ============================================================
    document_ids = fields.One2many(
        "finance.document",
        "profile_id",
        string="Documentos (Legacy)",
    )
    recommendation_ids = fields.One2many(
        "finance.recommendation",
        "profile_id",
        string="Recomendações",
    )
    compliance_log_ids = fields.One2many(
        "finance.compliance.log",
        "profile_id",
        string="Logs de compliance",
    )

    @api.model
    def create(self, vals):
        """Cria compliance automaticamente ao criar perfil."""
        profile = super().create(vals)
        
        # Cria registro de compliance integrado
        if "finance.compliance" in self.env:
            compliance = self.env["finance.compliance"].create({
                "profile_id": profile.id,
            })
            profile.compliance_id = compliance
        
        return profile
    
    # ============================================================
    # AÇÕES RÁPIDAS DE COMPLIANCE
    # ============================================================
    
    def action_open_documents_folder(self):
        """Abre pasta do cliente em Documents."""
        self.ensure_one()
        if self.compliance_id:
            return self.compliance_id.action_open_documents_folder()
        return False
    
    def action_send_contract_for_signature(self):
        """Envia contrato para assinatura digital."""
        self.ensure_one()
        if self.compliance_id:
            return self.compliance_id.action_send_contract_for_signature()
        return False
    
    def action_view_pending_signatures(self):
        """Visualiza assinaturas pendentes."""
        self.ensure_one()
        if self.compliance_id:
            return self.compliance_id.action_view_pending_signatures()
        return False
    
    def action_open_compliance_record(self):
        """Abre o registro de compliance em form view."""
        self.ensure_one()
        if not self.compliance_id:
            return False
        
        return {
            "type": "ir.actions.act_window",
            "name": "Compliance",
            "res_model": "finance.compliance",
            "res_id": self.compliance_id.id,
            "view_mode": "form",
            "target": "current",
        }
