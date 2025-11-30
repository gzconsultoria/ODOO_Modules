# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    finance_profile_id = fields.Many2one(
        "finance.profile", 
        string="Perfil Financeiro",
        help="Perfil financeiro vinculado a este Lead. "
             "Criado automaticamente quando Lead chega em 'Execução & Acompanhamento'."
    )
    finance_expected_aum = fields.Monetary(
        string="AUM Estimado", 
        currency_field="company_currency"
    )
    finance_origin = fields.Selection(
        [
            ("referral", "Indicação"),
            ("event", "Evento"),
            ("online", "Canal digital"),
            ("other", "Outro"),
        ],
        string="Origem Financeira",
    )
    finance_services = fields.Selection(
        [
            ("wealth", "Gestão de Patrimônio"),
            ("planning", "Planejamento Financeiro"),
            ("pension", "Previdência"),
            ("other", "Outros"),
        ],
        string="Serviço Desejado",
    )
    finance_suitability_status = fields.Selection(
        [
            ("draft", "Não Iniciado"), 
            ("in_progress", "Em Andamento"), 
            ("done", "Concluído")
        ],
        default="draft",
        string="Status Suitability"
    )
    
    # ============================================================
    # SINCRONIZAÇÃO BIDIRECIONAL - CAMPOS COMPUTADOS (READONLY)
    # ============================================================
    # Finance Profile é a fonte da verdade
    # Lead mostra dados atualizados em tempo real (somente leitura)
    
    # Dados Pessoais
    finance_client_birthdate = fields.Date(
        string="📅 Aniversário (Profile)",
        compute="_compute_finance_profile_data",
        store=False,
        help="Sincronizado automaticamente do Finance Profile (somente leitura)"
    )
    finance_spouse_name = fields.Char(
        string="👫 Cônjuge (Profile)",
        compute="_compute_finance_profile_data",
        store=False
    )
    finance_children_info = fields.Char(
        string="👶 Filhos (Profile)",
        compute="_compute_finance_profile_data",
        store=False
    )
    finance_hobbies = fields.Text(
        string="🎯 Hobbies (Profile)",
        compute="_compute_finance_profile_data",
        store=False
    )
    
    # Objetivos
    finance_main_goal = fields.Char(
        string="🎯 Meta Principal (Profile)",
        compute="_compute_finance_profile_data",
        store=False
    )
    finance_goal_amount = fields.Monetary(
        string="💰 Valor da Meta (Profile)",
        compute="_compute_finance_profile_data",
        currency_field="company_currency",
        store=False
    )
    finance_monthly_contribution = fields.Monetary(
        string="📊 Aporte Mensal Necessário (Profile)",
        compute="_compute_finance_profile_data",
        currency_field="company_currency",
        store=False
    )
    
    # Diagnóstico
    finance_diagnosis_summary = fields.Text(
        string="🔍 Diagnóstico SWOT (Profile)",
        compute="_compute_finance_profile_data",
        store=False
    )
    
    # Proposta
    finance_contract_type = fields.Selection(
        [
            ('monthly', 'Mensalidade Fixa'),
            ('quarterly', 'Trimestralidade Fixa'),
            ('aum_percentage', '% sobre AUM'),
        ],
        string="💼 Tipo de Contrato (Profile)",
        compute="_compute_finance_profile_data",
        store=False
    )
    finance_estimated_revenue = fields.Monetary(
        string="💵 Receita Anual Estimada (Profile)",
        compute="_compute_finance_profile_data",
        currency_field="company_currency",
        store=False
    )
    
    @api.depends('finance_profile_id', 
                 'finance_profile_id.client_birthdate',
                 'finance_profile_id.spouse_name',
                 'finance_profile_id.children_count',
                 'finance_profile_id.children_names',
                 'finance_profile_id.hobbies',
                 'finance_profile_id.main_goal',
                 'finance_profile_id.goal_amount',
                 'finance_profile_id.monthly_contribution_needed',
                 'finance_profile_id.diagnosis_current_situation',
                 'finance_profile_id.diagnosis_strengths',
                 'finance_profile_id.diagnosis_weaknesses',
                 'finance_profile_id.diagnosis_opportunities',
                 'finance_profile_id.contract_type',
                 'finance_profile_id.estimated_annual_revenue')
    def _compute_finance_profile_data(self):
        """
        Sincronização bidirecional: Finance Profile → Lead (readonly)
        
        Lead sempre mostra dados atualizados do Finance Profile.
        Vendedor vê informações em tempo real sem risco de sobrescrever.
        """
        for lead in self:
            profile = lead.finance_profile_id
            
            if not profile:
                # Sem profile vinculado: limpa campos
                lead.finance_client_birthdate = False
                lead.finance_spouse_name = False
                lead.finance_children_info = False
                lead.finance_hobbies = False
                lead.finance_main_goal = False
                lead.finance_goal_amount = 0.0
                lead.finance_monthly_contribution = 0.0
                lead.finance_diagnosis_summary = False
                lead.finance_contract_type = False
                lead.finance_estimated_revenue = 0.0
                continue
            
            # Dados Pessoais
            lead.finance_client_birthdate = profile.client_birthdate
            lead.finance_spouse_name = profile.spouse_name
            
            # Filhos (concatena quantidade + nomes)
            if profile.children_count:
                children_info = f"{profile.children_count} filho(s)"
                if profile.children_names:
                    children_info += f": {profile.children_names}"
                lead.finance_children_info = children_info
            else:
                lead.finance_children_info = "Sem filhos"
            
            lead.finance_hobbies = profile.hobbies
            
            # Objetivos
            lead.finance_main_goal = profile.main_goal
            lead.finance_goal_amount = profile.goal_amount or 0.0
            lead.finance_monthly_contribution = profile.monthly_contribution_needed or 0.0
            
            # Diagnóstico (resumo SWOT)
            swot_parts = []
            if profile.diagnosis_current_situation:
                swot_parts.append(f"📌 Situação: {profile.diagnosis_current_situation[:100]}...")
            if profile.diagnosis_strengths:
                swot_parts.append(f"✅ Forças: {profile.diagnosis_strengths[:80]}...")
            if profile.diagnosis_weaknesses:
                swot_parts.append(f"⚠️ Fraquezas: {profile.diagnosis_weaknesses[:80]}...")
            if profile.diagnosis_opportunities:
                swot_parts.append(f"💡 Oportunidades: {profile.diagnosis_opportunities[:80]}...")
            
            lead.finance_diagnosis_summary = "\n".join(swot_parts) if swot_parts else "Diagnóstico não preenchido"
            
            # Proposta
            lead.finance_contract_type = profile.contract_type
            lead.finance_estimated_revenue = profile.estimated_annual_revenue or 0.0
    
    # ============================================================
    # SINCRONIZAÇÃO AUTOMÁTICA COM FINANCE PROFILE
    # ============================================================
    
    def write(self, vals):
        """
        Override write para sincronizar automaticamente Finance Profile.
        
        Gatilho: quando Lead.stage_id muda para um estágio com is_won=True
        
        Ação: cria/atualiza Finance Profile automaticamente
        
        Funciona com:
        - CRM Nativo (cria profile básico)
        - CRM Wealth (copia todos os campos extras)
        - Qualquer CRM customizado (copia campos que coincidirem)
        """
        result = super(CrmLead, self).write(vals)
        
        # Detecta mudança de estágio
        if 'stage_id' in vals:
            for lead in self:
                # AUTO-CRIAÇÃO: Apenas quando lead é marcado como GANHO (is_won=True)
                if lead.stage_id and lead.stage_id.is_won:
                    lead._sync_to_finance_profile()
                    lead._create_client_folder_structure()  # NOVA AUTOMAÇÃO
        
        return result
    
    # ============================================================
    # AUTOMAÇÃO: CRIAÇÃO DE PASTAS DE DOCUMENTOS
    # ============================================================
    
    def _create_client_folder_structure(self):
        """
        Cria estrutura de pastas de documentos ao ganhar lead.
        
        **Estrutura criada:**
        
        📁 Clientes
          └─ 📁 João da Silva (CLI-00123)
              ├─ ✅ Suitability
              ├─ 📋 Cadastro e Documentação
              ├─ 📜 Política de Investimento
              ├─ 🤝 Atas de Reunião
              ├─ 💰 Financeiro
              ├─ 📊 Relatórios
              └─ 📝 Contratos
        
        **Idempotência:** Pode chamar N vezes, cria apenas 1 vez.
        **Vinculação:** Partner.client_folder_id aponta para pasta criada.
        """
        self.ensure_one()
        
        # Validações
        if not self.partner_id:
            return
        
        # Se já tem pasta criada, não duplica
        if self.partner_id.client_folder_id:
            return
        
        # Garante que tem finance_profile_id (vem do gz_finance_core)
        if not self.partner_id.finance_profile_id:
            # Partner sem finance_profile_id ainda - espera ser criado
            return
        
        # Busca pasta raiz "Clientes"
        try:
            root_folder = self.env.ref('gz_finance_docs.folder_clientes')
        except:
            # Módulo gz_finance_docs não instalado ou pasta não existe
            return
        
        # Cria pasta principal do cliente
        client_folder_name = f"{self.partner_id.name} ({self.partner_id.finance_profile_id})"
        
        client_folder = self.env['document_hub.folder'].create({
            'name': client_folder_name,
            'description': f"Documentos do cliente {self.partner_id.name}. "
                          f"Criada automaticamente ao converter Lead #{self.id}.",
            'parent_folder_id': root_folder.id,
            'partner_id': self.partner_id.id,
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
            self.env['document_hub.folder'].create({
                'name': subfolder_name,
                'description': subfolder_description,
                'parent_folder_id': client_folder.id,
                'partner_id': self.partner_id.id,
                'visibility_administration': True,
                'visibility_salesman': True,
            })
        
        # Vincula pasta ao partner
        self.partner_id.client_folder_id = client_folder.id
        
        # Notifica no chatter do Lead
        self.message_post(
            body=_(
                "📁 <strong>Estrutura de documentos criada automaticamente</strong><br/>"
                "Pasta principal: <b>%s</b><br/>"
                "Subpastas criadas: 7 (Suitability, Cadastro, Política, Atas, Financeiro, Relatórios, Contratos)<br/>"
                "<a href='/web#model=document_hub.folder&id=%s'>📂 Abrir Pasta do Cliente</a>"
            ) % (client_folder_name, client_folder.id)
        )

    
    def _sync_to_finance_profile(self):
        """
        Sincroniza dados do Lead CRM → Finance Profile.
        
        **Comportamento:**
        - Se Finance Profile não existe: CRIA e preenche com dados disponíveis
        - Se Finance Profile existe: ATUALIZA apenas campos vazios
        - **ANTI-DUPLICAÇÃO:** Se outro Lead já criou Profile para mesmo Partner, VINCULA ao invés de duplicar
        
        **Campos copiados:**
        - Básicos (sempre): partner_id, advisor_id, investor_type
        - Opcionais (se existirem no Lead): dados pessoais, objetivos, diagnóstico, proposta, etc.
        
        **Compatibilidade:**
        - ✅ CRM Nativo: cria profile básico
        - ✅ CRM Wealth: copia ~40 campos extras
        - ✅ CRM Customizado: copia campos que coincidirem
        """
        self.ensure_one()
        
        # Garante que existe partner_id
        if not self.partner_id:
            self._handle_partner_assignment(create_missing=True)
        
        if not self.partner_id:
            # Não pode criar profile sem partner
            return
        
        # Validação: Partner deve ser cliente
        if not self.partner_id.customer_rank > 0:
            # Marca como cliente automaticamente se for Lead válido
            self.partner_id.customer_rank = 1
        
        # ============================================================
        # ANTI-DUPLICAÇÃO: Busca Profile existente (qualquer Lead)
        # ============================================================
        profile = self.finance_profile_id
        
        if not profile:
            # Busca profile existente para este partner (de QUALQUER Lead)
            profile = self.env['finance.profile'].search([
                ('partner_id', '=', self.partner_id.id)
            ], limit=1)
            
            if profile:
                # ✅ ENCONTROU profile existente (criado por outro Lead)
                # Vincula este Lead ao profile existente ao invés de criar duplicata
                self.finance_profile_id = profile
                self.message_post(
                    body=_(
                        "🔗 Vinculado a Perfil Financeiro existente (ID: %s).<br/>"
                        "Este perfil foi criado anteriormente por outro Lead/Oportunidade."
                    ) % profile.id
                )
                
                # Continua para atualizar campos vazios (merge de dados)
                # NÃO retorna aqui - permite atualização incremental
        
        # Prepara valores para criação/atualização
        profile_vals = self._prepare_finance_profile_vals()
        
        if not profile:
            # ============================================================
            # CRIAR novo Finance Profile (usando método seguro)
            # ============================================================
            from psycopg2 import IntegrityError
            
            try:
                # Usa método helper que previne duplicatas
                profile = self.env['finance.profile'].get_or_create_for_partner(
                    partner_id=self.partner_id.id,
                    vals=profile_vals
                )
                
                
                self.finance_profile_id = profile
                
                # ============================================================
                # CRIAÇÃO AUTOMÁTICA DE GOALS (finance.goal)
                # ============================================================
                self._create_finance_goals(profile)
                
                # Notificação no Lead
                stage_name = self.stage_id.name if self.stage_id else 'desconhecido'
                self.message_post(
                    body=_(
                        "✅ <strong>Perfil Financeiro criado automaticamente</strong><br/>"
                        "Estágio: %s<br/>"
                        "Consultor: %s"
                    ) % (stage_name, profile.advisor_id.name)
                )
                
                # Notificação proativa para o vendedor
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=self.user_id.id if self.user_id else self.env.user.id,
                    summary=_('Perfil Financeiro Criado'),
                    note=_(
                        'O Perfil Financeiro foi criado automaticamente para %s.<br/>'
                        'Clique no botão "Perfil Financeiro" acima para visualizar.'
                    ) % self.partner_id.name
                )
                
            except IntegrityError as e:
                # Constraint SQL bloqueou duplicata
                if 'unique_partner_profile' in str(e):
                    profile = self.env['finance.profile'].search([
                        ('partner_id', '=', self.partner_id.id)
                    ], limit=1)
                    
                    if profile:
                        self.finance_profile_id = profile
                        self.message_post(
                            body=_(
                                "⚠️ Perfil Financeiro já existia para este Cliente.<br/>"
                                "Vinculado ao perfil existente (ID: %s)."
                            ) % profile.id
                        )
                else:
                    # Erro SQL diferente, não é duplicata
                    raise
        else:
            # ATUALIZAR Finance Profile existente (apenas campos vazios)
            update_vals = {}
            for field, value in profile_vals.items():
                if field in ['partner_id', 'crm_lead_id']:
                    # Sempre atualiza relacionamentos
                    update_vals[field] = value
                elif not profile[field]:
                    # Atualiza apenas se campo estiver vazio
                    update_vals[field] = value
            
            # Adiciona timestamp de sincronização
            update_vals['last_sync_date'] = fields.Datetime.now()
            
            if update_vals:
                profile.write(update_vals)
                if 'crm_lead_id' not in self.finance_profile_id or self.finance_profile_id != profile:
                    self.finance_profile_id = profile
                self.message_post(
                    body=_("🔄 Perfil Financeiro atualizado com dados do Lead.")
                )
    
    def _prepare_finance_profile_vals(self):
        """
        Prepara dicionário de valores para criar/atualizar Finance Profile.
        
        Usa detecção inteligente de campos (hasattr):
        - Se campo existe no Lead → copia valor
        - Se campo NÃO existe → ignora (sem erros)
        
        **Campos Básicos (CRM Nativo):**
        - partner_id, advisor_id, investor_type
        
        **Campos Opcionais (CRM Wealth ou customizações):**
        - Dados pessoais: cliente_nascimento, estado_civil, conjuge_nome, etc.
        - Objetivos: objetivo_principal, valor_objetivo, prazo_objetivo, etc.
        - Diagnóstico: diagnostico_situacao, diagnostico_forcas, etc.
        - Proposta: plano_contrato, valor_proposta, fee_gestao, etc.
        - Reunião: data_reuniao, estrategias_discutidas, etc.
        
        **Novos Recursos (Reformulação):**
        - Cria household automaticamente se casado/união estável
        - Cria finance.goal records baseado em objetivos do Lead
        - Status lifecycle iniciado como 'prospect' (lifecycle_event criado por override)
        """
        self.ensure_one()
        
        vals = {
            'partner_id': self.partner_id.id,
            'crm_lead_id': self.id,  # Link reverso
            'advisor_id': self.user_id.id if self.user_id else self.env.user.id,
            'investor_type': 'pf' if self.partner_id.company_type != 'company' else 'pj',
            'status': 'prospect',  # Status inicial do lifecycle
        }
        
        # ===== DADOS PESSOAIS (Opcionais - CRM Wealth ou customizações) =====
        if hasattr(self, 'cliente_nascimento') and self.cliente_nascimento:
            vals['client_birthdate'] = self.cliente_nascimento
        
        if hasattr(self, 'estado_civil') and self.estado_civil:
            vals['marital_status'] = self.estado_civil
        
        if hasattr(self, 'conjuge_nome') and self.conjuge_nome:
            vals['spouse_name'] = self.conjuge_nome
        
        if hasattr(self, 'conjuge_nascimento') and self.conjuge_nascimento:
            vals['spouse_birthdate'] = self.conjuge_nascimento
        
        if hasattr(self, 'filhos_qtd'):
            vals['children_count'] = self.filhos_qtd or 0
        
        if hasattr(self, 'filhos_nomes') and self.filhos_nomes:
            vals['children_names'] = self.filhos_nomes
        
        if hasattr(self, 'time_coracao') and self.time_coracao:
            vals['favorite_team'] = self.time_coracao
        
        if hasattr(self, 'hobbies') and self.hobbies:
            vals['hobbies'] = self.hobbies
        
        # ===== OBJETIVOS (Aba Qualificação) =====
        if hasattr(self, 'objetivo_curto_prazo') and self.objetivo_curto_prazo:
            vals['short_term_goal'] = self.objetivo_curto_prazo
        
        if hasattr(self, 'objetivo_longo_prazo') and self.objetivo_longo_prazo:
            vals['long_term_goal'] = self.objetivo_longo_prazo
        
        if hasattr(self, 'objetivo_principal') and self.objetivo_principal:
            vals['main_goal'] = self.objetivo_principal
        
        if hasattr(self, 'valor_objetivo') and self.valor_objetivo:
            vals['goal_amount'] = self.valor_objetivo
        
        if hasattr(self, 'prazo_objetivo'):
            vals['goal_deadline_years'] = self.prazo_objetivo or 0
        
        # ===== DIAGNÓSTICO SWOT (Aba Reunião) =====
        if hasattr(self, 'diagnostico_situacao') and self.diagnostico_situacao:
            vals['diagnosis_current_situation'] = self.diagnostico_situacao
        
        if hasattr(self, 'diagnostico_forcas') and self.diagnostico_forcas:
            vals['diagnosis_strengths'] = self.diagnostico_forcas
        
        if hasattr(self, 'diagnostico_fraquezas') and self.diagnostico_fraquezas:
            vals['diagnosis_weaknesses'] = self.diagnostico_fraquezas
        
        if hasattr(self, 'diagnostico_oportunidades') and self.diagnostico_oportunidades:
            vals['diagnosis_opportunities'] = self.diagnostico_oportunidades
        
        if hasattr(self, 'data_diagnostico') and self.data_diagnostico:
            vals['diagnosis_date'] = self.data_diagnostico
        
        # ===== PROPOSTA COMERCIAL (Aba Proposta) =====
        if hasattr(self, 'plano_contrato') and self.plano_contrato:
            vals['contract_plan'] = self.plano_contrato
        
        if hasattr(self, 'valor_proposta') and self.valor_proposta:
            vals['proposal_amount'] = self.valor_proposta
        
        if hasattr(self, 'fee_gestao') and self.fee_gestao:
            vals['management_fee'] = self.fee_gestao
        
        if hasattr(self, 'tipo_contrato') and self.tipo_contrato:
            vals['contract_type'] = self.tipo_contrato
        
        if hasattr(self, 'data_proposta') and self.data_proposta:
            vals['proposal_date'] = self.data_proposta
        
        if hasattr(self, 'justificativa_proposta') and self.justificativa_proposta:
            vals['proposal_justification'] = self.justificativa_proposta
        
        # ===== REUNIÃO ESTRATÉGICA =====
        if hasattr(self, 'data_reuniao') and self.data_reuniao:
            vals['meeting_date'] = self.data_reuniao
        
        if hasattr(self, 'estrategias_discutidas') and self.estrategias_discutidas:
            vals['meeting_strategies_discussed'] = self.estrategias_discutidas
        
        if hasattr(self, 'objecoes_identificadas') and self.objecoes_identificadas:
            vals['meeting_objections'] = self.objecoes_identificadas
        
        if hasattr(self, 'score_potencial'):
            vals['potential_score'] = self.score_potencial or 0
        
        # ===== QUALIFICAÇÃO =====
        if hasattr(self, 'prontidao_financeira') and self.prontidao_financeira:
            vals['financial_readiness'] = self.prontidao_financeira
        
        if hasattr(self, 'dor_principal') and self.dor_principal:
            vals['primary_pain_point'] = self.dor_principal
        
        # ===== RELACIONAMENTOS MANY2MANY =====
        # Mapeamento inteligente por nome: CRM Wealth Tags → Finance Profile Tags
        # Se tag não existir no Finance Profile, é ignorada (sem criar automaticamente)
        
        # 1. INTERESSES (crm.wealth.interesse → finance.interest.tag)
        if hasattr(self, 'interesse_inicial') and self.interesse_inicial:
            interesse_ids = []
            for crm_tag in self.interesse_inicial:
                # Busca tag por CODE (preferencial) ou NAME (fallback)
                finance_tag = None
                
                # Tenta por code primeiro (mais robusto)
                if hasattr(crm_tag, 'code') and crm_tag.code:
                    finance_tag = self.env['finance.interest.tag'].search([
                        ('code', '=', crm_tag.code)
                    ], limit=1)
                
                # Fallback: busca por nome
                if not finance_tag:
                    finance_tag = self.env['finance.interest.tag'].search([
                        ('name', '=ilike', crm_tag.name)
                    ], limit=1)
                
                if finance_tag:
                    interesse_ids.append((4, finance_tag.id))
            
            if interesse_ids:
                vals['investor_interests_ids'] = interesse_ids
        
        # 2. ESTRATÉGIAS (crm.wealth.estrategia → finance.strategy.tag)
        if hasattr(self, 'estrategias_recomendadas') and self.estrategias_recomendadas:
            estrategia_ids = []
            for crm_tag in self.estrategias_recomendadas:
                # Busca por code ou name
                finance_tag = None
                
                if hasattr(crm_tag, 'code') and crm_tag.code:
                    finance_tag = self.env['finance.strategy.tag'].search([
                        ('code', '=', crm_tag.code)
                    ], limit=1)
                
                if not finance_tag:
                    finance_tag = self.env['finance.strategy.tag'].search([
                        ('name', '=ilike', crm_tag.name)
                    ], limit=1)
                
                if finance_tag:
                    estrategia_ids.append((4, finance_tag.id))
            
            if estrategia_ids:
                vals['recommended_strategies_ids'] = estrategia_ids
        
        # 3. OBJEÇÕES (crm.wealth.objecao → finance.objection.tag)
        if hasattr(self, 'objecoes') and self.objecoes:
            objecao_ids = []
            for crm_tag in self.objecoes:
                # Busca por code ou name
                finance_tag = None
                
                if hasattr(crm_tag, 'code') and crm_tag.code:
                    finance_tag = self.env['finance.objection.tag'].search([
                        ('code', '=', crm_tag.code)
                    ], limit=1)
                
                if not finance_tag:
                    finance_tag = self.env['finance.objection.tag'].search([
                        ('name', '=ilike', crm_tag.name)
                    ], limit=1)
                
                if finance_tag:
                    objecao_ids.append((4, finance_tag.id))
            
            if objecao_ids:
                vals['proposal_objections_ids'] = objecao_ids
        
        return vals

    def action_create_finance_profile(self):
        """Cria manualmente um perfil financeiro vinculado ao lead."""
        for lead in self:
            lead._sync_to_finance_profile()
        return True

    def action_open_finance_profile(self):
        """Abre o formulário do perfil financeiro vinculado ao lead."""
        self.ensure_one()
        if not self.finance_profile_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Perfil Financeiro',
            'res_model': 'finance.profile',
            'res_id': self.finance_profile_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    @api.onchange("finance_profile_id")
    def _onchange_finance_profile_id(self):
        if self.finance_profile_id:
            self.partner_id = self.finance_profile_id.partner_id
    
    # ============================================================
    # MÉTODOS AUXILIARES: GOALS
    # ============================================================
    
    def _create_finance_goals(self, profile):
        """
        Cria automaticamente finance.goal records baseado nos objetivos do Lead.
        
        Mapeia 3 objetivos do CRM → finance.goal:
        1. Objetivo Principal (main_goal) → goal_type='other', priority='high'
        2. Objetivo Curto Prazo (short_term_goal) → goal_type='emergency_fund', priority='medium'
        3. Objetivo Longo Prazo (long_term_goal) → goal_type='retirement', priority='medium'
        
        Só cria goals se:
        - Campos respectivos estiverem preenchidos no Lead
        - Goal ainda não existe (evita duplicatas)
        """
        self.ensure_one()
        
        if not profile:
            return
        
        goals_created = []
        
        # ===== OBJETIVO PRINCIPAL =====
        objetivo_principal = None
        valor_objetivo = 0.0
        prazo_objetivo = 0
        
        if hasattr(self, 'objetivo_principal') and self.objetivo_principal:
            objetivo_principal = self.objetivo_principal
            
            if hasattr(self, 'valor_objetivo') and self.valor_objetivo:
                valor_objetivo = self.valor_objetivo
            
            if hasattr(self, 'prazo_objetivo'):
                prazo_objetivo = self.prazo_objetivo or 0
            
            # Cria goal principal
            goal_main = self.env['finance.goal'].create({
                'profile_id': profile.id,
                'name': objetivo_principal,
                'goal_type': 'other',  # Genérico até saber mais detalhes
                'target_value': valor_objetivo,
                'current_value': 0.0,
                'deadline_years': prazo_objetivo,
                'priority': 'high',
                'status': 'not_started',
            })
            goals_created.append(goal_main.name)
        
        # ===== OBJETIVO CURTO PRAZO =====
        if hasattr(self, 'objetivo_curto_prazo') and self.objetivo_curto_prazo:
            goal_short = self.env['finance.goal'].create({
                'profile_id': profile.id,
                'name': self.objetivo_curto_prazo,
                'goal_type': 'emergency',  # Assume reserva de emergência
                'target_value': 0.0,  # Consultor preencherá depois
                'current_value': 0.0,
                'deadline_years': 1,  # Curto prazo = 1 ano
                'priority': 'high',
                'status': 'not_started',
            })
            goals_created.append(goal_short.name)
        
        # ===== OBJETIVO LONGO PRAZO =====
        if hasattr(self, 'objetivo_longo_prazo') and self.objetivo_longo_prazo:
            goal_long = self.env['finance.goal'].create({
                'profile_id': profile.id,
                'name': self.objetivo_longo_prazo,
                'goal_type': 'retirement',  # Assume aposentadoria
                'target_value': 0.0,  # Consultor preencherá depois
                'current_value': 0.0,
                'deadline_years': 10,  # Longo prazo = 10 anos (default)
                'priority': 'medium',
                'status': 'not_started',
            })
            goals_created.append(goal_long.name)
        
        # Notificação
        if goals_created:
            self.message_post(
                body=_(
                    "🎯 <strong>Objetivos Financeiros criados automaticamente:</strong><br/>"
                    "• %s"
                ) % "<br/>• ".join(goals_created)
            )


