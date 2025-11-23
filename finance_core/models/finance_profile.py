# -*- coding: utf-8 -*-
import base64
import json
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class FinanceProfile(models.Model):
    _name = "finance.profile"
    _description = "Perfil financeiro do cliente"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "display_name"
    
    # ============================================================
    # CONSTRAINT SQL: Previne duplicatas por partner
    # ============================================================
    _sql_constraints = [
        (
            'unique_partner_profile',
            'UNIQUE(partner_id)',
            '⚠️ Já existe um Perfil Financeiro para este Cliente! '
            'Um cliente pode ter apenas um perfil ativo.'
        ),
    ]

    partner_id = fields.Many2one(
        "res.partner",
        string="Cliente",
        required=True,
        ondelete="cascade",
        index=True,
        tracking=True,
    )
    partner_function = fields.Char(
        related="partner_id.function",
        string="Cargo",
        readonly=True,
        store=True,
    )
    active = fields.Boolean(
        string="Ativo",
        default=True,
        tracking=True,
        help="Desmarque para desativar o perfil (modo congelado). Apenas administradores podem alterar.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Empresa",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    display_name = fields.Char(compute="_compute_display_name", store=True)
    advisor_id = fields.Many2one(
        "res.users",
        string="Consultor responsável",
        tracking=True,
        default=lambda self: self.env.user,
    )
    
    # ============================================================
    # INTEGRAÇÃO COM CRM
    # ============================================================
    crm_lead_id = fields.Many2one(
        'crm.lead',
        string='Oportunidade CRM',
        tracking=True,
        ondelete='set null',
        help='Lead/Oportunidade no CRM que originou este perfil financeiro.'
    )
    last_sync_date = fields.Datetime(
        string='Última Sincronização CRM',
        readonly=True,
        tracking=True,
        help='Data e hora da última sincronização automática com CRM Lead'
    )
    investor_type = fields.Selection(
        [
            ("pf", "Pessoa Física"),
            ("pj", "Pessoa Jurídica"),
        ],
        string="Tipo de cliente",
        required=True,
        default="pf",
        tracking=True,
    )
    suitability_score = fields.Integer(
        string="Pontuação suitability",
        tracking=True,
        help="Score de 0 a 100 baseado no questionário de suitability. Determina o perfil de risco do cliente.",
    )
    suitability_profile = fields.Selection(
        [
            ("conservative", "Conservador"),
            ("moderate", "Moderado"),
            ("bold", "Arrojado"),
        ],
        string="Perfil de risco",
        tracking=True,
    )
    suitability_last_review = fields.Date(string="Última revisão de suitability", tracking=True)
    suitability_next_review = fields.Date(
        string="Próxima revisão de suitability",
        compute="_compute_suitability_next_review",
        store=True,
    )
    suitability_state = fields.Selection(
        [
            ("draft", "Em análise"),
            ("valid", "Válido"),
            ("expiring", "Próximo do vencimento"),
            ("expired", "Expirado"),
        ],
        compute="_compute_suitability_state",
        store=True,
        string="Status suitability",
    )
    compliance_status = fields.Selection(
        [
            ("clean", "Em conformidade"),
            ("pending", "Pendências"),
            ("restricted", "Restrito"),
        ],
        string="Status de compliance",
        default="clean",
        tracking=True,
    )
    annual_income = fields.Monetary(string="Renda anual", currency_field="currency_id", tracking=True)
    net_worth = fields.Monetary(string="Patrimônio líquido", currency_field="currency_id", tracking=True)
    emergency_fund_months = fields.Float(
        string="Meses de reserva",
        tracking=True,
        help="Número de meses de despesas cobertas pela reserva de emergência. Recomenda-se entre 6 e 12 meses.",
    )
    saving_capacity = fields.Monetary(string="Capacidade de poupança mensal", currency_field="currency_id", tracking=True)
    household_notes = fields.Text(string="Notas pessoais")
    risk_warnings = fields.Text(string="Alertas de risco")
    objective_summary = fields.Text(string="Resumo dos objetivos do cliente")
    last_meeting_id = fields.Many2one("calendar.event", string="Última reunião")
    next_meeting_id = fields.Many2one("calendar.event", string="Próxima reunião")
    event_count = fields.Integer(
        string="Total de reuniões",
        compute="_compute_event_count",
        store=False,
        help="Total de reuniões agendadas com este cliente"
    )
    days_since_last_meeting = fields.Integer(
        string="Dias desde última reunião",
        compute="_compute_days_since_last_meeting",
        store=False,
        help="Número de dias desde a última reunião realizada"
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Moeda",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    advisory_alert_ids = fields.One2many("finance.alert", "profile_id", string="Alertas inteligentes")
    advisory_score = fields.Float(
        string="Score financeiro",
        compute="_compute_advisory_score",
        store=True,
        help="Score automático de 0 a 100 baseado em renda, capacidade de poupança, reserva de emergência, suitability e compliance. Quanto maior, melhor a saúde financeira.",
    )
    cashflow_balance = fields.Monetary(
        string="Balanço de fluxo de caixa",
        currency_field="currency_id",
        compute="_compute_financial_snapshots",
        store=True,
    )
    goals_progress = fields.Float(
        string="Progresso médio das metas",
        compute="_compute_financial_snapshots",
        store=True,
        aggregator="avg",
        default=0.0,
    )
    goals_progress_percentage = fields.Float(
        string="Progresso médio das metas (%)",
        compute="_compute_goals_progress_percentage",
        store=True,
        default=0.0,
    )
    portfolio_value = fields.Monetary(
        string="AUM consolidado",
        currency_field="currency_id",
        compute="_compute_financial_snapshots",
        store=True,
    )
    pending_documents = fields.Integer(
        string="Documentos pendentes",
        compute="_compute_pending_documents",
        store=True,
        help="Número total de alertas de documentos abertos + documentos expirados que necessitam ação.",
    )
    privacy_deletion_requested = fields.Boolean(
        string="Exclusão solicitada",
        tracking=True,
    )
    privacy_requested_date = fields.Date(
        string="Data da solicitação",
        tracking=True,
    )

    # ============================================================
    # DADOS PESSOAIS (Relacionamento - integrado do CRM Wealth)
    # ============================================================
    client_birthdate = fields.Date(
        string="Aniversário do Cliente",
        help="Data de aniversário do cliente para envio de mensagens personalizadas"
    )
    marital_status = fields.Selection([
        ('single', 'Solteiro(a)'),
        ('married', 'Casado(a)'),
        ('divorced', 'Divorciado(a)'),
        ('widowed', 'Viúvo(a)')
    ], string="Estado Civil")
    spouse_name = fields.Char(string="Nome do(a) Cônjuge")
    spouse_birthdate = fields.Date(
        string="Aniversário do(a) Cônjuge",
        help="Data de aniversário do cônjuge"
    )
    children_count = fields.Integer(string="Quantidade de Filhos", default=0)
    children_names = fields.Text(
        string="Nomes e Idades dos Filhos",
        help="Ex: João (5 anos), Maria (8 anos)"
    )
    favorite_team = fields.Char(
        string="Time do Coração",
        help="Informação para conexão emocional com cliente"
    )
    hobbies = fields.Text(
        string="Hobbies/Interesses",
        help="Ex: Golfe, Viagens, Culinária"
    )
    
    # ============================================================
    # OBJETIVOS FINANCEIROS (Resumo Inicial)
    # ============================================================
    short_term_goal = fields.Text(
        string="Objetivo Curto Prazo (12 meses)",
        help="Objetivos a serem alcançados nos próximos 12 meses"
    )
    long_term_goal = fields.Text(
        string="Objetivo Longo Prazo (5+ anos)",
        help="Objetivos de médio e longo prazo (5 anos ou mais)"
    )
    main_goal = fields.Selection([
        ('retirement', 'Aposentadoria'),
        ('fire', 'FIRE (Independência Financeira)'),
        ('property', 'Compra de Imóvel'),
        ('education', 'Educação dos Filhos'),
        ('travel', 'Viagens'),
        ('business', 'Abrir Negócio'),
        ('legacy', 'Deixar Legado'),
        ('other', 'Outro')
    ], string="Objetivo Principal", tracking=True)
    goal_amount = fields.Monetary(
        string="Valor do Objetivo",
        currency_field='currency_id',
        help="Valor monetário do objetivo principal"
    )
    goal_deadline_years = fields.Integer(
        string="Prazo (anos)",
        help="Prazo em anos para atingir o objetivo"
    )
    monthly_contribution_needed = fields.Monetary(
        string="Aporte Mensal Necessário",
        compute='_compute_monthly_contribution',
        store=True,
        currency_field='currency_id',
        help="Cálculo automático usando fórmula PMT (Payment)"
    )
    
    # ============================================================
    # DIAGNÓSTICO FINANCEIRO (SWOT Inicial)
    # ============================================================
    diagnosis_current_situation = fields.Text(
        string="Situação Atual",
        help="Descrição da situação financeira atual do cliente"
    )
    diagnosis_strengths = fields.Text(
        string="Pontos Fortes",
        help="Pontos fortes identificados na situação financeira"
    )
    diagnosis_weaknesses = fields.Text(
        string="Pontos a Melhorar",
        help="Pontos fracos ou áreas de melhoria"
    )
    diagnosis_opportunities = fields.Text(
        string="Oportunidades",
        help="Oportunidades identificadas para o cliente"
    )
    diagnosis_date = fields.Date(
        string="Data do Diagnóstico",
        help="Data em que o diagnóstico foi realizado"
    )
    
    # ============================================================
    # PROPOSTA COMERCIAL
    # ============================================================
    contract_plan = fields.Selection([
        ('monthly', 'Mensal'),
        ('fire', 'FIRE'),
        ('premium', 'Premium'),
        ('wealth', 'Gestão de Patrimônio'),
        ('mentoring', 'Mentoria'),
        ('custom', 'Personalizado')
    ], string="Plano Contratado", tracking=True)
    proposal_amount = fields.Monetary(
        string="Valor da Proposta",
        currency_field='currency_id',
        tracking=True,
        help="Valor mensal ou valor base da proposta"
    )
    management_fee = fields.Float(
        string="Fee de Gestão (%)",
        help="Percentual anual sobre AUM (Assets Under Management)",
        tracking=True
    )
    contract_type = fields.Selection([
        ('monthly', 'Mensalidade Fixa'),
        ('quarterly', 'Trimestral'),
        ('aum_percentage', '% sobre AUM')
    ], string="Tipo de Contrato", tracking=True)
    estimated_annual_revenue = fields.Monetary(
        string="Receita Anual Estimada",
        compute='_compute_estimated_revenue',
        store=True,
        currency_field='currency_id',
        help="Receita anual estimada baseada no contrato"
    )
    proposal_justification = fields.Text(
        string="Justificativa da Proposta",
        help="Justificativa do valor proposto"
    )
    proposal_date = fields.Date(
        string="Data da Proposta",
        tracking=True
    )
    proposal_objections_ids = fields.Many2many(
        'finance.objection.tag',
        string='Objeções Apresentadas',
        help='Objeções e resistências apresentadas pelo cliente: Preço, Tempo, Medo, Complexidade, Confiança'
    )
    
    # ============================================================
    # QUALIFICAÇÃO INICIAL
    # ============================================================
    financial_readiness = fields.Selection([
        ('organizing', '📋 Organizando finanças'),
        ('starting', '🚀 Iniciando investimentos'),
        ('planning', '🎯 Planejando crescimento'),
        ('optimizing', '⚡ Otimizando patrimônio')
    ], string='Momento Financeiro', help='Estágio atual do cliente em sua jornada financeira')
    
    primary_pain_point = fields.Selection([
        ('time', '⏰ Falta de tempo'),
        ('strategy', '🎯 Falta de estratégia'),
        ('fear', '😰 Medo de perder dinheiro'),
        ('organization', '📊 Desorganização financeira'),
        ('knowledge', '📚 Falta de conhecimento'),
        ('discipline', '💪 Falta de disciplina')
    ], string='Dor Principal', help='Principal desafio ou dor do cliente')
    
    investor_interests_ids = fields.Many2many(
        'finance.interest.tag',
        string='Interesses do Investidor',
        help='Tipos de investimentos de interesse do cliente'
    )
    
    # ============================================================
    # REUNIÃO ESTRATÉGICA (substituindo aba Reuniões simples)
    # ============================================================
    meeting_date = fields.Date(
        string='Data da Reunião',
        tracking=True,
        help='Data da reunião estratégica com o cliente'
    )
    meeting_strategies_discussed = fields.Text(
        string='Estratégias Discutidas',
        help='Resumo das estratégias discutidas na reunião'
    )
    meeting_objections = fields.Text(
        string='Objeções Identificadas',
        help='Principais objeções ou dúvidas levantadas pelo cliente'
    )
    recommended_strategies_ids = fields.Many2many(
        'finance.strategy.tag',
        string='Estratégias Recomendadas',
        help='Estratégias de investimento recomendadas: Renda Fixa, Tesouro, FIIs, ETFs, Previdência, Proteção'
    )
    potential_score = fields.Selection([
        ('0', '⭐ 0 estrelas'),
        ('1', '⭐ 1 estrela'),
        ('2', '⭐⭐ 2 estrelas'),
        ('3', '⭐⭐⭐ 3 estrelas'),
        ('4', '⭐⭐⭐⭐ 4 estrelas'),
        ('5', '⭐⭐⭐⭐⭐ 5 estrelas'),
    ], string='Score de Potencial', tracking=True, help='Avaliação do potencial do cliente (0-5 estrelas)')
    


    _constraints = [
        models.Constraint(
            "unique(partner_id)",
            "Cada cliente só pode ter um perfil financeiro.",
        ),
    ]

    def name_get(self):
        return [(profile.id, profile.display_name) for profile in self]

    @api.depends("partner_id", "partner_id.name")
    def _compute_display_name(self):
        for profile in self:
            partner_name = profile.partner_id.name or _("Sem nome")
            company_name = profile.company_id.name if profile.company_id else False
            profile.display_name = (
                "%s · %s" % (partner_name, company_name)
                if company_name
                else "%s · Perfil financeiro" % partner_name
            )

    @api.constrains("partner_id", "company_id")
    def _check_company_alignment(self):
        for profile in self:
            if profile.partner_id.company_id and profile.partner_id.company_id != profile.company_id:
                raise ValidationError(
                    _(
                        "O contato pertence à empresa %(partner_company)s. Atualize a empresa do perfil para manter consistência.",
                        partner_company=profile.partner_id.company_id.display_name,
                    )
                )

    @api.constrains("suitability_score")
    def _check_suitability_score_range(self):
        """Valida que o score de suitability está entre 0 e 100"""
        for profile in self:
            if profile.suitability_score and not (0 <= profile.suitability_score <= 100):
                raise ValidationError(_("O score de suitability deve estar entre 0 e 100."))

    @api.constrains("emergency_fund_months")
    def _check_emergency_fund_positive(self):
        """Valida que os meses de reserva não são negativos"""
        for profile in self:
            if profile.emergency_fund_months and profile.emergency_fund_months < 0:
                raise ValidationError(_("Os meses de reserva de emergência não podem ser negativos."))

    @api.constrains("annual_income", "net_worth", "saving_capacity")
    def _check_monetary_fields_positive(self):
        """Valida que valores monetários não são negativos"""
        for profile in self:
            if profile.annual_income and profile.annual_income < 0:
                raise ValidationError(_("A renda anual não pode ser negativa."))
            if profile.net_worth and profile.net_worth < 0:
                raise ValidationError(_("O patrimônio líquido não pode ser negativo."))
            if profile.saving_capacity and profile.saving_capacity < 0:
                raise ValidationError(_("A capacidade de poupança não pode ser negativa."))

    @api.depends("suitability_last_review")
    def _compute_suitability_next_review(self):
        for profile in self:
            if profile.suitability_last_review:
                profile.suitability_next_review = profile.suitability_last_review.replace(
                    year=profile.suitability_last_review.year + 1
                )
            else:
                profile.suitability_next_review = False

    @api.depends("suitability_last_review", "suitability_next_review")
    def _compute_suitability_state(self):
        today = date.today()
        for profile in self:
            if not profile.suitability_last_review:
                profile.suitability_state = "draft"
                continue
            if profile.suitability_next_review and profile.suitability_next_review < today:
                profile.suitability_state = "expired"
            elif profile.suitability_next_review and (
                profile.suitability_next_review - today
            ).days <= 30:
                profile.suitability_state = "expiring"
            else:
                profile.suitability_state = "valid"

    @api.depends(
        "annual_income",
        "saving_capacity",
        "emergency_fund_months",
        "suitability_state",
        "compliance_status",
    )
    def _compute_advisory_score(self):
        for profile in self:
            score = 0.0
            if profile.annual_income:
                score += min(profile.annual_income / 100000.0, 1.0) * 25
            if profile.saving_capacity:
                score += min(profile.saving_capacity / 5000.0, 1.0) * 25
            if profile.emergency_fund_months:
                score += min(profile.emergency_fund_months / 6.0, 1.0) * 15
            if profile.suitability_state == "valid":
                score += 15
            elif profile.suitability_state == "expiring":
                score += 5
            if profile.compliance_status == "clean":
                score += 20
            elif profile.compliance_status == "pending":
                score += 10
            profile.advisory_score = round(score, 2)

    @api.depends("partner_id")
    def _compute_financial_snapshots(self):
        for profile in self:
            goals_progress = 0.0
            goal_count = 0
            cashflow_balance = 0.0
            aum_total = 0.0
            if hasattr(profile, "goal_ids"):
                goals = profile.goal_ids.filtered(lambda g: g.state != "archived")
                if goals:
                    goal_progress_total = sum(goal.progress_ratio for goal in goals)
                    goals_progress = goal_progress_total / len(goals)
                    goal_count = len(goals)
            if hasattr(profile, "cashflow_plan_ids"):
                latest_plan = profile.cashflow_plan_ids[:1]
                if latest_plan:
                    cashflow_balance = latest_plan.monthly_surplus
            if hasattr(profile, "portfolio_snapshot_ids"):
                latest_snapshot = profile.portfolio_snapshot_ids[:1]
                if latest_snapshot:
                    aum_total = latest_snapshot.market_value
            normalized_progress = goals_progress if goal_count else 0.0
            profile.goals_progress = normalized_progress
            profile.cashflow_balance = cashflow_balance
            profile.portfolio_value = aum_total

    @api.depends("goals_progress")
    def _compute_goals_progress_percentage(self):
        for profile in self:
            profile.goals_progress_percentage = round(profile.goals_progress * 100.0, 2)


    @api.depends('goal_amount', 'goal_deadline_years')
    def _compute_monthly_contribution(self):
        """Calcula aporte mensal necessário usando fórmula PMT (Payment)"""
        for profile in self:
            if not profile.goal_amount or not profile.goal_deadline_years or profile.goal_deadline_years <= 0:
                profile.monthly_contribution_needed = 0.0
                continue
            
            # Taxa de retorno anual padrão (configurável via parâmetros do sistema)
            taxa_anual = float(
                self.env['ir.config_parameter'].sudo()
                .get_param('finance_core.default_return_rate', default=10.0)
            )
            
            # Conversão para taxa mensal composta
            taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
            n_meses = profile.goal_deadline_years * 12
            
            # Fórmula PMT: FV / [((1 + i)^n - 1) / i]
            # FV = Valor Futuro (goal_amount)
            # i = taxa mensal
            # n = número de meses
            if taxa_mensal > 0:
                denominador = ((1 + taxa_mensal) ** n_meses - 1) / taxa_mensal
                profile.monthly_contribution_needed = profile.goal_amount / denominador if denominador else 0.0
            else:
                # Se taxa = 0, divisão simples
                profile.monthly_contribution_needed = profile.goal_amount / n_meses if n_meses else 0.0
    
    @api.depends('proposal_amount', 'management_fee', 'portfolio_value', 'contract_type')
    def _compute_estimated_revenue(self):
        """Calcula receita anual estimada baseada no tipo de contrato"""
        for profile in self:
            if profile.contract_type == 'aum_percentage' and profile.management_fee > 0 and profile.portfolio_value > 0:
                # Percentual sobre AUM (Assets Under Management)
                profile.estimated_annual_revenue = (
                    profile.portfolio_value * profile.management_fee / 100
                )
            elif profile.proposal_amount > 0:
                if profile.contract_type == 'quarterly':
                    # Trimestral: proposta × 4
                    profile.estimated_annual_revenue = profile.proposal_amount * 4
                else:
                    # Mensal: proposta × 12
                    profile.estimated_annual_revenue = profile.proposal_amount * 12
            else:
                profile.estimated_annual_revenue = 0.0

    @api.depends("advisory_alert_ids", "advisory_alert_ids.state")
    def _compute_pending_documents(self):
        for profile in self:
            alert_count = len(
                profile.advisory_alert_ids.filtered(lambda alert: alert.category == "document" and alert.state != "done")
            )
            document_count = 0
            if "finance.document" in self.env:
                document_count = self.env["finance.document"].search_count(
                    [
                        ("profile_id", "=", profile.id),
                        ("is_expired", "=", True),
                    ]
                )
            profile.pending_documents = alert_count + document_count

    @api.constrains("suitability_state", "compliance_status")
    def _check_compliance_alignment(self):
        for profile in self:
            if profile.suitability_state == "expired" and profile.compliance_status == "clean":
                raise ValidationError(
                    _("Atualize o status de compliance quando a suitability estiver expirada para manter consistência.")
                )

    def action_open_partner(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "res_id": self.partner_id.id,
        }

    def action_refresh_alerts(self):
        self.ensure_one()
        self._generate_smart_alerts()
        return True

    def action_open_alerts(self):
        self.ensure_one()
        action = self.env.ref("finance_core.action_finance_alerts").read()[0]
        action['domain'] = [('profile_id', '=', self.id)]
        context = action.get('context') or {}
        context = safe_eval(context) if isinstance(context, str) else dict(context)
        context.update(
            {
                'default_profile_id': self.id,
                'search_default_profile_id': self.id,
            }
        )
        action['context'] = context
        return action

    def _generate_smart_alerts(self):
        today = date.today()
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for profile in self:
            alerts_to_create = []
            if profile.suitability_state in {"expiring", "expired"}:
                alerts_to_create.append(
                    {
                        "name": _(
                            "Suitability a vencer"
                            if profile.suitability_state == "expiring"
                            else "Suitability vencida"
                        ),
                        "category": "compliance",
                        "description": _(
                            "Revise a suitability de %(client)s. A última revisão foi em %(date)s.",
                            client=profile.partner_id.name,
                            date=profile.suitability_last_review,
                        ),
                    }
                )
            if hasattr(profile, "goal_ids"):
                delayed_goals = profile.goal_ids.filtered(lambda g: g.is_late)
                for goal in delayed_goals:
                    alerts_to_create.append(
                        {
                            "name": _("Meta em atraso: %(goal)s", goal=goal.name),
                            "category": "goal",
                            "description": goal.alert_message,
                        }
                    )
            if hasattr(profile, "portfolio_snapshot_ids"):
                deviations = profile.portfolio_snapshot_ids[:1].mapped("allocation_warning")
                if deviations:
                    alerts_to_create.append(
                        {
                            "name": _("Carteira fora do alvo"),
                            "category": "portfolio",
                            "description": deviations[0],
                        }
                    )
            existing_alerts = {alert.name for alert in profile.advisory_alert_ids if alert.state != "done"}
            for alert_vals in alerts_to_create:
                if alert_vals["name"] in existing_alerts:
                    continue
                alert_vals.update({"profile_id": profile.id, "trigger_date": today})
                alert = self.env["finance.alert"].create(alert_vals)
                if activity_type:
                    has_activity = self.env["mail.activity"].search_count(
                        [
                            ("res_id", "=", profile.id),
                            ("res_model", "=", profile._name),
                            ("note", "=", alert.description or alert.name),
                            ("activity_type_id", "=", activity_type.id),
                        ]
                    )
                    if not has_activity:
                        self.env["mail.activity"].create(
                            {
                                "res_model_id": self.env["ir.model"]._get_id(profile._name),
                                "res_id": profile.id,
                                "activity_type_id": activity_type.id,
                                "summary": alert.name,
                                "note": alert.description or alert.name,
                                "user_id": profile.advisor_id.id or self.env.user.id,
                                "date_deadline": today,
                            }
                        )

    def action_open_onboarding_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "finance.onboarding.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_advisor_id": self.advisor_id.id,
                "default_investor_type": self.investor_type,
            },
        }

    def action_open_goal_wizard(self):
        self.ensure_one()
        if "finance.goal.wizard" not in self.env:
            raise UserError(_("Instale o módulo de planejamento financeiro para criar metas guiadas."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "finance.goal.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_profile_id": self.id},
        }

    def action_open_review_wizard(self):
        self.ensure_one()
        if "finance.review.wizard" not in self.env:
            raise UserError(_("Instale o módulo de investimentos para executar a revisão trimestral."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "finance.review.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_profile_id": self.id},
        }

    def action_open_recommendation_wizard(self):
        self.ensure_one()
        if "finance.recommendation.wizard" not in self.env:
            raise UserError(_("Instale o módulo de compliance para emitir recomendações guiadas."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "finance.recommendation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_profile_id": self.id},
        }

    @api.depends('partner_id')
    def _compute_event_count(self):
        """Conta total de reuniões do cliente."""
        for profile in self:
            if 'calendar.event' in self.env and profile.partner_id:
                profile.event_count = self.env['calendar.event'].search_count([
                    ('partner_ids', 'in', profile.partner_id.ids)
                ])
            else:
                profile.event_count = 0

    @api.depends('last_meeting_id', 'last_meeting_id.start')
    def _compute_days_since_last_meeting(self):
        """Calcula dias desde a última reunião."""
        today = fields.Date.today()
        for profile in self:
            if profile.last_meeting_id and profile.last_meeting_id.start:
                meeting_date = fields.Date.to_date(profile.last_meeting_id.start)
                profile.days_since_last_meeting = (today - meeting_date).days
            else:
                profile.days_since_last_meeting = 0

    def action_schedule_review(self):
        self.ensure_one()
        if "calendar.event" not in self.env:
            raise UserError(_("Instale a integração de calendário para agendar revisões."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_name": _("Revisão financeira"),
                "default_finance_profile_id": self.id,
                "default_partner_ids": [(4, self.partner_id.id)] if self.partner_id else [],
            },
        }

    def _cron_update_meeting_references(self):
        """CRON: Atualiza automaticamente last_meeting_id e next_meeting_id de todos os perfis."""
        if 'calendar.event' not in self.env:
            return
        
        profiles = self.search([])
        today = fields.Datetime.now()
        
        for profile in profiles:
            if not profile.partner_id:
                continue
            
            # Última reunião (mais recente no passado)
            last_event = self.env['calendar.event'].search([
                ('partner_ids', 'in', profile.partner_id.ids),
                ('start', '<=', today),
            ], order='start desc', limit=1)
            
            # Próxima reunião (mais próxima no futuro)
            next_event = self.env['calendar.event'].search([
                ('partner_ids', 'in', profile.partner_id.ids),
                ('start', '>', today),
            ], order='start asc', limit=1)
            
            profile.write({
                'last_meeting_id': last_event.id if last_event else False,
                'next_meeting_id': next_event.id if next_event else False,
            })

    def action_open_dashboard(self):
        self.ensure_one()
        action = self.env.ref("finance_core.action_finance_profile_dashboard").read()[0]
        context = action.get('context') or {}
        context = safe_eval(context) if isinstance(context, str) else dict(context)
        context.update({'finance_profile_id': self.id})
        action['context'] = context
        return action

    def action_export_personal_data(self):
        self.ensure_one()
        goal_data = []
        if "finance.goal" in self.env and hasattr(self, "goal_ids"):
            goal_data = self.goal_ids.read()
        portfolio_data = []
        if "finance.portfolio" in self.env and hasattr(self, "portfolio_ids"):
            portfolio_data = self.portfolio_ids.read()
        document_data = []
        if "finance.document" in self.env:
            document_data = self.env["finance.document"].search_read([("profile_id", "=", self.id)])
        data = {
            "profile": self.read()[0],
            "partner": self.partner_id.read()[0],
            "goals": goal_data,
            "portfolios": portfolio_data,
            "documents": document_data,
        }
        payload = json.dumps(data, default=str, ensure_ascii=False, indent=2)
        attachment = self.env["ir.attachment"].create(
            {
                "name": "export_%s.json" % self.partner_id.id,
                "datas": base64.b64encode(payload.encode("utf-8")),
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/json",
            }
        )
        self.message_post(body=_("Exportação de dados pessoais gerada."), attachment_ids=[attachment.id])
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }

    def action_request_data_deletion(self):
        self.ensure_one()
        self.write(
            {
                "privacy_deletion_requested": True,
                "privacy_requested_date": fields.Date.context_today(self),
            }
        )
        self.message_post(body=_("Solicitação de exclusão registrada conforme LGPD."))
        return True

    def action_anonymize_partner(self):
        self.ensure_one()
        partner = self.partner_id
        anonymized_vals = {
            "name": _("Cliente Anonimizado %s") % self.id,
            "email": False,
            "phone": False,
            "mobile": False,
            "street": False,
            "street2": False,
            "zip": False,
            "city": False,
            "state_id": False,
            "vat": False,
            "website": False,
        }
        partner.write(anonymized_vals)
        self.write(
            {
                "household_notes": False,
                "objective_summary": False,
            }
        )
        self.message_post(body=_("Dados pessoais foram anonimizados mediante solicitação."))
        return True
    
    def action_toggle_active(self):
        """Desativa/Ativa o perfil (somente admin)."""
        self.ensure_one()
        
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Apenas administradores podem desativar/ativar perfis financeiros."))
        
        new_state = not self.active
        self.active = new_state
        
        if new_state:
            self.message_post(
                body=_("✅ <strong>Perfil Reativado</strong><br/>O perfil foi reativado pelo administrador %s.") % self.env.user.name
            )
        else:
            self.message_post(
                body=_("🔒 <strong>Perfil Desativado</strong><br/>O perfil foi congelado (modo leitura) pelo administrador %s.<br/>Todas as operações estão bloqueadas até reativação.") % self.env.user.name
            )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_secure_delete(self):
        """Abre wizard de confirmação de exclusão com senha."""
        self.ensure_one()
        
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Apenas administradores podem excluir perfis financeiros."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('⚠️ Confirmar Exclusão Permanente'),
            'res_model': 'finance.profile.delete.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_profile_id': self.id,
                'default_profile_name': self.display_name,
            }
        }
    
    # ============================================================
    # MÉTODO HELPER: Busca ou Cria Profile (Anti-duplicação)
    # ============================================================
    @api.model
    def get_or_create_for_partner(self, partner_id, vals=None):
        """
        Busca Profile existente para Partner ou cria novo (anti-duplicação).
        
        **Args:**
            partner_id (int): ID do res.partner
            vals (dict): Valores adicionais para criar/atualizar
        
        **Returns:**
            finance.profile: Profile existente ou recém-criado
        
        **Comportamento:**
            - Se Profile existe → retorna existente + atualiza campos vazios
            - Se Profile NÃO existe → cria novo com vals
            - **NUNCA cria duplicatas** (garantido por constraint SQL)
        
        **Uso:**
            profile = env['finance.profile'].get_or_create_for_partner(
                partner_id=123,
                vals={'advisor_id': 5, 'investor_type': 'pf'}
            )
        """
        if not partner_id:
            raise UserError(_("Partner ID é obrigatório para criar Finance Profile"))
        
        # Busca profile existente
        profile = self.search([('partner_id', '=', partner_id)], limit=1)
        
        if profile:
            # ✅ Profile existe → atualiza apenas campos vazios
            if vals:
                update_vals = {}
                for field, value in vals.items():
                    if field == 'partner_id':
                        continue  # Nunca atualiza partner_id
                    if not profile[field]:  # Só atualiza se campo vazio
                        update_vals[field] = value
                
                if update_vals:
                    profile.write(update_vals)
            
            return profile
        else:
            # ✅ Profile NÃO existe → cria novo
            create_vals = vals or {}
            create_vals['partner_id'] = partner_id
            
            # Validação: Partner deve ser cliente
            partner = self.env['res.partner'].browse(partner_id)
            if not partner.customer_rank > 0:
                raise UserError(_(
                    "Apenas Clientes podem ter Finance Profile.\n"
                    "O Partner '%s' não está marcado como Cliente."
                ) % partner.name)
            
            return self.create(create_vals)


class ResPartner(models.Model):
    _inherit = "res.partner"

    finance_profile_id = fields.One2many(
        "finance.profile",
        "partner_id",
        string="Perfil financeiro",
    )

    def action_open_finance_profile(self):
        self.ensure_one()
        profile = self.finance_profile_id[:1]
        action = {
            "type": "ir.actions.act_window",
            "res_model": "finance.profile",
            "view_mode": "form",
            "target": "current",
        }
        if profile:
            action.update({"res_id": profile.id})
        else:
            action.update({"context": {"default_partner_id": self.id}})
        return action
