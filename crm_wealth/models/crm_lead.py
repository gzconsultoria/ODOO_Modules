# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


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
    # CAMPOS DE COMPLETUDE (% DE PREENCHIMENTO POR ABA)
    # ============================================================
    
    captacao_completude = fields.Integer(
        string='Completude Captação (%)',
        compute='_compute_completude_abas',
        store=False
    )
    
    qualificacao_completude = fields.Integer(
        string='Completude Qualificação (%)',
        compute='_compute_completude_abas',
        store=False
    )
    
    reuniao_completude = fields.Integer(
        string='Completude Reunião (%)',
        compute='_compute_completude_abas',
        store=False
    )
    
    proposta_completude = fields.Integer(
        string='Completude Proposta (%)',
        compute='_compute_completude_abas',
        store=False
    )
    
    onboarding_completude = fields.Integer(
        string='Completude Onboarding (%)',
        compute='_compute_completude_abas',
        store=False
    )
    
    execucao_completude = fields.Integer(
        string='Completude Execução (%)',
        compute='_compute_completude_abas',
        store=False
    )

    # ============================================================
    # CAMPOS PESSOAIS (Para conexão emocional com cliente)
    # ============================================================
    
    data_aniversario_cliente = fields.Date(
        string="Aniversário do Cliente",
        help="Data de aniversário do cliente"
    )
    
    estado_civil = fields.Selection([
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)')
    ], string="Estado Civil")
    
    nome_conjuge = fields.Char(string="Nome do(a) Cônjuge")
    
    data_aniversario_conjuge = fields.Date(string="Aniversário do(a) Cônjuge")
    
    quantidade_filhos = fields.Integer(string="Quantidade de Filhos", default=0)
    
    nomes_filhos = fields.Text(
        string="Nomes e Idades dos Filhos",
        help="Ex: João (5 anos), Maria (8 anos)"
    )
    
    time_coracao = fields.Char(string="Time do Coração")
    
    hobbies = fields.Text(
        string="Hobbies/Interesses",
        help="Ex: Golfe, Viagens, Culinária"
    )

    # ============================================================
    # CAMPOS PARA ABA RESUMO
    # ============================================================
    
    score_qualificacao = fields.Integer(
        string="Score de Qualificação",
        compute='_compute_score_qualificacao',
        store=False,
        help="Score de 0-100 baseado em completude, engajamento e potencial financeiro"
    )
    
    lead_temperature = fields.Selection([
        ('cold', '🔵 Frio'),
        ('warm', '🟡 Morno'),
        ('hot', '🔴 Quente')
    ], string="Temperatura do Lead", compute='_compute_lead_temperature', store=False)
    
    dias_em_pipeline = fields.Integer(
        string="Dias em Pipeline",
        compute='_compute_dias_pipeline',
        store=False
    )
    
    progresso_geral = fields.Float(
        string="Progresso Geral (%)",
        compute='_compute_progresso_geral',
        store=False
    )
    
    alertas_resumo = fields.Html(
        string="Alertas e Lembretes",
        compute='_compute_alertas_resumo',
        store=False
    )
    
    perfil_pessoal_resumo = fields.Html(
        string="Perfil Pessoal",
        compute='_compute_perfil_pessoal_resumo',
        store=False
    )

    # ============================================================
    # CAMPOS PARA SLA E RASTREAMENTO DE TEMPO
    # ============================================================
    
    stage_date = fields.Datetime(
        string='Data de Entrada no Estágio',
        help='Quando o lead entrou no estágio atual (usado para cálculo de SLA)',
        tracking=True,
        copy=False
    )
    
    days_in_current_stage = fields.Integer(
        string='Dias no Estágio Atual',
        compute='_compute_days_in_stage',
        store=False,
        help='Quantos dias o lead está no estágio atual'
    )
    
    sla_status = fields.Selection([
        ('ok', '✅ Dentro do Prazo'),
        ('warning', '⚠️ Próximo do Limite'),
        ('exceeded', '🔴 SLA Estourado')
    ], string='Status SLA', compute='_compute_sla_status', store=False)

    # ============================================================
    # ABA 1: CAPTAÇÃO
    # ============================================================
    
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
    
    objetivo_principal = fields.Selection([
        ('aposentadoria', 'Aposentadoria'),
        ('fire', 'Independência Financeira (FIRE)'),
        ('imovel', 'Comprar Imóvel'),
        ('educacao_filhos', 'Educação dos Filhos'),
        ('viagem', 'Viagem dos Sonhos'),
        ('empreender', 'Empreender'),
        ('outro', 'Outro'),
    ], string='Objetivo Principal', tracking=True)
    
    valor_objetivo = fields.Monetary(
        string='Valor do Objetivo (R$)',
        currency_field='company_currency',
        help='Quanto precisa acumular para atingir o objetivo'
    )
    
    prazo_objetivo = fields.Integer(
        string='Prazo para Objetivo (anos)',
        help='Em quantos anos deseja atingir o objetivo'
    )
    
    aporte_mensal_necessario = fields.Monetary(
        string='Aporte Mensal Necessário',
        currency_field='company_currency',
        compute='_compute_calculos_financeiros',
        store=True,
        help='Calculado considerando taxa de 10% a.a. e prazo definido'
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
    
    data_reuniao = fields.Date(
        string='Data da Reunião',
        tracking=True
    )
    
    estrategias_discutidas = fields.Text(
        string='Estratégias Discutidas',
        help='Resumo das estratégias discutidas na reunião'
    )
    
    objecoes_identificadas = fields.Text(
        string='Objeções Identificadas',
        help='Principais objeções ou dúvidas levantadas'
    )
    
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
    
    # Campos para cálculos automáticos
    fee_gestao = fields.Float(
        string='Fee de Gestão (% a.a.)',
        digits=(5, 2),
        help='Taxa anual de gestão em porcentagem',
        tracking=True
    )
    
    tipo_contrato = fields.Selection([
        ('mensal', 'Mensal'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
        ('percentual_aum', '% sobre AUM'),
    ], string='Tipo de Contrato', tracking=True)
    
    receita_anual_estimada = fields.Monetary(
        string='Receita Anual Estimada',
        currency_field='company_currency',
        compute='_compute_calculos_financeiros',
        store=True,
        help='Calculado como: Valor da Proposta × Fee de Gestão'
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
    
    @api.depends(
        'momento_financeiro', 'patrimonio_aproximado', 'renda_mensal', 'interesse_inicial',
        'perfil_investidor', 'dor_principal', 'objetivo_principal', 'prazo_objetivo',
        'data_reuniao', 'estrategias_discutidas', 'objecoes_identificadas',
        'valor_proposta', 'fee_gestao', 'tipo_contrato',
        'suitability_oficial', 'perfil_risco_final', 'documentos_entregues',
        'valor_investido_atual', 'distribuicao_portfolio'
    )
    def _compute_completude_abas(self):
        """
        Calcula a porcentagem de campos obrigatórios preenchidos em cada aba.
        Usado para mostrar indicadores visuais de completude.
        """
        for lead in self:
            # ABA 1: CAPTAÇÃO (4 campos importantes)
            captacao_campos = [
                lead.momento_financeiro,
                lead.patrimonio_aproximado,
                lead.renda_mensal,
                lead.interesse_inicial,
            ]
            lead.captacao_completude = self._calcular_percentual(captacao_campos)
            
            # ABA 2: QUALIFICAÇÃO (4 campos importantes)
            qualificacao_campos = [
                lead.perfil_investidor,
                lead.dor_principal,
                lead.objetivo_principal,
                lead.prazo_objetivo,
            ]
            lead.qualificacao_completude = self._calcular_percentual(qualificacao_campos)
            
            # ABA 3: REUNIÃO (3 campos importantes)
            reuniao_campos = [
                lead.data_reuniao,
                lead.estrategias_discutidas,
                lead.objecoes_identificadas,
            ]
            lead.reuniao_completude = self._calcular_percentual(reuniao_campos)
            
            # ABA 4: PROPOSTA (3 campos importantes)
            proposta_campos = [
                lead.valor_proposta,
                lead.fee_gestao,
                lead.tipo_contrato,
            ]
            lead.proposta_completude = self._calcular_percentual(proposta_campos)
            
            # ABA 5: ONBOARDING (3 campos importantes)
            onboarding_campos = [
                lead.suitability_oficial,
                lead.perfil_risco_final,
                lead.documentos_entregues,
            ]
            lead.onboarding_completude = self._calcular_percentual(onboarding_campos)
            
            # ABA 6: EXECUÇÃO (2 campos importantes)
            execucao_campos = [
                lead.valor_investido_atual,
                lead.distribuicao_portfolio,
            ]
            lead.execucao_completude = self._calcular_percentual(execucao_campos)
    
    def _calcular_percentual(self, campos):
        """
        Calcula percentual de campos preenchidos.
        
        Args:
            campos: Lista de valores de campos
            
        Returns:
            int: Percentual de 0 a 100
        """
        if not campos:
            return 0
        
        total = len(campos)
        preenchidos = 0
        
        for campo in campos:
            # Verifica se o campo está preenchido
            if campo:
                # Para Many2many, verifica se tem registros
                if hasattr(campo, '__iter__') and not isinstance(campo, str):
                    if len(campo) > 0:
                        preenchidos += 1
                else:
                    preenchidos += 1
        
        return int((preenchidos / total) * 100) if total > 0 else 0
    
    # ============================================================
    # VALIDAÇÕES DE CAMPOS OBRIGATÓRIOS POR ESTÁGIO
    # ============================================================
    
    @api.constrains('stage_id')
    def _check_required_fields_by_stage(self):
        """
        Valida se os campos obrigatórios foram preenchidos antes de avançar para o próximo estágio.
        Bloqueia a mudança de estágio se houver campos obrigatórios faltando.
        """
        for lead in self:
            if not lead.stage_id:
                continue
            
            seq = lead.stage_sequence or 0
            campos_faltantes = []
            
            # QUALIFICAÇÃO (seq >= 20): Valida campos da CAPTAÇÃO
            if seq >= 20:
                if not lead.patrimonio_aproximado:
                    campos_faltantes.append('Patrimônio Aproximado')
                if not lead.interesse_inicial:
                    campos_faltantes.append('Interesses Iniciais')
            
            # REUNIÃO (seq >= 30): Valida campos da QUALIFICAÇÃO
            if seq >= 30:
                if not lead.perfil_investidor:
                    campos_faltantes.append('Perfil do Investidor')
                if not lead.dor_principal:
                    campos_faltantes.append('Dor Principal')
                if not lead.objetivo_principal:
                    campos_faltantes.append('Objetivo Principal')
            
            # PROPOSTA (seq >= 40): Valida campos da REUNIÃO
            if seq >= 40:
                if not lead.data_reuniao:
                    campos_faltantes.append('Data da Reunião')
                if not lead.estrategias_discutidas:
                    campos_faltantes.append('Estratégias Discutidas')
            
            # ONBOARDING (seq >= 50): Valida campos da PROPOSTA
            if seq >= 50:
                if not lead.valor_proposta:
                    campos_faltantes.append('Valor da Proposta')
                if not lead.fee_gestao:
                    campos_faltantes.append('Fee de Gestão')
            
            # EXECUÇÃO (seq >= 60): Valida campos do ONBOARDING
            if seq >= 60:
                if not lead.suitability_oficial:
                    campos_faltantes.append('Suitability Oficial')
                if not lead.perfil_risco_final:
                    campos_faltantes.append('Perfil de Risco Final')
                if not lead.documentos_entregues:
                    campos_faltantes.append('Documentos Entregues')
            
            # Se houver campos faltantes, bloqueia a mudança
            if campos_faltantes:
                raise ValidationError(
                    f"❌ Não é possível avançar para '{lead.stage_id.name}'.\n\n"
                    f"Os seguintes campos obrigatórios precisam ser preenchidos:\n"
                    f"• " + "\n• ".join(campos_faltantes) +
                    f"\n\nPreencha os dados antes de avançar no funil."
                )
    
    # ============================================================
    # CÁLCULOS FINANCEIROS AUTOMÁTICOS
    # ============================================================
    
    @api.depends('valor_objetivo', 'prazo_objetivo', 'valor_proposta', 'fee_gestao')
    def _compute_calculos_financeiros(self):
        """
        Calcula automaticamente:
        1. Aporte mensal necessário para atingir objetivo
        2. Receita anual estimada do contrato
        
        A taxa de retorno é configurável em: Configurações → CRM → Wealth Management
        """
        # Busca a taxa configurada (padrão: 10% a.a.)
        taxa_anual = float(self.env['ir.config_parameter'].sudo().get_param(
            'crm_wealth.taxa_padrao', default=10.0
        ))
        
        for lead in self:
            # CÁLCULO 1: Aporte Mensal Necessário
            # Fórmula: PMT (Pagamento) usando juros compostos
            if lead.valor_objetivo and lead.prazo_objetivo and lead.prazo_objetivo > 0:
                fv = float(lead.valor_objetivo)  # Future Value (valor futuro)
                n_meses = lead.prazo_objetivo * 12  # Número de meses
                
                # Converte taxa anual para mensal: (1 + i_anual)^(1/12) - 1
                taxa_mensal = ((1 + taxa_anual / 100) ** (1/12)) - 1
                
                # Fórmula PMT: FV / [((1 + i)^n - 1) / i]
                if taxa_mensal > 0:
                    denominador = (((1 + taxa_mensal) ** n_meses) - 1) / taxa_mensal
                    if denominador > 0:
                        lead.aporte_mensal_necessario = fv / denominador
                    else:
                        lead.aporte_mensal_necessario = 0
                else:
                    # Sem juros, apenas divisão simples
                    lead.aporte_mensal_necessario = fv / n_meses
            else:
                lead.aporte_mensal_necessario = 0
            
            # CÁLCULO 2: Receita Anual Estimada
            # Fórmula: Valor da Proposta × (Fee % / 100)
            if lead.valor_proposta and lead.fee_gestao:
                lead.receita_anual_estimada = lead.valor_proposta * (lead.fee_gestao / 100)
            else:
                lead.receita_anual_estimada = 0
    
    # ============================================================
    # MÉTODOS COMPUTADOS PARA ABA RESUMO
    # ============================================================
    
    @api.depends('captacao_completude', 'qualificacao_completude', 'reuniao_completude',
                 'proposta_completude', 'onboarding_completude', 'execucao_completude')
    def _compute_score_qualificacao(self):
        """Calcula score de 0-100 baseado em completude, engajamento e potencial"""
        for lead in self:
            score = 0
            
            # Dados básicos (30 pontos)
            if lead.valor_investido_atual and lead.valor_investido_atual > 0:
                score += 10
            if lead.valor_objetivo and lead.valor_objetivo > 0:
                score += 10
            if lead.perfil_investidor:
                score += 10
            
            # Completude média (40 pontos)
            completudes = [
                lead.captacao_completude,
                lead.qualificacao_completude,
                lead.reuniao_completude,
                lead.proposta_completude,
                lead.onboarding_completude,
                lead.execucao_completude
            ]
            media_completude = sum(completudes) / len(completudes) if completudes else 0
            score += int(media_completude * 0.4)  # 40% do score
            
            # Potencial financeiro (30 pontos)
            if lead.receita_anual_estimada >= 50000:
                score += 30
            elif lead.receita_anual_estimada >= 30000:
                score += 20
            elif lead.receita_anual_estimada >= 10000:
                score += 10
            
            lead.score_qualificacao = min(score, 100)
    
    @api.depends('score_qualificacao')
    def _compute_lead_temperature(self):
        """Define temperatura do lead baseado no score"""
        for lead in self:
            if lead.score_qualificacao >= 70:
                lead.lead_temperature = 'hot'
            elif lead.score_qualificacao >= 40:
                lead.lead_temperature = 'warm'
            else:
                lead.lead_temperature = 'cold'
    
    @api.depends('create_date')
    def _compute_dias_pipeline(self):
        """Calcula quantos dias o lead está no pipeline"""
        from datetime import datetime
        for lead in self:
            if lead.create_date:
                delta = datetime.now() - lead.create_date
                lead.dias_em_pipeline = delta.days
            else:
                lead.dias_em_pipeline = 0
    
    @api.depends('captacao_completude', 'qualificacao_completude', 'reuniao_completude',
                 'proposta_completude', 'onboarding_completude', 'execucao_completude')
    def _compute_progresso_geral(self):
        """Calcula progresso geral como média das completudes"""
        for lead in self:
            completudes = [
                lead.captacao_completude,
                lead.qualificacao_completude,
                lead.reuniao_completude,
                lead.proposta_completude,
                lead.onboarding_completude,
                lead.execucao_completude
            ]
            lead.progresso_geral = sum(completudes) / len(completudes) if completudes else 0
    
    @api.depends('data_aniversario_cliente', 'data_aniversario_conjuge', 'stage_id',
                 'captacao_completude', 'qualificacao_completude', 'reuniao_completude')
    def _compute_alertas_resumo(self):
        """Gera alertas e lembretes importantes"""
        from datetime import date, timedelta
        
        for lead in self:
            alertas = []
            
            # Alertas de aniversário
            hoje = date.today()
            
            if lead.data_aniversario_cliente:
                # Ajustar para o próximo ano se já passou
                prox_aniv = lead.data_aniversario_cliente.replace(year=hoje.year)
                if prox_aniv < hoje:
                    prox_aniv = prox_aniv.replace(year=hoje.year + 1)
                
                dias = (prox_aniv - hoje).days
                if 0 < dias <= 30:
                    alertas.append(f'🎂 Aniversário do cliente em {dias} dias ({prox_aniv.strftime("%d/%m")})')
            
            if lead.data_aniversario_conjuge and lead.nome_conjuge:
                prox_aniv = lead.data_aniversario_conjuge.replace(year=hoje.year)
                if prox_aniv < hoje:
                    prox_aniv = prox_aniv.replace(year=hoje.year + 1)
                
                dias = (prox_aniv - hoje).days
                if 0 < dias <= 120:  # 4 meses antes
                    alertas.append(f'🎂 Aniversário de {lead.nome_conjuge} em {dias} dias ({prox_aniv.strftime("%d/%m")})')
            
            # Alertas de completude
            if lead.captacao_completude < 100 and lead.stage_sequence >= 10:
                alertas.append(f'💡 Completar Captação ({lead.captacao_completude}% concluído)')
            
            if lead.qualificacao_completude < 100 and lead.stage_sequence >= 20:
                alertas.append(f'💡 Completar Qualificação ({lead.qualificacao_completude}% concluído)')
            
            if lead.reuniao_completude < 100 and lead.stage_sequence >= 30:
                alertas.append(f'💡 Completar Análise de Perfil ({lead.reuniao_completude}% concluído)')
            
            # Montar HTML
            if alertas:
                html = '<ul class="o_list_view">'
                for alerta in alertas:
                    html += f'<li>{alerta}</li>'
                html += '</ul>'
                lead.alertas_resumo = html
            else:
                lead.alertas_resumo = '<p class="text-muted">🟢 Nenhum alerta no momento</p>'
    
    @api.depends('data_aniversario_cliente', 'estado_civil', 'nome_conjuge',
                 'quantidade_filhos', 'nomes_filhos', 'time_coracao', 'hobbies')
    def _compute_perfil_pessoal_resumo(self):
        """Gera card visual com informações pessoais do cliente"""
        from datetime import date
        
        for lead in self:
            linhas = []
            
            # Aniversário do cliente
            if lead.data_aniversario_cliente:
                hoje = date.today()
                prox_aniv = lead.data_aniversario_cliente.replace(year=hoje.year)
                if prox_aniv < hoje:
                    prox_aniv = prox_aniv.replace(year=hoje.year + 1)
                dias = (prox_aniv - hoje).days
                
                if dias <= 30:
                    linhas.append(f'🎂 <strong>Aniversário:</strong> {lead.data_aniversario_cliente.strftime("%d/%m")} (<span class="text-danger">em {dias} dias!</span>)')
                else:
                    linhas.append(f'🎂 <strong>Aniversário:</strong> {lead.data_aniversario_cliente.strftime("%d/%m")} (em {dias} dias)')
            
            # Estado civil e cônjuge
            if lead.estado_civil == 'casado' and lead.nome_conjuge:
                conjuge_info = f'💑 <strong>Casado(a) com:</strong> {lead.nome_conjuge}'
                
                if lead.data_aniversario_conjuge:
                    hoje = date.today()
                    prox_aniv = lead.data_aniversario_conjuge.replace(year=hoje.year)
                    if prox_aniv < hoje:
                        prox_aniv = prox_aniv.replace(year=hoje.year + 1)
                    dias = (prox_aniv - hoje).days
                    conjuge_info += f' · Aniv: {lead.data_aniversario_conjuge.strftime("%d/%m")} (em {dias} dias)'
                
                linhas.append(conjuge_info)
            elif lead.estado_civil:
                estado_dict = dict(lead._fields['estado_civil'].selection)
                linhas.append(f'💑 <strong>Estado Civil:</strong> {estado_dict.get(lead.estado_civil)}')
            
            # Filhos
            if lead.quantidade_filhos > 0:
                if lead.nomes_filhos:
                    linhas.append(f'👶 <strong>{lead.quantidade_filhos} Filhos:</strong> {lead.nomes_filhos}')
                else:
                    linhas.append(f'👶 <strong>Filhos:</strong> {lead.quantidade_filhos}')
            
            # Time
            if lead.time_coracao:
                linhas.append(f'⚽ <strong>Time:</strong> {lead.time_coracao}')
            
            # Hobbies
            if lead.hobbies:
                linhas.append(f'🎯 <strong>Hobbies:</strong> {lead.hobbies}')
            
            if linhas:
                lead.perfil_pessoal_resumo = '<br/>'.join(linhas)
            else:
                lead.perfil_pessoal_resumo = '<p class="text-muted">Nenhuma informação pessoal cadastrada ainda.</p>'

    # ============================================================
    # MÉTODOS PARA SLA E RASTREAMENTO DE TEMPO
    # ============================================================
    
    @api.depends('stage_date')
    def _compute_days_in_stage(self):
        """Calcula quantos dias o lead está no estágio atual"""
        from datetime import datetime
        
        for lead in self:
            if lead.stage_date:
                delta = datetime.now() - fields.Datetime.from_string(str(lead.stage_date))
                lead.days_in_current_stage = delta.days
            else:
                lead.days_in_current_stage = 0
    
    @api.depends('days_in_current_stage', 'stage_id')
    def _compute_sla_status(self):
        """Determina o status do SLA baseado no estágio e configurações"""
        ICP = self.env['ir.config_parameter'].sudo()
        
        for lead in self:
            if not lead.stage_id or not lead.days_in_current_stage:
                lead.sla_status = 'ok'
                continue
            
            # Busca o SLA configurado para o estágio atual
            stage_name = lead.stage_id.name.lower()
            sla_limit = 999  # Default alto
            
            if 'captação' in stage_name or 'capta' in stage_name:
                sla_limit = int(ICP.get_param('crm_wealth.sla_captacao', 7))
            elif 'qualificação' in stage_name or 'qualifica' in stage_name:
                sla_limit = int(ICP.get_param('crm_wealth.sla_qualificacao', 5))
            elif 'reunião' in stage_name or 'reuniao' in stage_name:
                sla_limit = int(ICP.get_param('crm_wealth.sla_reuniao', 3))
            elif 'proposta' in stage_name:
                sla_limit = int(ICP.get_param('crm_wealth.sla_proposta', 5))
            elif 'onboarding' in stage_name:
                sla_limit = int(ICP.get_param('crm_wealth.sla_onboarding', 15))
            
            # Determina o status
            days = lead.days_in_current_stage
            if days >= sla_limit:
                lead.sla_status = 'exceeded'
            elif days >= (sla_limit * 0.8):  # 80% do limite
                lead.sla_status = 'warning'
            else:
                lead.sla_status = 'ok'
    
    def write(self, vals):
        """Sobrescreve write para atualizar stage_date quando mudar de estágio"""
        # Se mudou o estágio, atualiza a data
        if 'stage_id' in vals:
            vals['stage_date'] = fields.Datetime.now()
        
        return super(CrmLead, self).write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescreve create para setar stage_date na criação"""
        for vals in vals_list:
            if 'stage_date' not in vals:
                vals['stage_date'] = fields.Datetime.now()
        
        return super(CrmLead, self).create(vals_list)
    
    # ============================================================
    # MÉTODOS PARA AUTOMATED ACTIONS (SLA)
    # ============================================================
    
    def action_check_sla_captacao(self):
        """Verifica SLA de leads em Captação - Chamado por cron"""
        ICP = self.env['ir.config_parameter'].sudo()
        
        # Verifica se SLAs estão habilitados
        if not ICP.get_param('crm_wealth.sla_enabled', True):
            return
        
        sla_days = int(ICP.get_param('crm_wealth.sla_captacao', 7))
        limit_date = fields.Datetime.now() - timedelta(days=sla_days)
        
        # Busca leads em Captação que estão há mais tempo que o SLA
        leads = self.search([
            ('stage_id.name', 'ilike', 'captação'),
            ('stage_date', '<=', limit_date),
            ('active', '=', True)
        ])
        
        for lead in leads:
            # Verifica se já não existe atividade similar aberta
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
                ('summary', 'ilike', 'SLA: Captação'),
                ('state', '!=', 'done')
            ], limit=1)
            
            if not existing:
                # Cria atividade
                lead.activity_schedule(
                    'mail.mail_activity_data_call',
                    summary=f'🔥 SLA: Lead há {lead.days_in_current_stage} dias em Captação',
                    note='⚠️ Este lead está parado há mais de {} dias em Captação. Agende uma ligação de qualificação!'.format(sla_days),
                    user_id=lead.user_id.id or self.env.user.id,
                    date_deadline=fields.Date.today()
                )
                
                # Notificação
                lead.message_post(
                    body=f'⚠️ <strong>Alerta de SLA:</strong> Este lead está há {lead.days_in_current_stage} dias em Captação sem progresso.',
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
    
    def action_check_sla_proposta(self):
        """Verifica SLA de propostas sem resposta - Chamado por cron"""
        ICP = self.env['ir.config_parameter'].sudo()
        
        if not ICP.get_param('crm_wealth.sla_enabled', True):
            return
        
        sla_days = int(ICP.get_param('crm_wealth.sla_proposta', 5))
        limit_date = fields.Datetime.now() - timedelta(days=sla_days)
        
        leads = self.search([
            ('stage_id.name', 'ilike', 'proposta'),
            ('stage_date', '<=', limit_date),
            ('active', '=', True)
        ])
        
        for lead in leads:
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
                ('summary', 'ilike', 'SLA: Proposta'),
                ('state', '!=', 'done')
            ], limit=1)
            
            if not existing:
                lead.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=f'📞 SLA: Proposta sem resposta há {lead.days_in_current_stage} dias',
                    note='🔔 A proposta foi enviada há {} dias sem retorno. Faça follow-up com o cliente!'.format(sla_days),
                    user_id=lead.user_id.id or self.env.user.id,
                    date_deadline=fields.Date.today()
                )
                
                lead.message_post(
                    body=f'🔔 <strong>Follow-up necessário:</strong> Proposta enviada há {lead.days_in_current_stage} dias sem resposta.',
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
    
    def action_check_sla_reuniao(self):
        """Verifica SLA de reuniões sem follow-up - Chamado por cron"""
        ICP = self.env['ir.config_parameter'].sudo()
        
        if not ICP.get_param('crm_wealth.sla_enabled', True):
            return
        
        sla_days = int(ICP.get_param('crm_wealth.sla_reuniao', 3))
        limit_date = fields.Datetime.now() - timedelta(days=sla_days)
        
        # Busca leads que tiveram reunião mas não avançaram
        leads = self.search([
            ('stage_id.name', 'ilike', 'reunião'),
            ('data_reuniao', '!=', False),
            ('stage_date', '<=', limit_date),
            ('active', '=', True)
        ])
        
        for lead in leads:
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
                ('summary', 'ilike', 'SLA: Reunião'),
                ('state', '!=', 'done')
            ], limit=1)
            
            if not existing:
                lead.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=f'📧 SLA: Reunião sem follow-up há {lead.days_in_current_stage} dias',
                    note='⏰ A reunião aconteceu há {} dias sem follow-up. Envie a proposta ou faça contato!'.format(sla_days),
                    user_id=lead.user_id.id or self.env.user.id,
                    date_deadline=fields.Date.today()
                )
                
                lead.message_post(
                    body=f'⏰ <strong>Follow-up pendente:</strong> Reunião realizada há {lead.days_in_current_stage} dias sem ação.',
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )


# ============================================================
# MODELOS AUXILIARES
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
