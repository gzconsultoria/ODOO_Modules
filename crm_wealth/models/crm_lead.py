# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # ============================================================
    # CAMPOS COMPUTADOS PARA CONTROLE DE VISIBILIDADE DAS ABAS
    # ============================================================
    
    stage_sequence = fields.Integer(
        string='Sequência do Estágio',
        related='stage_id.sequence',
        store=True,
        readonly=True
    )
    
    show_captacao = fields.Boolean(
        string='Mostrar Aba Captação',
        compute='_compute_show_tabs',
        store=False
    )
    
    show_qualificacao = fields.Boolean(
        string='Mostrar Aba Qualificação',
        compute='_compute_show_tabs',
        store=False
    )
    
    show_reuniao = fields.Boolean(
        string='Mostrar Aba Reunião',
        compute='_compute_show_tabs',
        store=False
    )
    
    show_proposta = fields.Boolean(
        string='Mostrar Aba Proposta',
        compute='_compute_show_tabs',
        store=False
    )
    
    show_onboarding = fields.Boolean(
        string='Mostrar Aba Onboarding',
        compute='_compute_show_tabs',
        store=False
    )
    
    show_execucao = fields.Boolean(
        string='Mostrar Aba Execução',
        compute='_compute_show_tabs',
        store=False
    )

    # ============================================================
    # ABA 1: CAPTAÇÃO
    # ============================================================
    
    origem_lead = fields.Selection([
        ('instagram', 'Instagram'),
        ('indicacao', 'Indicação'),
        ('site', 'Site'),
        ('whatsapp', 'WhatsApp'),
        ('evento', 'Evento'),
        ('midia_paga', 'Mídia Paga'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('outros', 'Outros'),
    ], string='Origem do Lead', tracking=True)
    
    momento_financeiro = fields.Selection([
        ('organizando', 'Organizando finanças'),
        ('iniciando', 'Iniciando investimentos'),
        ('planejamento', 'Buscando planejamento'),
        ('especialista', 'Busca de especialista'),
    ], string='Momento Financeiro Atual', tracking=True)
    
    patrimonio_aproximado = fields.Selection([
        ('ate_50k', 'Até R$ 50.000'),
        ('50k_200k', 'R$ 50.000 - R$ 200.000'),
        ('200k_500k', 'R$ 200.000 - R$ 500.000'),
        ('500k_1m', 'R$ 500.000 - R$ 1.000.000'),
        ('1m_mais', 'Acima de R$ 1.000.000'),
    ], string='Patrimônio Aproximado', tracking=True)
    
    renda_mensal = fields.Selection([
        ('ate_5k', 'Até R$ 5.000'),
        ('5k_10k', 'R$ 5.000 - R$ 10.000'),
        ('10k_20k', 'R$ 10.000 - R$ 20.000'),
        ('20k_50k', 'R$ 20.000 - R$ 50.000'),
        ('50k_mais', 'Acima de R$ 50.000'),
    ], string='Renda Mensal', tracking=True)
    
    interesse_inicial = fields.Many2many(
        'crm.wealth.interesse',
        string='Interesses Iniciais',
        help='Principais áreas de interesse do lead'
    )
    
    # ============================================================
    # ABA 2: QUALIFICAÇÃO
    # ============================================================
    
    perfil_investidor = fields.Selection([
        ('conservador', 'Conservador'),
        ('moderado', 'Moderado'),
        ('arrojado', 'Arrojado'),
        ('qualificado', 'Qualificado'),
    ], string='Perfil do Investidor - Suitability Preliminar', tracking=True)
    
    dor_principal = fields.Selection([
        ('tempo', 'Tempo'),
        ('estrategia', 'Estratégia'),
        ('medo', 'Medo de perder dinheiro'),
        ('organizacao', 'Organização financeira'),
        ('juros_dividas', 'Juros / Dívidas'),
        ('aposentadoria', 'Aposentadoria'),
    ], string='Dor Principal', tracking=True)
    
    objetivo_curto_prazo = fields.Text(
        string='Objetivo de Curto Prazo (12 meses)',
        help='Ex.: investir melhor, sair do zero, quitar dívidas'
    )
    
    objetivo_longo_prazo = fields.Text(
        string='Objetivo de Longo Prazo (5+ anos)',
        help='Ex.: FIRE, comprar imóvel, aposentadoria, independência financeira'
    )
    
    # ============================================================
    # ABA 3: REUNIÃO ESTRATÉGICA
    # ============================================================
    
    diagnostico_situacao_atual = fields.Text(
        string='Situação Atual'
    )
    
    diagnostico_pontos_fortes = fields.Text(
        string='Pontos Fortes'
    )
    
    diagnostico_pontos_melhorar = fields.Text(
        string='Pontos a Melhorar'
    )
    
    diagnostico_oportunidades = fields.Text(
        string='Oportunidades de Estratégia'
    )
    
    estrategias_recomendadas = fields.Many2many(
        'crm.wealth.estrategia',
        string='Estratégias Recomendadas',
        help='Renda fixa, Tesouro, FIIs, ETFs, Previdência, Proteção'
    )
    
    score_potencial = fields.Selection([
        ('0', '⭐ 0 estrelas'),
        ('1', '⭐ 1 estrela'),
        ('2', '⭐⭐ 2 estrelas'),
        ('3', '⭐⭐⭐ 3 estrelas'),
        ('4', '⭐⭐⭐⭐ 4 estrelas'),
        ('5', '⭐⭐⭐⭐⭐ 5 estrelas'),
    ], string='Score de Potencial', tracking=True)
    
    # ============================================================
    # ABA 4: PROPOSTA
    # ============================================================
    
    plano_contratado = fields.Selection([
        ('consultoria_mensal', 'Consultoria Mensal'),
        ('plano_fire', 'Plano FIRE'),
        ('plano_premium', 'Plano Premium'),
        ('gestao_completa', 'Gestão Completa'),
        ('mentoria', 'Mentoria'),
        ('personalizado', 'Personalizado'),
    ], string='Plano Sugerido', tracking=True)
    
    valor_proposta = fields.Monetary(
        string='Valor da Proposta',
        currency_field='company_currency',
        tracking=True
    )
    
    justificativa_valor = fields.Text(
        string='Justificativa de Valor',
        help='Explicação curta do racional da proposta'
    )
    
    objecoes_apresentadas = fields.Many2many(
        'crm.wealth.objecao',
        string='Objeções Apresentadas',
        help='Preço, tempo, medo, complexidade, confiança'
    )
    
    # ============================================================
    # ABA 5: ONBOARDING
    # ============================================================
    
    suitability_oficial = fields.Boolean(
        string='Suitability Oficial Preenchido?',
        tracking=True
    )
    
    documentos_entregues = fields.Many2many(
        'crm.wealth.documento',
        string='Documentos Entregues',
        help='ID, comprovante, extratos, carteira atual'
    )
    
    perfil_risco_final = fields.Selection([
        ('conservador', 'Conservador'),
        ('moderado', 'Moderado'),
        ('arrojado', 'Arrojado'),
        ('qualificado', 'Qualificado'),
        ('superqualificado', 'Superqualificado'),
    ], string='Perfil de Risco Final', tracking=True)
    
    estrutura_inicial_montada = fields.Boolean(
        string='Estrutura Inicial Montada?',
        tracking=True
    )
    
    contas_corretoras = fields.Many2many(
        'crm.wealth.corretora',
        string='Contas de Corretoras',
        help='Clear, Genial, XP, BTG, Banco Inter, etc.'
    )
    
    # ============================================================
    # ABA 6: EXECUÇÃO & ACOMPANHAMENTO
    # ============================================================
    
    valor_investido_atual = fields.Monetary(
        string='Valor Investido Atual',
        currency_field='company_currency',
        help='Estimado ou integrado via API externa'
    )
    
    distribuicao_portfolio = fields.Text(
        string='Distribuição de Portfólio',
        help='Descrição da alocação atual (pode ser JSON para dashboard futuro)'
    )
    
    acompanhamento_mensal_ids = fields.One2many(
        'crm.wealth.acompanhamento',
        'lead_id',
        string='Acompanhamento Mensal'
    )
    
    historico_mudancas = fields.Text(
        string='Histórico de Mudanças',
        help='Ex.: Mudamos %RF para %RV, etc.'
    )

    # ============================================================
    # MÉTODOS COMPUTADOS
    # ============================================================
    
    @api.depends('stage_id', 'stage_id.sequence', 'stage_sequence')
    def _compute_show_tabs(self):
        """
        Controla a visibilidade das abas baseado no estágio atual.
        Regra: mostra a aba atual e todas as anteriores.
        
        Sequências dos estágios Wealth:
        - Captação: 10
        - Qualificação: 20  
        - Reunião: 30
        - Proposta: 40
        - Onboarding: 50
        - Execução: 60
        """
        for lead in self:
            # Usa stage_sequence (campo related) para pegar a sequência
            seq = lead.stage_sequence or 0
            
            # Mostra aba atual e todas anteriores
            lead.show_captacao = seq >= 10
            lead.show_qualificacao = seq >= 20
            lead.show_reuniao = seq >= 30
            lead.show_proposta = seq >= 40
            lead.show_onboarding = seq >= 50
            lead.show_execucao = seq >= 60


# ============================================================
# MODELOS AUXILIARES (Many2many)
# ============================================================

class CrmWealthInteresse(models.Model):
    _name = 'crm.wealth.interesse'
    _description = 'Interesses do Lead'
    _order = 'name'

    name = fields.Char(string='Interesse', required=True)
    active = fields.Boolean(default=True)


class CrmWealthEstrategia(models.Model):
    _name = 'crm.wealth.estrategia'
    _description = 'Estratégias de Investimento'
    _order = 'name'

    name = fields.Char(string='Estratégia', required=True)
    descricao = fields.Text(string='Descrição')
    active = fields.Boolean(default=True)


class CrmWealthObjecao(models.Model):
    _name = 'crm.wealth.objecao'
    _description = 'Objeções do Cliente'
    _order = 'name'

    name = fields.Char(string='Objeção', required=True)
    tratativa_padrao = fields.Text(string='Tratativa Padrão')
    active = fields.Boolean(default=True)


class CrmWealthDocumento(models.Model):
    _name = 'crm.wealth.documento'
    _description = 'Documentos do Cliente'
    _order = 'name'

    name = fields.Char(string='Documento', required=True)
    obrigatorio = fields.Boolean(string='Obrigatório?', default=False)
    active = fields.Boolean(default=True)


class CrmWealthCorretora(models.Model):
    _name = 'crm.wealth.corretora'
    _description = 'Corretoras'
    _order = 'name'

    name = fields.Char(string='Corretora', required=True)
    active = fields.Boolean(default=True)
