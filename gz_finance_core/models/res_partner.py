# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # ================================
    # SQL CONSTRAINTS
    # ================================
    _sql_constraints = [
        ('finance_profile_id_unique',
         'UNIQUE(finance_profile_id)',
         'O Finance Profile ID deve ser único! Este ID já está em uso.')
    ]
    
    # ================================
    # FIELDS - Financial Identification
    # ================================
    finance_profile_id = fields.Char(
        string='ID Perfil Financeiro',
        copy=False,
        index=True,
        readonly=True,
        groups='base.group_system',
        help='Identificador único para operações financeiras'
    )
    
    is_finance_client = fields.Boolean(
        string='Cliente Financeiro',
        default=False,
        help='Marque se este contato é um cliente de consultoria financeira'
    )
    
    # ================================
    # FIELDS - Rastreamento de Origem
    # ================================
    origin_lead_id = fields.Many2one(
        'crm.lead',
        string='Lead de Origem',
        readonly=True,
        ondelete='set null',
        help='Lead CRM que originou este perfil financeiro (rastreabilidade CRM→Finance)'
    )
    
    origin_lead_name = fields.Char(
        string='Nome do Lead Original',
        related='origin_lead_id.name',
        readonly=True,
        store=False
    )
    
    conversion_date = fields.Datetime(
        string='Data de Conversão',
        readonly=True,
        help='Data/hora em que o lead foi convertido em perfil financeiro'
    )
    
    # ================================
    # FIELDS - Patrimony (AUM)
    # ================================
    currency_id = fields.Many2one(
        'res.currency',
        string='Moeda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    aum = fields.Monetary(
        string='AUM (Patrimônio sob Gestão)',
        compute='_compute_aum',
        store=True,
        currency_field='currency_id',
        help='Total de ativos sob gestão'
    )
    
    aum_updated_at = fields.Datetime(
        string='Última Atualização AUM',
        readonly=True,
        groups='base.group_system'
    )
    
    aum_growth_percent = fields.Float(
        string='Crescimento AUM (%)',
        compute='_compute_aum_growth',
        store=True,
        help='Variação percentual entre último e penúltimo snapshot'
    )
    
    finance_patrimony_ids = fields.One2many(
        'finance.patrimony',
        'partner_id',
        string='Histórico de Patrimônio'
    )
    
    # ================================
    # FIELDS - Dados para Churn Detection
    # ================================
    
    aum_3months_ago = fields.Monetary(
        string='AUM 3 Meses Atrás',
        compute='_compute_aum_3months_ago',
        store=True,
        currency_field='currency_id',
        help='AUM de 3 meses atrás (usado para calcular decline no churn indicator)'
    )
    
    meetings_last_6months = fields.Integer(
        string='Reuniões (6 meses)',
        compute='_compute_meetings_last_6months',
        store=False,
        help='Número de reuniões realizadas nos últimos 6 meses'
    )
    
    response_rate = fields.Float(
        string='Taxa de Resposta (%)',
        compute='_compute_response_rate',
        store=False,
        digits=(5, 2),
        help='Percentual de mensagens respondidas nos últimos 3 meses'
    )
    
    finance_aum_snapshot_ids = fields.One2many(
        'finance.aum.snapshot',
        'partner_id',
        string='Histórico de Snapshots AUM'
    )
    
    # ================================
    # FIELDS - Categorization
    # ================================
    finance_category_ids = fields.Many2many(
        'finance.category',
        'partner_finance_category_rel',
        'partner_id',
        'category_id',
        string='Categorias Financeiras'
    )
    
    client_segment = fields.Selection([
        ('retail', 'Varejo'),
        ('affluent', 'Affluent'),
        ('high_net_worth', 'Alta Renda'),
        ('ultra_high_net_worth', 'Altíssima Renda'),
    ], compute='_compute_client_segment', store=True, string='Segmento', index=True)
    
    # ================================
    # FIELDS - Compliance (Basic)
    # ================================
    kyc_status = fields.Selection([
        ('pending', 'Pendente'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),
        ('expired', 'Expirado'),
        ('rejected', 'Rejeitado'),
    ], string='Status KYC', default='pending', tracking=True, index=True)
    
    kyc_completed_date = fields.Date('Data Conclusão KYC')
    kyc_expiry_date = fields.Date('Data Expiração KYC')
    
    kyc_needs_renewal = fields.Boolean(
        string='KYC Precisa Renovação',
        compute='_compute_kyc_needs_renewal',
        store=True,
        help='True se KYC vence em menos de 30 dias'
    )
    
    is_pep = fields.Boolean(
        string='PEP (Pessoa Politicamente Exposta)',
        tracking=True
    )
    
    risk_profile = fields.Selection([
        ('conservative', 'Conservador'),
        ('moderate', 'Moderado'),
        ('aggressive', 'Arrojado'),
        ('not_defined', 'Não Definido'),
    ], string='Perfil de Risco', default='not_defined', tracking=True, index=True)
    
    # Suitability avançado
    suitability_score = fields.Integer(
        string='Pontuação Suitability',
        tracking=True,
        help='Score de 0 a 100 baseado no questionário de adequação (suitability)'
    )
    
    suitability_last_review = fields.Date(
        string='Última Revisão Suitability',
        tracking=True
    )
    
    suitability_next_review = fields.Date(
        string='Próxima Revisão Suitability',
        compute='_compute_suitability_next_review',
        store=True,
        help='Calculado automaticamente: última revisão + 12 meses'
    )
    
    # ================================
    # FIELDS - Dados Pessoais Estendidos
    # ================================
    marital_status = fields.Selection([
        ('single', 'Solteiro(a)'),
        ('married', 'Casado(a)'),
        ('divorced', 'Divorciado(a)'),
        ('widowed', 'Viúvo(a)'),
        ('other', 'Outro'),
    ], string='Estado Civil')
    
    spouse_name = fields.Char('Nome do Cônjuge')
    spouse_birthdate = fields.Date('Data Nascimento Cônjuge')
    
    children_count = fields.Integer('Número de Filhos', default=0)
    children_names = fields.Text('Nomes e Idades dos Filhos')
    
    # ================================
    # FIELDS - Dados Estratégicos
    # ================================
    birthdate_finance = fields.Date(
        string='Data de Nascimento',
        help='Data de nascimento do cliente'
    )
    
    age = fields.Integer(
        string='Idade',
        compute='_compute_age',
        store=True,
        help='Idade calculada automaticamente'
    )
    
    days_to_birthday = fields.Integer(
        string='Dias para Aniversário',
        compute='_compute_age',
        store=False,
        help='Faltam quantos dias para o próximo aniversário'
    )
    
    favorite_team = fields.Char(
        string='Time do Coração',
        help='Time de futebol ou outro esporte favorito'
    )
    
    hobby = fields.Text(
        string='Hobbie',
        help='Hobbies e interesses pessoais'
    )
    
    practices_sports = fields.Boolean(
        string='Pratica Esportes',
        default=False
    )
    
    sports_details = fields.Char(
        string='Qual Esporte',
        help='Especifique qual(is) esporte(s) pratica'
    )
    
    vehicle = fields.Char(
        string='Veículo que Dirige',
        help='Marca e modelo do veículo'
    )
    
    # ================================
    # FIELDS - Situação Financeira
    # ================================
    annual_income = fields.Monetary(
        string='Renda Anual',
        currency_field='currency_id',
        tracking=True,
        help='Renda bruta anual do cliente'
    )
    
    monthly_expenses = fields.Monetary(
        string='Despesas Mensais',
        currency_field='currency_id',
        help='Despesas mensais estimadas'
    )
    
    saving_capacity = fields.Monetary(
        string='Capacidade de Poupança',
        compute='_compute_saving_capacity',
        store=True,
        currency_field='currency_id',
        help='Calculado: (Renda Anual / 12) - Despesas Mensais'
    )
    
    emergency_fund_months = fields.Float(
        string='Reserva de Emergência (meses)',
        help='Quantos meses de despesas o cliente tem em reserva'
    )
    
    # ================================
    # FIELDS - Objetivos Financeiros
    # ================================
    main_goal = fields.Selection([
        ('retirement', 'Aposentadoria'),
        ('education', 'Educação Filhos'),
        ('property', 'Aquisição Imóvel'),
        ('business', 'Empreender'),
        ('travel', 'Viagens'),
        ('financial_independence', 'Independência Financeira'),
        ('wealth_preservation', 'Preservação Patrimônio'),
        ('other', 'Outro'),
    ], string='Objetivo Principal')
    
    short_term_goal = fields.Text('Objetivo Curto Prazo (1-2 anos)')
    long_term_goal = fields.Text('Objetivo Longo Prazo (5+ anos)')
    
    goal_amount = fields.Monetary(
        string='Valor do Objetivo',
        currency_field='currency_id',
        help='Quanto precisa acumular para atingir o objetivo principal'
    )
    
    goal_deadline_years = fields.Integer(
        string='Prazo (anos)',
        help='Em quantos anos pretende atingir o objetivo'
    )
    
    monthly_contribution_needed = fields.Monetary(
        string='Aporte Mensal Necessário',
        compute='_compute_monthly_contribution',
        store=True,
        currency_field='currency_id',
        help='Calculado usando taxa esperada de retorno'
    )
    
    # ================================
    # FIELDS - Diagnóstico Financeiro
    # ================================
    diagnosis_date = fields.Date('Data do Diagnóstico')
    
    diagnosis_current_situation = fields.Html(
        string='Situação Atual',
        help='Resumo da situação financeira atual do cliente'
    )
    
    diagnosis_strengths = fields.Html(
        string='Pontos Fortes',
        help='O que o cliente está fazendo bem financeiramente'
    )
    
    diagnosis_weaknesses = fields.Html(
        string='Pontos a Melhorar',
        help='Áreas que precisam atenção'
    )
    
    diagnosis_opportunities = fields.Html(
        string='Oportunidades',
        help='Oportunidades de investimento ou otimização'
    )
    
    # ================================
    # FIELDS - Proposta Comercial
    # ================================
    proposal_date = fields.Date('Data da Proposta', tracking=True)
    
    proposal_amount = fields.Monetary(
        string='Valor da Proposta',
        currency_field='currency_id',
        tracking=True,
        help='Patrimônio inicial estimado para gestão'
    )
    
    contract_plan = fields.Selection([
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
        ('custom', 'Customizado'),
    ], string='Plano Contratado', tracking=True)
    
    contract_type = fields.Selection([
        ('monthly', 'Mensal (R$)'),
        ('quarterly', 'Trimestral (R$)'),
        ('semiannual', 'Semestral (R$)'),
        ('annual', 'Anual (R$)'),
        ('aum_percentage', '(%) sobre AUM'),
        ('aum_percentage_plus_fixed', '(%) sobre AUM + (R$ Fixo)'),
    ], string='Tipo de Contrato', tracking=True)
    
    management_fee = fields.Float(
        string='Fee de Gestão (% a.a.)',
        digits=(5, 2),
        tracking=True,
        help='Taxa anual de gestão em percentual'
    )
    
    estimated_annual_revenue = fields.Monetary(
        string='Receita Anual Estimada',
        compute='_compute_estimated_revenue',
        store=True,
        currency_field='currency_id',
        help='Calculado: AUM × Fee de Gestão'
    )
    
    proposal_justification = fields.Html(
        string='Justificativa da Proposta',
        help='Explicação do valor e benefícios da consultoria'
    )
    
    # ================================
    # FIELDS - Relationships
    # ================================
    advisor_id = fields.Many2one(
        'res.users',
        string='Consultor Responsável',
        tracking=True,
        help='Consultor financeiro responsável por este cliente'
    )
    
    advisor_team_id = fields.Many2one(
        'crm.team',
        string='Equipe de Consultoria',
        domain=[('use_opportunities', '=', True)]
    )
    
    # ================================
    # FIELDS - Accounting
    # ================================
    finance_invoice_count = fields.Integer(
        compute='_compute_finance_invoice_count',
        string='Número de Faturas'
    )
    
    patrimony_count = fields.Integer(
        compute='_compute_patrimony_count',
        string='Snapshots de Patrimônio'
    )
    
    # ================================
    # FIELDS - Technical
    # ================================
    finance_notes = fields.Html('Observações Financeiras')
    
    # ================================
    # COMPUTE METHODS
    # ================================
    @api.depends('finance_patrimony_ids', 'finance_patrimony_ids.total_value', 'finance_patrimony_ids.date')
    def _compute_aum(self):
        """Calculate AUM based on most recent patrimony snapshot
        
        Uses only the latest snapshot to avoid inflating AUM by summing historical data.
        """
        for partner in self:
            if partner.finance_patrimony_ids:
                # Get most recent snapshot (sorted by date descending)
                latest_patrimony = partner.finance_patrimony_ids.sorted('date', reverse=True)[:1]
                partner.aum = latest_patrimony.total_value
                partner.aum_updated_at = fields.Datetime.now()
            else:
                partner.aum = 0.0
                partner.aum_updated_at = False
    
    @api.depends('finance_patrimony_ids', 'finance_patrimony_ids.total_value', 'finance_patrimony_ids.date')
    def _compute_aum_growth(self):
        """Calculate AUM growth percentage between last two snapshots"""
        for partner in self:
            snapshots = partner.finance_patrimony_ids.sorted('date', reverse=True)
            if len(snapshots) >= 2:
                latest = snapshots[0].total_value
                previous = snapshots[1].total_value
                if previous > 0:
                    partner.aum_growth_percent = ((latest - previous) / previous) * 100
                else:
                    partner.aum_growth_percent = 0.0
            else:
                partner.aum_growth_percent = 0.0
    
    @api.depends('finance_aum_snapshot_ids', 'finance_aum_snapshot_ids.snapshot_date', 'finance_aum_snapshot_ids.aum_value')
    def _compute_aum_3months_ago(self):
        """
        Calcular AUM de 3 meses atrás usando snapshots mensais
        
        Usado pelo crm.churn.indicator para calcular decline de AUM
        """
        from dateutil.relativedelta import relativedelta
        
        for partner in self:
            if not partner.finance_aum_snapshot_ids:
                partner.aum_3months_ago = 0.0
                continue
            
            # Data de 3 meses atrás
            target_date = fields.Date.today() - relativedelta(months=3)
            
            # Buscar snapshot mais próximo de 3 meses atrás (±15 dias)
            date_min = target_date - timedelta(days=15)
            date_max = target_date + timedelta(days=15)
            
            snapshot = partner.finance_aum_snapshot_ids.filtered(
                lambda s: date_min <= s.snapshot_date <= date_max
            ).sorted('snapshot_date', reverse=True)[:1]
            
            if snapshot:
                partner.aum_3months_ago = snapshot.aum_value
                _logger.debug(
                    f"AUM 3 meses atrás para {partner.name}: "
                    f"R$ {snapshot.aum_value:,.2f} (snapshot: {snapshot.snapshot_date})"
                )
            else:
                # Se não há snapshot de 3 meses, buscar o mais antigo disponível
                oldest_snapshot = partner.finance_aum_snapshot_ids.sorted('snapshot_date')[:1]
                if oldest_snapshot:
                    partner.aum_3months_ago = oldest_snapshot.aum_value
                    _logger.debug(
                        f"AUM 3 meses atrás para {partner.name}: "
                        f"usando snapshot mais antigo - R$ {oldest_snapshot.aum_value:,.2f}"
                    )
                else:
                    partner.aum_3months_ago = 0.0
    
    def _compute_meetings_last_6months(self):
        """
        Contar reuniões concluídas nos últimos 6 meses
        
        Usa mail.activity do Odoo com activity_type_id = 'meeting'
        """
        from dateutil.relativedelta import relativedelta
        
        six_months_ago = fields.Date.today() - relativedelta(months=6)
        
        for partner in self:
            # Buscar atividades do tipo "meeting" concluídas
            if 'mail.activity' in self.env:
                # Buscar activity_type_id de meeting
                meeting_activity = self.env.ref('mail.mail_activity_data_meeting', raise_if_not_found=False)
                
                if meeting_activity:
                    # Contar atividades concluídas (state = 'done' não existe, usamos date_done)
                    # No Odoo, atividades concluídas são deletadas, então vamos contar de outra forma
                    
                    # Alternativa: Contar eventos de calendário (calendar.event)
                    if 'calendar.event' in self.env:
                        meetings = self.env['calendar.event'].search([
                            ('partner_ids', 'in', [partner.id]),
                            ('start', '>=', six_months_ago),
                            ('start', '<=', fields.Datetime.now()),
                        ])
                        partner.meetings_last_6months = len(meetings)
                    else:
                        partner.meetings_last_6months = 0
                else:
                    partner.meetings_last_6months = 0
            else:
                partner.meetings_last_6months = 0
    
    def _compute_response_rate(self):
        """
        Calcular taxa de resposta baseado em mensagens
        
        Lógica:
        - Busca mensagens ENVIADAS para o cliente (últimos 3 meses)
        - Busca mensagens RECEBIDAS do cliente (últimos 3 meses)
        - Taxa = (recebidas / enviadas) * 100
        """
        from dateutil.relativedelta import relativedelta
        
        three_months_ago = datetime.now() - relativedelta(months=3)
        
        for partner in self:
            if 'mail.message' not in self.env:
                partner.response_rate = 0.0
                continue
            
            # Mensagens ENVIADAS para o cliente (message_type = 'email' ou 'comment')
            sent_messages = self.env['mail.message'].search_count([
                ('model', '=', 'res.partner'),
                ('res_id', '=', partner.id),
                ('message_type', 'in', ['email', 'comment']),
                ('date', '>=', three_months_ago),
                ('author_id', '!=', partner.id),  # Não enviadas pelo próprio cliente
            ])
            
            # Mensagens RECEBIDAS do cliente (author_id = partner)
            received_messages = self.env['mail.message'].search_count([
                ('model', '=', 'res.partner'),
                ('res_id', '=', partner.id),
                ('message_type', 'in', ['email', 'comment']),
                ('date', '>=', three_months_ago),
                ('author_id', '=', partner.id),  # Enviadas pelo cliente
            ])
            
            # Calcular taxa de resposta
            if sent_messages > 0:
                partner.response_rate = (received_messages / sent_messages) * 100
            else:
                partner.response_rate = 0.0
                
    @api.depends('aum')
    def _compute_client_segment(self):
        """Automatic segmentation based on AUM"""
        # Get thresholds from configuration
        ICP = self.env['ir.config_parameter'].sudo()
        retail_max = float(ICP.get_param('finance_core.retail_max', '100000'))
        affluent_max = float(ICP.get_param('finance_core.affluent_max', '1000000'))
        hnw_max = float(ICP.get_param('finance_core.hnw_max', '10000000'))
        
        for partner in self:
            if partner.aum < retail_max:
                partner.client_segment = 'retail'
            elif partner.aum < affluent_max:
                partner.client_segment = 'affluent'
            elif partner.aum < hnw_max:
                partner.client_segment = 'high_net_worth'
            else:
                partner.client_segment = 'ultra_high_net_worth'
    
    @api.depends('kyc_expiry_date', 'kyc_status')
    def _compute_kyc_needs_renewal(self):
        """Check if KYC expires in less than 30 days"""
        today = fields.Date.today()
        for partner in self:
            if partner.kyc_status == 'completed' and partner.kyc_expiry_date:
                days_to_expiry = (partner.kyc_expiry_date - today).days
                partner.kyc_needs_renewal = 0 < days_to_expiry <= 30
            else:
                partner.kyc_needs_renewal = False
    
    @api.depends('annual_income', 'monthly_expenses')
    def _compute_saving_capacity(self):
        """Calcula capacidade de poupança mensal"""
        for partner in self:
            if partner.annual_income and partner.monthly_expenses:
                monthly_income = partner.annual_income / 12.0
                partner.saving_capacity = monthly_income - partner.monthly_expenses
            else:
                partner.saving_capacity = 0.0
    
    @api.depends('goal_amount', 'goal_deadline_years', 'risk_profile')
    def _compute_monthly_contribution(self):
        """
        Calcula aporte mensal necessário usando fórmula PMT
        FV = PMT × [((1 + i)^n - 1) / i]
        PMT = FV / [((1 + i)^n - 1) / i]
        """
        for partner in self:
            if not partner.goal_amount or not partner.goal_deadline_years:
                partner.monthly_contribution_needed = 0.0
                continue
            
            # Taxa esperada baseada no perfil de risco
            expected_returns = {
                'conservative': 0.08,  # 8% a.a.
                'moderate': 0.10,      # 10% a.a.
                'aggressive': 0.12,    # 12% a.a.
                'not_defined': 0.10,   # Default 10%
            }
            
            annual_rate = expected_returns.get(partner.risk_profile, 0.10)
            monthly_rate = annual_rate / 12.0
            months = partner.goal_deadline_years * 12
            
            # Fórmula PMT para valor futuro
            if monthly_rate > 0:
                fv_factor = ((1 + monthly_rate) ** months - 1) / monthly_rate
                partner.monthly_contribution_needed = partner.goal_amount / fv_factor
            else:
                # Se taxa zero, divisão simples
                partner.monthly_contribution_needed = partner.goal_amount / months
    
    @api.depends('suitability_last_review')
    def _compute_suitability_next_review(self):
        """Próxima revisão: 12 meses após última revisão"""
        for partner in self:
            if partner.suitability_last_review:
                from dateutil.relativedelta import relativedelta
                partner.suitability_next_review = partner.suitability_last_review + relativedelta(months=12)
            else:
                partner.suitability_next_review = False
    
    @api.depends('aum', 'management_fee')
    def _compute_estimated_revenue(self):
        """Receita anual estimada: AUM × Fee de Gestão"""
        for partner in self:
            if partner.aum and partner.management_fee:
                partner.estimated_annual_revenue = partner.aum * (partner.management_fee / 100.0)
            else:
                partner.estimated_annual_revenue = 0.0
    
    @api.depends('birthdate_finance')
    def _compute_age(self):
        """Calcular idade e dias para próximo aniversário"""
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        today = date.today()
        
        for partner in self:
            if partner.birthdate_finance:
                birthdate = partner.birthdate_finance
                
                # Calcular idade
                partner.age = relativedelta(today, birthdate).years
                
                # Calcular dias para próximo aniversário
                next_birthday = date(today.year, birthdate.month, birthdate.day)
                
                # Se o aniversário já passou este ano, considerar o próximo ano
                if next_birthday < today:
                    next_birthday = date(today.year + 1, birthdate.month, birthdate.day)
                
                partner.days_to_birthday = (next_birthday - today).days
            else:
                partner.age = 0
                partner.days_to_birthday = 0
                
    def _compute_finance_invoice_count(self):
        """Count invoices related to financial services"""
        Invoice = self.env['account.move']
        for partner in self:
            partner.finance_invoice_count = Invoice.search_count([
                ('partner_id', 'child_of', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '!=', 'cancel'),
            ])
    
    def _compute_patrimony_count(self):
        """Count patrimony snapshots"""
        for partner in self:
            partner.patrimony_count = len(partner.finance_patrimony_ids)
    
    # ================================
    # ONCHANGE METHODS
    # ================================
    @api.onchange('is_finance_client')
    def _onchange_is_finance_client(self):
        """Auto-fill data when marking as finance client"""
        if self.is_finance_client and not self.finance_profile_id:
            self.finance_profile_id = self._generate_profile_id()
            
    # ================================
    # CONSTRAINT METHODS
    # ================================
    # NOTA: Constraint de unicidade do finance_profile_id movido para SQL (_sql_constraints)
    # para melhor performance - não executa em todo write(), apenas em INSERT/UPDATE real
    
    @api.constrains('kyc_expiry_date', 'kyc_completed_date')
    def _check_kyc_dates(self):
        """Validate KYC dates"""
        for partner in self:
            if partner.kyc_completed_date and partner.kyc_expiry_date:
                if partner.kyc_expiry_date <= partner.kyc_completed_date:
                    raise ValidationError(_(
                        'KYC Expiry Date must be after Completed Date'
                    ))
    
    @api.constrains('management_fee')
    def _check_management_fee(self):
        """Validate management fee is between 0 and 100"""
        for partner in self:
            if partner.management_fee:
                if partner.management_fee < 0 or partner.management_fee > 100:
                    raise ValidationError(_(
                        'Fee de Gestão deve estar entre 0%% e 100%%'
                    ))
    
    @api.constrains('goal_deadline_years')
    def _check_goal_deadline(self):
        """Validate goal deadline is positive"""
        for partner in self:
            if partner.goal_deadline_years and partner.goal_deadline_years < 0:
                raise ValidationError(_(
                    'Prazo do objetivo deve ser positivo'
                ))
    
    @api.constrains('suitability_score')
    def _check_suitability_score(self):
        """Validate suitability score is between 0 and 100"""
        for partner in self:
            if partner.suitability_score:
                if partner.suitability_score < 0 or partner.suitability_score > 100:
                    raise ValidationError(_(
                        'Pontuação Suitability deve estar entre 0 e 100'
                    ))
    
    # ================================
    # CRUD METHODS
    # ================================
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate automatic Profile ID"""
        for vals in vals_list:
            if vals.get('is_finance_client') and not vals.get('finance_profile_id'):
                vals['finance_profile_id'] = self._generate_profile_id()
        
        partners = super().create(vals_list)
        return partners
    
    def write(self, vals):
        """Override write to auto-generate Profile ID when toggle is activated
        
        Handles batch operations correctly by generating individual IDs for each partner.
        """
        # If activating finance client toggle, generate individual IDs
        if vals.get('is_finance_client'):
            # Generate ID for each partner that doesn't have one
            for partner in self:
                if not partner.finance_profile_id:
                    # Use super().write to avoid recursion
                    super(ResPartner, partner).write({
                        'finance_profile_id': partner._generate_profile_id()
                    })
            # Remove from vals to avoid overwriting individual IDs
            vals = dict(vals)  # Copy to avoid modifying original
            vals.pop('finance_profile_id', None)
        
        result = super().write(vals)
        
        # ============================================================
        # AUTOMAÇÃO: Cria pastas de documentos ao ativar toggle
        # ============================================================
        if vals.get('is_finance_client'):
            for partner in self:
                if partner.finance_profile_id and not partner.client_folder_id:
                    partner._create_client_folder_structure()
        
        return result
    
    # ================================
    # ACTION METHODS
    # ================================
    def action_view_finance_invoices(self):
        """Open client's financial invoices"""
        self.ensure_one()
        return {
            'name': _('Faturas Financeiras'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('partner_id', 'child_of', self.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ],
            'context': {
                'default_partner_id': self.id,
                'default_move_type': 'out_invoice',
            }
        }
    
    def action_view_patrimony_history(self):
        """Open client's patrimony history"""
        self.ensure_one()
        return {
            'name': _('Histórico de Patrimônio - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'finance.patrimony',
            'view_mode': 'list,form,graph,pivot',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_group_date': 1,
            }
        }
    
    def action_update_aum(self):
        """Force AUM update (called by cron or manually)"""
        self._compute_aum()
        return True
    
    def refresh_aum(self):
        """Force refresh AUM and persist changes
        
        Unlike action_update_aum, this method ensures changes are written to database.
        Useful for manual refresh or after bulk snapshot imports.
        """
        self.ensure_one()
        self._compute_aum()
        # Force write to trigger compute dependencies
        return self.write({'aum_updated_at': fields.Datetime.now()})
    
    @api.model
    def action_generate_missing_profile_ids(self):
        """Generate Profile IDs for existing finance clients without one
        
        Can be called from:
        - Settings → Technical → Server Actions
        - Odoo Shell
        - Scheduled Action
        """
        partners_without_id = self.search([
            ('is_finance_client', '=', True),
            ('finance_profile_id', '=', False)
        ])
        
        if not partners_without_id:
            _logger.info("All finance clients already have Profile IDs")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Perfis Completos'),
                    'message': _('Todos os clientes já possuem Profile ID'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        updated_count = 0
        failed = []
        
        for partner in partners_without_id:
            try:
                profile_id = partner._generate_profile_id()
                partner.write({'finance_profile_id': profile_id})
                updated_count += 1
                _logger.info(f"Generated Profile ID for {partner.name}: {profile_id}")
            except Exception as e:
                failed.append(partner.name)
                _logger.error(f"Failed to generate ID for {partner.name}: {e}")
        
        message = _('%d Profile IDs gerados com sucesso') % updated_count
        if failed:
            message += _('\n\nFalhas (%d): %s') % (len(failed), ', '.join(failed))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Profile IDs Gerados'),
                'message': message,
                'type': 'success' if not failed else 'warning',
                'sticky': True,
            }
        }
    
    # ================================
    # HELPER METHODS
    # ================================
    def _generate_profile_id(self):
        """Generate unique Profile ID using sequence (format: FIN-DD.MM.YYYY-XXXX)
        
        The sequence already includes the FIN- prefix, this method just calls next_by_code
        """
        sequence_value = self.env['ir.sequence'].next_by_code('finance.profile')
        if not sequence_value:
            # Fallback manual generation if sequence fails
            today = fields.Date.today()
            date_str = today.strftime('%d.%m.%Y')
            last_id = self.search([], order='id desc', limit=1)
            next_num = (last_id.id + 1) if last_id else 1
            return f'FIN-{date_str}-{next_num:04d}'
        return sequence_value
    
    def compute_roi(self, start_date, end_date):
        """Calcular ROI (Return on Investment) entre duas datas
        
        Args:
            start_date (date): Data inicial
            end_date (date): Data final
            
        Returns:
            float: ROI em percentual (ex: 15.5 para 15.5%)
        """
        self.ensure_one()
        
        start_snap = self.finance_patrimony_ids.filtered(
            lambda x: x.date == start_date
        )
        end_snap = self.finance_patrimony_ids.filtered(
            lambda x: x.date == end_date
        )
        
        if start_snap and end_snap and start_snap.total_value > 0:
            roi = ((end_snap.total_value - start_snap.total_value) / 
                   start_snap.total_value) * 100
            return round(roi, 2)
        
        return 0.0
    
    def is_segment(self, segment_name):
        """Helper to check client segment
        
        Args:
            segment_name (str): 'retail', 'affluent', 'high_net_worth', 'ultra_high_net_worth'
            
        Returns:
            bool: True if partner belongs to specified segment
            
        Example:
            if partner.is_segment('high_net_worth'):
                # Apply HNW specific logic
        """
        self.ensure_one()
        return self.client_segment == segment_name
    
    def schedule_next_review(self):
        """Schedule next suitability review (12 months from last review)
        
        Returns:
            date: Next review date
        """
        self.ensure_one()
        if self.suitability_last_review:
            next_review = self.suitability_last_review + timedelta(days=365)
        else:
            next_review = fields.Date.today() + timedelta(days=365)
        
        self.suitability_next_review = next_review
        return next_review
    
    @api.model
    def _cron_update_kyc_expiry(self):
        """Scheduled action to mark expired KYC"""
        expired_partners = self.search([
            ('kyc_status', '=', 'completed'),
            ('kyc_expiry_date', '<', fields.Date.today())
        ])
        
        if expired_partners:
            expired_partners.write({'kyc_status': 'expired'})
            _logger.info(f'Marked {len(expired_partners)} KYC as expired')
        
        # Notify advisors about KYC expiring soon (30 days)
        expiring_soon = self.search([
            ('kyc_status', '=', 'completed'),
            ('kyc_expiry_date', '<=', fields.Date.today() + timedelta(days=30)),
            ('kyc_expiry_date', '>', fields.Date.today())
        ])
        
        for partner in expiring_soon:
            if partner.advisor_id:
                partner.message_post(
                    body=_('KYC expirará em %s') % partner.kyc_expiry_date,
                    partner_ids=[partner.advisor_id.partner_id.id],
                    subtype_xmlid='mail.mt_note'
                )
    
    # ============================================================
    # INTEGRAÇÃO COM SISTEMA DE DOCUMENTOS (gz_finance_docs)
    # ============================================================
    
    def _create_client_folder_structure(self):
        """
        Cria estrutura de pastas de documentos ao ativar toggle Cliente Consultoria.
        
        **Trigger:** 
        - Partner.is_finance_client = True
        - Partner.finance_profile_id exists
        - Partner.client_folder_id not exists
        
        **Estrutura criada:**
        
        📁 Clientes
          └─ 📁 João da Silva (FIN-29.11.2025-0008)
              ├─ ✅ Suitability
              ├─ 📋 Cadastro e Documentação
              ├─ 📜 Política de Investimento
              ├─ 🤝 Atas de Reunião
              ├─ 💰 Financeiro
              ├─ 📊 Relatórios
              └─ 📝 Contratos
        
        **Idempotência:** Pode chamar N vezes, cria apenas 1 vez.
        **Módulo:** Requer gz_finance_docs instalado.
        """
        self.ensure_one()
        
        # Validações
        if not self.finance_profile_id:
            return
        
        if self.client_folder_id:
            return  # Já tem pasta criada
        
        # Verifica se módulo gz_finance_docs está instalado
        try:
            folder_model = self.env['document_hub.folder']
        except KeyError:
            # Módulo não instalado
            _logger.warning("gz_finance_docs não instalado - pulando criação de pastas")
            return
        
        # Busca pasta raiz "Clientes"
        try:
            root_folder = self.env.ref('gz_finance_docs.folder_clientes')
        except:
            _logger.warning("Pasta raiz 'Clientes' não encontrada - pulando criação de pastas")
            return
        
        # Cria pasta principal do cliente
        client_folder_name = f"{self.name} ({self.finance_profile_id})"
        
        client_folder = folder_model.create({
            'name': client_folder_name,
            'description': f"Documentos do cliente {self.name}. "
                          f"Criada automaticamente ao ativar Cliente Consultoria.",
            'parent_folder_id': root_folder.id,
            'partner_id': self.id,
            'client_folder': True,
            'visibility_administration': True,
            'visibility_salesman': True,
        })
        
        # Define subpastas padrão
        subfolders = [
            ('✅ Suitability', 'Questionários API, análises de perfil de risco e adequação de produtos.'),
            ('📋 Cadastro e Documentação', 'Documentos pessoais, comprovantes, procurações e ficha cadastral.'),
            ('📜 Política de Investimento', 'IPS (Investment Policy Statement) e diretrizes personalizadas.'),
            ('🤝 Atas de Reunião', 'Registros de reuniões, decisões de investimento e follow-ups.'),
            ('💰 Financeiro', 'Notas fiscais, recibos e documentação financeira do cliente.'),
            ('📊 Relatórios', 'Relatórios de performance, análises e rebalanceamentos de carteira.'),
            ('📝 Contratos', 'Contratos de assessoria, termos de adesão e acordos de gestão.'),
        ]
        
        # Cria cada subpasta
        for subfolder_name, subfolder_description in subfolders:
            folder_model.create({
                'name': subfolder_name,
                'description': subfolder_description,
                'parent_folder_id': client_folder.id,
                'partner_id': self.id,
                'visibility_administration': True,
                'visibility_salesman': True,
            })
        
        # Vincula pasta ao partner
        self.client_folder_id = client_folder.id
        
        # Notifica no chatter
        self.message_post(
            body=_(
                "📁 <strong>Estrutura de documentos criada automaticamente</strong><br/>"
                "Pasta principal: <b>%s</b><br/>"
                "Subpastas criadas: 7 (Suitability, Cadastro, Política, Atas, Financeiro, Relatórios, Contratos)<br/>"
                "<a href='/web#model=document_hub.folder&id=%s'>📂 Abrir Pasta do Cliente</a>"
            ) % (client_folder_name, client_folder.id)
        )
        
        _logger.info(f"Pastas criadas para cliente {self.name} ({self.finance_profile_id})")
