# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class FinanceCompliance(models.Model):
    _name = "finance.compliance"
    _description = "Gestão de Compliance Financeiro"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # ============================================================
    # RELACIONAMENTOS COM FINANCE CORE
    # ============================================================
    profile_id = fields.Many2one(
        "finance.profile",
        required=True,
        ondelete="cascade",
        string="Perfil Financeiro",
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        related="profile_id.partner_id",
        store=True,
        string="Cliente",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="profile_id.company_id",
        store=True,
        string="Empresa",
    )

    # ============================================================
    # INTEGRAÇÃO COM DOCUMENTS (Odoo Enterprise)
    # ============================================================
    folder_id = fields.Many2one(
        "documents.folder",
        string="Pasta de Documentos",
        help="Pasta automática criada em Documents para este cliente",
        tracking=True,
    )
    document_ids = fields.Many2many(
        "documents.document",
        compute="_compute_documents",
        string="Documentos",
        help="Todos os documentos do cliente (busca por partner_id + folder_id)",
    )
    document_count = fields.Integer(
        compute="_compute_documents",
        string="Total de Documentos",
    )

    # ============================================================
    # INTEGRAÇÃO COM SIGN (Odoo Enterprise)
    # ============================================================
    sign_request_ids = fields.Many2many(
        "sign.request",
        compute="_compute_sign_requests",
        string="Solicitações de Assinatura",
    )
    pending_signatures_count = fields.Integer(
        compute="_compute_sign_requests",
        string="Assinaturas Pendentes",
    )
    signed_count = fields.Integer(
        compute="_compute_sign_requests",
        string="Documentos Assinados",
    )

    # ============================================================
    # COMPLIANCE CHECKLIST (Computados automaticamente)
    # ============================================================
    contract_signed = fields.Boolean(
        string="✅ Contrato Assinado",
        compute="_compute_compliance_status",
        store=True,
        help="Contrato de consultoria assinado digitalmente",
    )
    suitability_completed = fields.Boolean(
        string="✅ Suitability Completo",
        compute="_compute_compliance_status",
        store=True,
        help="Análise de perfil de investidor preenchida",
    )
    personal_docs_complete = fields.Boolean(
        string="✅ Docs Pessoais Completos",
        compute="_compute_compliance_status",
        store=True,
        help="CNH/RG, Comprovante Residência, Certidões, Procurações",
    )
    brokerage_selected = fields.Boolean(
        string="✅ Corretora Selecionada",
        compute="_compute_compliance_status",
        store=True,
        help="Cliente escolheu pelo menos uma corretora",
    )
    compliance_score = fields.Integer(
        string="Score (%)",
        compute="_compute_compliance_score",
        store=True,
        help="0-100% baseado no checklist completo",
    )
    compliance_state = fields.Selection(
        [
            ("draft", "Não Iniciado"),
            ("in_progress", "Em Andamento"),
            ("pending_signatures", "Pendente Assinaturas"),
            ("complete", "Completo"),
            ("expired", "Documentos Vencidos"),
        ],
        default="draft",
        compute="_compute_compliance_state",
        store=True,
        string="Status",
        tracking=True,
    )

    # ============================================================
    # CORRETORAS SELECIONADAS
    # ============================================================
    brokerage_ids = fields.Many2many(
        "finance.brokerage",
        string="Corretoras",
        help="Clear, XP, BTG, Genial, Rico, Banco Inter, etc.",
        tracking=True,
    )

    # ============================================================
    # CHECKLIST DE DOCUMENTOS REQUERIDOS
    # ============================================================
    required_document_ids = fields.One2many(
        "finance.compliance.document.requirement",
        "compliance_id",
        string="Checklist de Documentos",
    )
    required_docs_count = fields.Integer(
        compute="_compute_required_docs_stats",
        string="Total Requeridos",
    )
    completed_docs_count = fields.Integer(
        compute="_compute_required_docs_stats",
        string="Completos",
    )
    pending_docs_count = fields.Integer(
        compute="_compute_required_docs_stats",
        string="Pendentes",
    )
    expired_docs_count = fields.Integer(
        compute="_compute_required_docs_stats",
        string="Vencidos",
    )

    # ============================================================
    # MÉTODOS COMPUTADOS
    # ============================================================

    @api.depends("folder_id", "partner_id")
    def _compute_documents(self):
        """Busca todos os documentos do cliente (por pasta + partner_id)."""
        if "documents.document" not in self.env:
            # Módulo documents não instalado
            for compliance in self:
                compliance.document_ids = False
                compliance.document_count = 0
            return

        for compliance in self:
            domain = []

            # Busca por pasta (hierárquica)
            if compliance.folder_id:
                domain.append(("folder_id", "child_of", compliance.folder_id.id))

            # OU busca por partner_id (direto)
            if compliance.partner_id:
                if domain:
                    domain = ["|"] + domain + [("partner_id", "=", compliance.partner_id.id)]
                else:
                    domain = [("partner_id", "=", compliance.partner_id.id)]

            if domain:
                docs = self.env["documents.document"].search(domain)
                compliance.document_ids = docs
                compliance.document_count = len(docs)
            else:
                compliance.document_ids = False
                compliance.document_count = 0

    @api.depends("partner_id")
    def _compute_sign_requests(self):
        """Busca solicitações de assinatura do cliente."""
        if "sign.request" not in self.env:
            # Módulo sign não instalado
            for compliance in self:
                compliance.sign_request_ids = False
                compliance.pending_signatures_count = 0
                compliance.signed_count = 0
            return

        for compliance in self:
            if compliance.partner_id:
                requests = self.env["sign.request"].search(
                    [("partner_id", "=", compliance.partner_id.id)]
                )
                compliance.sign_request_ids = requests
                compliance.pending_signatures_count = len(requests.filtered(lambda r: r.state == "sent"))
                compliance.signed_count = len(requests.filtered(lambda r: r.state == "signed"))
            else:
                compliance.sign_request_ids = False
                compliance.pending_signatures_count = 0
                compliance.signed_count = 0

    @api.depends("required_document_ids", "required_document_ids.is_complete")
    def _compute_required_docs_stats(self):
        """Calcula estatísticas do checklist de documentos."""
        for compliance in self:
            reqs = compliance.required_document_ids
            compliance.required_docs_count = len(reqs)
            compliance.completed_docs_count = len(reqs.filtered("is_complete"))
            compliance.pending_docs_count = len(reqs.filtered(lambda r: not r.is_complete))
            compliance.expired_docs_count = len(reqs.filtered("is_expired"))

    @api.depends(
        "required_document_ids",
        "required_document_ids.is_complete",
        "required_document_ids.category",
        "brokerage_ids",
        "profile_id.suitability_state",
    )
    def _compute_compliance_status(self):
        """Calcula status do checklist (4 itens principais)."""
        for compliance in self:
            reqs = compliance.required_document_ids

            # 1. Contrato assinado?
            contract_req = reqs.filtered(lambda r: r.category == "contract")
            compliance.contract_signed = any(contract_req.mapped("is_complete"))

            # 2. Suitability completo?
            compliance.suitability_completed = compliance.profile_id.suitability_state == "valid"

            # 3. Documentos pessoais completos?
            personal_categories = ["personal_id", "proof_residence", "certificate", "power_attorney"]
            personal_reqs = reqs.filtered(lambda r: r.category in personal_categories and r.is_required)
            if personal_reqs:
                compliance.personal_docs_complete = all(personal_reqs.mapped("is_complete"))
            else:
                compliance.personal_docs_complete = False

            # 4. Corretora selecionada?
            compliance.brokerage_selected = bool(compliance.brokerage_ids)

    @api.depends(
        "contract_signed",
        "suitability_completed",
        "personal_docs_complete",
        "brokerage_selected",
        "completed_docs_count",
        "required_docs_count",
    )
    def _compute_compliance_score(self):
        """Calcula score 0-100% baseado no checklist."""
        for compliance in self:
            score = 0

            # Checklist principal (60%)
            if compliance.contract_signed:
                score += 20
            if compliance.suitability_completed:
                score += 15
            if compliance.personal_docs_complete:
                score += 15
            if compliance.brokerage_selected:
                score += 10

            # Documentos adicionais (40%)
            if compliance.required_docs_count > 0:
                completion_rate = compliance.completed_docs_count / compliance.required_docs_count
                score += int(completion_rate * 40)

            compliance.compliance_score = min(score, 100)

    @api.depends(
        "compliance_score",
        "pending_signatures_count",
        "expired_docs_count",
    )
    def _compute_compliance_state(self):
        """Determina estado geral do compliance."""
        for compliance in self:
            if compliance.expired_docs_count > 0:
                compliance.compliance_state = "expired"
            elif compliance.pending_signatures_count > 0:
                compliance.compliance_state = "pending_signatures"
            elif compliance.compliance_score >= 95:
                compliance.compliance_state = "complete"
            elif compliance.compliance_score > 0:
                compliance.compliance_state = "in_progress"
            else:
                compliance.compliance_state = "draft"

    # ============================================================
    # AÇÕES DO USUÁRIO
    # ============================================================

    def action_create_client_folder(self):
        """Cria pasta automática em Documents para o cliente."""
        self.ensure_one()

        if "documents.folder" not in self.env:
            raise UserError(
                _("Módulo Documents não está instalado. "
                  "Esta funcionalidade requer Odoo Enterprise com Documents.")
            )

        # Busca ou cria workspace "Finance - Compliance"
        workspace = self.env["documents.folder"].search(
            [("name", "=", "Finance - Compliance"), ("parent_folder_id", "=", False)],
            limit=1,
        )

        if not workspace:
            workspace = self.env["documents.folder"].create(
                {
                    "name": "Finance - Compliance",
                    "description": "Documentos de compliance financeiro dos clientes",
                }
            )

        # Cria pasta do cliente
        client_folder = self.env["documents.folder"].create(
            {
                "name": self.partner_id.name,
                "parent_folder_id": workspace.id,
                "description": f"Compliance: {self.partner_id.name} (CPF/CNPJ: {self.partner_id.vat or 'N/A'})",
            }
        )

        # Cria subpastas organizacionais
        subfolders = [
            "01 - Contratos",
            "02 - Suitability",
            "03 - Documentos Pessoais",
            "04 - Assinaturas",
            "05 - Relatórios",
            "06 - Outros",
        ]

        for subfolder_name in subfolders:
            self.env["documents.folder"].create(
                {
                    "name": subfolder_name,
                    "parent_folder_id": client_folder.id,
                }
            )

        self.folder_id = client_folder

        # Registra no chatter
        self.message_post(
            body=_(
                "📁 <strong>Pasta criada em Documents</strong><br/>"
                "Workspace: Finance - Compliance<br/>"
                "Pasta: %s<br/>"
                "Subpastas: 6 criadas"
            )
            % self.partner_id.name
        )

        # Cria atividade para upload
        self.activity_schedule(
            "mail.mail_activity_data_todo",
            user_id=self.profile_id.advisor_id.id or self.env.user.id,
            summary="📤 Upload de Documentos de Compliance",
            note=_(
                "Pasta criada automaticamente em Documents para %s.<br/>"
                "Próximos passos:<br/>"
                "1. Fazer upload dos documentos necessários<br/>"
                "2. Enviar contrato para assinatura<br/>"
                "3. Completar suitability"
            )
            % self.partner_id.name,
        )

        return True

    def action_open_documents_folder(self):
        """Abre pasta do cliente em Documents."""
        self.ensure_one()

        if "documents.document" not in self.env:
            raise UserError(
                _("Módulo Documents não está instalado. "
                  "Esta funcionalidade requer Odoo Enterprise com Documents.")
            )

        if not self.folder_id:
            self.action_create_client_folder()

        return {
            "type": "ir.actions.act_window",
            "name": f"📁 Documentos: {self.partner_id.name}",
            "res_model": "documents.document",
            "view_mode": "kanban,list,form",
            "domain": [("folder_id", "child_of", self.folder_id.id)],
            "context": {
                "default_folder_id": self.folder_id.id,
                "default_partner_id": self.partner_id.id,
                "search_default_folder_id": self.folder_id.id,
            },
        }

    def action_send_contract_for_signature(self):
        """Envia contrato de consultoria para assinatura digital."""
        self.ensure_one()

        if "sign.request" not in self.env:
            raise UserError(
                _("Módulo Sign não está instalado. "
                  "Esta funcionalidade requer Odoo Enterprise com Sign.")
            )

        # Busca template de contrato
        template = self.env.ref(
            "finance_compliance.sign_template_consultancy_contract",
            raise_if_not_found=False,
        )

        if not template:
            raise UserError(
                _("Template de contrato não encontrado.\n"
                  "Crie um template em Sign com ID: sign_template_consultancy_contract")
            )

        # Cria solicitação de assinatura
        sign_request = self.env["sign.request"].create(
            {
                "template_id": template.id,
                "reference": f"Contrato Consultoria: {self.partner_id.name}",
                "partner_id": self.partner_id.id,
            }
        )

        # Adiciona signatários
        advisor_partner = self.profile_id.advisor_id.partner_id
        if not advisor_partner:
            advisor_partner = self.env.user.partner_id

        sign_request.write(
            {
                "request_item_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.partner_id.id,
                            "role_id": self.env.ref("sign.sign_item_role_customer").id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": advisor_partner.id,
                            "role_id": self.env.ref("sign.sign_item_role_employee").id,
                        },
                    ),
                ]
            }
        )

        # Envia email
        sign_request.action_sent()

        # Registra no chatter
        self.message_post(
            body=_(
                "📝 <strong>Contrato enviado para assinatura</strong><br/>"
                "Documento: Contrato de Consultoria Financeira<br/>"
                "Signatários:<br/>"
                "• Cliente: %s<br/>"
                "• Consultor: %s"
            )
            % (self.partner_id.name, advisor_partner.name)
        )

        return {
            "type": "ir.actions.act_window",
            "name": "Solicitação de Assinatura",
            "res_model": "sign.request",
            "res_id": sign_request.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_pending_signatures(self):
        """Abre lista de assinaturas pendentes."""
        self.ensure_one()

        if "sign.request" not in self.env:
            raise UserError(_("Módulo Sign não está instalado."))

        return {
            "type": "ir.actions.act_window",
            "name": f"⏳ Assinaturas Pendentes: {self.partner_id.name}",
            "res_model": "sign.request",
            "view_mode": "list,form",
            "domain": [
                ("partner_id", "=", self.partner_id.id),
                ("state", "=", "sent"),
            ],
            "context": {
                "default_partner_id": self.partner_id.id,
            },
        }

    def _create_default_requirements(self):
        """Cria checklist padrão de documentos requeridos."""
        self.ensure_one()

        default_requirements = [
            # Contratos
            {
                "sequence": 10,
                "name": "Contrato de Consultoria Financeira",
                "category": "contract",
                "is_required": True,
            },
            # Suitability
            {
                "sequence": 20,
                "name": "Formulário de Suitability Preenchido",
                "category": "suitability",
                "is_required": True,
            },
            # Documentos Pessoais
            {
                "sequence": 30,
                "name": "CNH ou RG (frente e verso)",
                "category": "personal_id",
                "is_required": True,
            },
            {
                "sequence": 40,
                "name": "Comprovante de Residência (até 90 dias)",
                "category": "proof_residence",
                "is_required": True,
            },
            {
                "sequence": 50,
                "name": "Certidão de Casamento (se aplicável)",
                "category": "certificate",
                "is_required": False,
            },
            {
                "sequence": 60,
                "name": "Procuração (se aplicável)",
                "category": "power_attorney",
                "is_required": False,
            },
            # Corretora
            {
                "sequence": 70,
                "name": "Termo de Adesão - Corretora",
                "category": "brokerage",
                "is_required": True,
            },
        ]

        for req_vals in default_requirements:
            req_vals["compliance_id"] = self.id
            self.env["finance.compliance.document.requirement"].create(req_vals)

        return True

    @api.model
    def create(self, vals):
        compliance = super().create(vals)

        # Cria pasta automática se módulo documents estiver instalado
        if "documents.folder" in self.env:
            try:
                compliance.action_create_client_folder()
            except Exception as e:
                # Não bloqueia criação se falhar
                compliance.message_post(
                    body=_("⚠️ Erro ao criar pasta em Documents: %s") % str(e)
                )

        # Cria checklist padrão
        compliance._create_default_requirements()

        return compliance


class FinanceComplianceDocumentRequirement(models.Model):
    _name = "finance.compliance.document.requirement"
    _description = "Documento Requerido para Compliance"
    _order = "sequence, name"

    compliance_id = fields.Many2one(
        "finance.compliance",
        required=True,
        ondelete="cascade",
        string="Compliance",
    )
    sequence = fields.Integer(default=10, string="Sequência")
    name = fields.Char(required=True, string="Documento")
    category = fields.Selection(
        [
            ("contract", "Contrato"),
            ("suitability", "Suitability"),
            ("personal_id", "Documento de Identidade"),
            ("proof_residence", "Comprovante de Residência"),
            ("certificate", "Certidão"),
            ("power_attorney", "Procuração"),
            ("brokerage", "Corretora"),
            ("other", "Outro"),
        ],
        required=True,
        string="Categoria",
    )
    is_required = fields.Boolean(default=True, string="Obrigatório")
    is_complete = fields.Boolean(
        compute="_compute_is_complete",
        store=True,
        string="Completo",
    )
    document_id = fields.Many2one(
        "documents.document",
        string="Documento Anexado",
        help="Link para documento em Documents (opcional se módulo não instalado)",
    )
    sign_request_id = fields.Many2one(
        "sign.request",
        string="Assinatura Digital",
        help="Link para solicitação de assinatura (opcional se módulo não instalado)",
    )
    expiration_date = fields.Date(string="Vencimento")
    is_expired = fields.Boolean(
        compute="_compute_is_expired",
        store=True,
        string="Vencido",
    )
    notes = fields.Text(string="Observações")

    @api.depends("document_id", "sign_request_id", "category")
    def _compute_is_complete(self):
        """Verifica se documento está completo (assinado ou anexado)."""
        for req in self:
            if req.category == "contract":
                # Contrato precisa estar assinado
                req.is_complete = bool(req.sign_request_id and req.sign_request_id.state == "signed")
            else:
                # Outros: basta estar anexado OU assinado
                req.is_complete = bool(req.document_id) or bool(
                    req.sign_request_id and req.sign_request_id.state == "signed"
                )

    @api.depends("expiration_date")
    def _compute_is_expired(self):
        """Verifica se documento está vencido."""
        today = fields.Date.today()
        for req in self:
            req.is_expired = bool(req.expiration_date and req.expiration_date < today)


class FinanceBrokerage(models.Model):
    _name = "finance.brokerage"
    _description = "Corretora de Valores"
    _order = "name"

    name = fields.Char(required=True, string="Nome da Corretora")
    code = fields.Char(string="Código", help="Ex: CLEAR, XP, BTG")
    website = fields.Char(string="Website")
    logo = fields.Binary(string="Logo")
    active = fields.Boolean(default=True, string="Ativa")
    notes = fields.Text(string="Observações")
