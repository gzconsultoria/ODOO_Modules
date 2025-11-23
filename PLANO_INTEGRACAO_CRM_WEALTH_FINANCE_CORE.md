# 🔄 Plano de Integração: CRM Wealth → Finance Core

**Data:** 22/11/2024  
**Objetivo:** Trazer funcionalidades essenciais do CRM Wealth para Finance Core, mantendo arquitetura modular

---

## 🎯 Estratégia de Migração

### **Princípios:**
1. ✅ **Trazer para Finance Core:** Dados que são parte integral do perfil do cliente
2. ❌ **NÃO trazer:** Funcionalidades que já existem em outros módulos (`finance_planning`, `finance_compliance`, `finance_investments`)
3. ⚠️ **Adaptar:** Campos de processo do CRM para o contexto de onboarding do Finance Profile
4. 🔄 **Visibilidade progressiva:** Implementar abas que aparecem conforme `onboarding_stage`

---

## 📋 Análise Campo a Campo

### ✅ **TRAZER PARA FINANCE CORE** (Prioridade ALTA)

#### **1. Dados Pessoais (Relacionamento)**
```python
# ORIGEM: CRM Wealth
data_aniversario_cliente       → client_birthdate
estado_civil                   → marital_status  
nome_conjuge                   → spouse_name
data_aniversario_conjuge       → spouse_birthdate
quantidade_filhos              → children_count
nomes_filhos                   → children_names
time_coracao                   → favorite_team
hobbies                        → hobbies

# MOTIVO: Dados pessoais são core do relacionamento wealth management
# NÃO existe em nenhum outro módulo finance_*
```

#### **2. Objetivos Financeiros**
```python
# ORIGEM: CRM Wealth
objetivo_curto_prazo           → short_term_goal
objetivo_longo_prazo           → long_term_goal
objetivo_principal             → main_goal
valor_objetivo                 → goal_amount
prazo_objetivo                 → goal_deadline_years

# MOTIVO: Objetivos básicos devem estar no profile
# finance_planning tem metas DETALHADAS (com versões, snapshots)
# Aqui é apenas resumo inicial
```

#### **3. Cálculos Financeiros**
```python
# ORIGEM: CRM Wealth
aporte_mensal_necessario       → monthly_contribution_needed (computed)

# MÉTODO A COPIAR:
@api.depends('valor_objetivo', 'prazo_objetivo')
def _compute_calculos_financeiros(self):
    # Fórmula PMT: FV / [((1 + i)^n - 1) / i]
    taxa_anual = float(self.env['ir.config_parameter'].sudo().get_param('finance_core.taxa_padrao', default=10.0))
    
# MOTIVO: Cálculo útil para primeira conversa com cliente
# NÃO precisa da complexidade do finance_planning
```

#### **4. Diagnóstico Financeiro (SWOT)**
```python
# ORIGEM: CRM Wealth (aba Reunião)
diagnostico_situacao_atual     → diagnosis_current_situation
diagnostico_pontos_fortes      → diagnosis_strengths
diagnostico_pontos_melhorar    → diagnosis_weaknesses
diagnostico_oportunidades      → diagnosis_opportunities

# MOTIVO: Diagnóstico inicial é parte do onboarding
# finance_compliance tem recomendações FORMAIS (com compliance)
# Aqui é apenas notas iniciais
```

#### **5. Proposta Comercial**
```python
# ORIGEM: CRM Wealth (aba Proposta)
plano_contratado               → contract_plan
valor_proposta                 → proposal_amount
fee_gestao                     → management_fee
tipo_contrato                  → contract_type
receita_anual_estimada         → estimated_annual_revenue (computed)

# MOTIVO: Dados comerciais são parte do profile do cliente
# NÃO existe módulo finance_commercial
```

#### **6. Sistema de Visibilidade Progressiva**
```python
# ORIGEM: CRM Wealth
# ADAPTAR onboarding_stage existente para controlar visibilidade

# Mapeamento:
# new         → Mostra: Dados Pessoais + Objetivos
# diagnosis   → Mostra: + Diagnóstico  
# planning    → Mostra: + Proposta
# execution   → Mostra: + (tudo via outros módulos)
# review      → Mostra: + (tudo)

# CAMPOS COMPUTADOS:
show_personal_data = fields.Boolean(compute='_compute_show_tabs')
show_goals = fields.Boolean(compute='_compute_show_tabs')
show_diagnosis = fields.Boolean(compute='_compute_show_tabs')
show_proposal = fields.Boolean(compute='_compute_show_tabs')
```

---

### ❌ **NÃO TRAZER** (Já existe em outros módulos)

#### **1. Documentação e Onboarding**
```python
# CRM Wealth tem:
documentos_entregues           # Many2many
contas_corretoras              # Many2many
estrutura_inicial_montada      # Boolean

# JÁ EXISTE EM: finance_compliance
# - finance.document (com versionamento, expiração)
# - finance.recommendation (recomendações formais)
# DECISÃO: NÃO duplicar
```

#### **2. Execução e Carteiras**
```python
# CRM Wealth tem:
valor_investido_atual          # Monetary
distribuicao_portfolio         # Text
acompanhamento_mensal_ids      # One2many

# JÁ EXISTE EM: finance_investments
# - finance.portfolio (versionado com snapshots)
# - finance.portfolio.snapshot (histórico completo)
# DECISÃO: NÃO duplicar
```

#### **3. Captação (Faixas genéricas)**
```python
# CRM Wealth tem:
patrimonio_aproximado          # Faixas: <50k, 50-200k, etc
renda_mensal                   # Faixas: <5k, 5-10k, etc

# JÁ EXISTE EM: finance_core
# - annual_income (valor exato, mais preciso)
# - net_worth (valor exato, mais preciso)
# DECISÃO: Manter valores exatos, NÃO adicionar faixas
```

#### **4. SLA e Crons**
```python
# CRM Wealth tem:
stage_date                     # Datetime
days_in_current_stage          # Integer
sla_status                     # Selection
# + 3 cron jobs diários

# MOTIVO: SLA faz sentido em CRM (processo de vendas)
# Finance Profile não tem "pipeline de vendas"
# DECISÃO: NÃO trazer (complexidade desnecessária)
```

---

### ⚠️ **ADAPTAR** (Modificar para contexto Finance)

#### **1. Interesse Inicial → Investor Interests**
```python
# CRM Wealth tem:
interesse_inicial              # Many2many com tags

# ADAPTAR PARA:
investor_interests = fields.Many2many(
    'finance.interest.tag',
    string='Interesses do Investidor',
    help='Bolsa, Renda Fixa, Fundos Imobiliários, Criptomoedas, etc'
)

# Criar modelo auxiliar:
class FinanceInterestTag(models.Model):
    _name = 'finance.interest.tag'
    name = fields.Char(required=True)
    color = fields.Integer()
```

#### **2. Momento Financeiro → Financial Readiness**
```python
# CRM Wealth tem:
momento_financeiro             # Organizando/Iniciando/Planejamento

# ADAPTAR PARA:
financial_readiness = fields.Selection([
    ('organizing', '📋 Organizando finanças'),
    ('starting', '🚀 Iniciando investimentos'),
    ('planning', '🎯 Planejando crescimento'),
    ('optimizing', '⚡ Otimizando patrimônio')
], string='Momento Financeiro')
```

#### **3. Dor Principal → Primary Pain Point**
```python
# CRM Wealth tem:
dor_principal                  # Tempo/Estratégia/Medo/Organização

# ADAPTAR PARA:
primary_pain_point = fields.Selection([
    ('time', '⏰ Falta de tempo'),
    ('strategy', '🎯 Falta de estratégia'),
    ('fear', '😰 Medo de perder dinheiro'),
    ('organization', '📊 Desorganização financeira'),
    ('knowledge', '📚 Falta de conhecimento')
], string='Dor Principal do Cliente')
```

---

## 🏗️ Estrutura de Implementação

### **Fase 1: Adicionar Campos ao Modelo** (1h)

**Arquivo:** `finance_core/models/finance_profile.py`

```python
class FinanceProfile(models.Model):
    _inherit = 'finance.profile'
    
    # ============================================================
    # DADOS PESSOAIS (Relacionamento)
    # ============================================================
    client_birthdate = fields.Date(string="Aniversário do Cliente")
    marital_status = fields.Selection([
        ('single', 'Solteiro(a)'),
        ('married', 'Casado(a)'),
        ('divorced', 'Divorciado(a)'),
        ('widowed', 'Viúvo(a)')
    ], string="Estado Civil")
    spouse_name = fields.Char(string="Nome do(a) Cônjuge")
    spouse_birthdate = fields.Date(string="Aniversário do(a) Cônjuge")
    children_count = fields.Integer(string="Quantidade de Filhos", default=0)
    children_names = fields.Text(string="Nomes e Idades dos Filhos")
    favorite_team = fields.Char(string="Time do Coração")
    hobbies = fields.Text(string="Hobbies/Interesses")
    
    # ============================================================
    # OBJETIVOS FINANCEIROS (Resumo Inicial)
    # ============================================================
    short_term_goal = fields.Text(string="Objetivo Curto Prazo (12 meses)")
    long_term_goal = fields.Text(string="Objetivo Longo Prazo (5+ anos)")
    main_goal = fields.Selection([
        ('retirement', 'Aposentadoria'),
        ('fire', 'FIRE (Independência Financeira)'),
        ('property', 'Compra de Imóvel'),
        ('education', 'Educação dos Filhos'),
        ('travel', 'Viagens'),
        ('business', 'Abrir Negócio'),
        ('legacy', 'Deixar Legado')
    ], string="Objetivo Principal")
    goal_amount = fields.Monetary(
        string="Valor do Objetivo",
        currency_field='currency_id'
    )
    goal_deadline_years = fields.Integer(string="Prazo (anos)")
    monthly_contribution_needed = fields.Monetary(
        string="Aporte Mensal Necessário",
        compute='_compute_monthly_contribution',
        store=True,
        currency_field='currency_id',
        help="Cálculo automático usando fórmula PMT"
    )
    
    # ============================================================
    # DIAGNÓSTICO FINANCEIRO (SWOT Inicial)
    # ============================================================
    diagnosis_current_situation = fields.Text(string="Situação Atual")
    diagnosis_strengths = fields.Text(string="Pontos Fortes")
    diagnosis_weaknesses = fields.Text(string="Pontos a Melhorar")
    diagnosis_opportunities = fields.Text(string="Oportunidades")
    diagnosis_date = fields.Date(string="Data do Diagnóstico")
    
    # ============================================================
    # PROPOSTA COMERCIAL
    # ============================================================
    contract_plan = fields.Selection([
        ('monthly', 'Mensal'),
        ('fire', 'FIRE'),
        ('premium', 'Premium'),
        ('wealth', 'Gestão de Patrimônio'),
        ('mentoring', 'Mentoria')
    ], string="Plano Contratado", tracking=True)
    proposal_amount = fields.Monetary(
        string="Valor da Proposta",
        currency_field='currency_id',
        tracking=True
    )
    management_fee = fields.Float(
        string="Fee de Gestão (%)",
        help="Percentual anual sobre AUM",
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
        currency_field='currency_id'
    )
    proposal_justification = fields.Text(string="Justificativa da Proposta")
    
    # ============================================================
    # QUALIFICAÇÃO INICIAL
    # ============================================================
    financial_readiness = fields.Selection([
        ('organizing', '📋 Organizando finanças'),
        ('starting', '🚀 Iniciando investimentos'),
        ('planning', '🎯 Planejando crescimento'),
        ('optimizing', '⚡ Otimizando patrimônio')
    ], string='Momento Financeiro')
    
    primary_pain_point = fields.Selection([
        ('time', '⏰ Falta de tempo'),
        ('strategy', '🎯 Falta de estratégia'),
        ('fear', '😰 Medo de perder dinheiro'),
        ('organization', '📊 Desorganização financeira'),
        ('knowledge', '📚 Falta de conhecimento')
    ], string='Dor Principal')
    
    investor_interests_ids = fields.Many2many(
        'finance.interest.tag',
        string='Interesses do Investidor'
    )
    
    # ============================================================
    # VISIBILIDADE PROGRESSIVA DE ABAS
    # ============================================================
    show_personal_data = fields.Boolean(
        compute='_compute_show_tabs',
        string='Mostrar Dados Pessoais'
    )
    show_goals = fields.Boolean(
        compute='_compute_show_tabs',
        string='Mostrar Objetivos'
    )
    show_diagnosis = fields.Boolean(
        compute='_compute_show_tabs',
        string='Mostrar Diagnóstico'
    )
    show_proposal = fields.Boolean(
        compute='_compute_show_tabs',
        string='Mostrar Proposta'
    )
    
    # ============================================================
    # MÉTODOS COMPUTADOS
    # ============================================================
    
    @api.depends('onboarding_stage')
    def _compute_show_tabs(self):
        """Controla visibilidade progressiva das abas baseado no estágio"""
        stage_order = ['new', 'diagnosis', 'planning', 'execution', 'review']
        
        for profile in self:
            current_index = stage_order.index(profile.onboarding_stage) if profile.onboarding_stage else 0
            
            # Aba Dados Pessoais: sempre visível
            profile.show_personal_data = True
            
            # Aba Objetivos: sempre visível
            profile.show_goals = True
            
            # Aba Diagnóstico: a partir de 'diagnosis'
            profile.show_diagnosis = current_index >= 1
            
            # Aba Proposta: a partir de 'planning'
            profile.show_proposal = current_index >= 2
    
    @api.depends('goal_amount', 'goal_deadline_years')
    def _compute_monthly_contribution(self):
        """Calcula aporte mensal necessário usando fórmula PMT"""
        for profile in self:
            if not profile.goal_amount or not profile.goal_deadline_years:
                profile.monthly_contribution_needed = 0.0
                continue
            
            # Taxa anual padrão (configurável)
            taxa_anual = float(
                self.env['ir.config_parameter'].sudo()
                .get_param('finance_core.default_return_rate', default=10.0)
            )
            
            # Conversão para taxa mensal
            taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
            n_meses = profile.goal_deadline_years * 12
            
            # Fórmula PMT: FV / [((1 + i)^n - 1) / i]
            if taxa_mensal > 0:
                denominador = ((1 + taxa_mensal) ** n_meses - 1) / taxa_mensal
                profile.monthly_contribution_needed = profile.goal_amount / denominador
            else:
                # Se taxa = 0, divisão simples
                profile.monthly_contribution_needed = profile.goal_amount / n_meses
    
    @api.depends('proposal_amount', 'management_fee', 'portfolio_value')
    def _compute_estimated_revenue(self):
        """Calcula receita anual estimada"""
        for profile in self:
            if profile.contract_type == 'aum_percentage' and profile.management_fee > 0:
                # % sobre AUM
                profile.estimated_annual_revenue = (
                    profile.portfolio_value * profile.management_fee / 100
                )
            elif profile.proposal_amount > 0:
                # Mensalidade fixa × 12
                profile.estimated_annual_revenue = profile.proposal_amount * 12
            else:
                profile.estimated_annual_revenue = 0.0
```

---

### **Fase 2: Criar Modelo Auxiliar** (30min)

**Arquivo:** `finance_core/models/finance_interest_tag.py`

```python
# -*- coding: utf-8 -*-
from odoo import models, fields


class FinanceInterestTag(models.Model):
    _name = 'finance.interest.tag'
    _description = 'Tags de interesses do investidor'
    _order = 'name'
    
    name = fields.Char(string='Interesse', required=True)
    color = fields.Integer(string='Cor', default=0)
    active = fields.Boolean(default=True)
```

---

### **Fase 3: Atualizar Views XML** (2h)

**Arquivo:** `finance_core/views/finance_profile_views.xml`

```xml
<!-- ADICIONAR dentro do <notebook> existente -->

<page string="👤 Dados Pessoais" invisible="not show_personal_data">
    <field name="show_personal_data" invisible="1"/>
    <group>
        <group string="Cliente">
            <field name="client_birthdate"/>
            <field name="marital_status"/>
            <field name="children_count"/>
            <field name="children_names" invisible="children_count == 0"/>
        </group>
        <group string="Cônjuge" invisible="marital_status not in ['married']">
            <field name="spouse_name"/>
            <field name="spouse_birthdate"/>
        </group>
        <group string="Interesses Pessoais">
            <field name="favorite_team"/>
            <field name="hobbies" widget="text"/>
        </group>
    </group>
</page>

<page string="🎯 Objetivos" invisible="not show_goals">
    <field name="show_goals" invisible="1"/>
    <group>
        <group string="Objetivos">
            <field name="short_term_goal" widget="text"/>
            <field name="long_term_goal" widget="text"/>
            <field name="main_goal"/>
        </group>
        <group string="Meta Principal">
            <field name="goal_amount"/>
            <field name="goal_deadline_years"/>
            <field name="monthly_contribution_needed" readonly="1"/>
        </group>
    </group>
</page>

<page string="🔍 Diagnóstico" invisible="not show_diagnosis">
    <field name="show_diagnosis" invisible="1"/>
    <group>
        <field name="diagnosis_date"/>
    </group>
    <group>
        <group string="Análise SWOT">
            <field name="diagnosis_current_situation" widget="text"/>
            <field name="diagnosis_strengths" widget="text"/>
            <field name="diagnosis_weaknesses" widget="text"/>
            <field name="diagnosis_opportunities" widget="text"/>
        </group>
    </group>
</page>

<page string="💼 Proposta" invisible="not show_proposal">
    <field name="show_proposal" invisible="1"/>
    <group>
        <group string="Plano Comercial">
            <field name="contract_plan"/>
            <field name="proposal_amount"/>
            <field name="contract_type"/>
        </group>
        <group string="Precificação">
            <field name="management_fee"/>
            <field name="estimated_annual_revenue" readonly="1"/>
            <field name="proposal_justification" widget="text"/>
        </group>
    </group>
</page>

<page string="🎲 Qualificação Inicial">
    <group>
        <field name="financial_readiness"/>
        <field name="primary_pain_point"/>
        <field name="investor_interests_ids" widget="many2many_tags"/>
    </group>
</page>
```

---

### **Fase 4: Dados Iniciais** (30min)

**Arquivo:** `finance_core/data/finance_interest_tag_data.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Tags de Interesses -->
        <record id="interest_stocks" model="finance.interest.tag">
            <field name="name">Ações/Bolsa</field>
            <field name="color">1</field>
        </record>
        <record id="interest_fixed_income" model="finance.interest.tag">
            <field name="name">Renda Fixa</field>
            <field name="color">2</field>
        </record>
        <record id="interest_reits" model="finance.interest.tag">
            <field name="name">Fundos Imobiliários</field>
            <field name="color">3</field>
        </record>
        <record id="interest_crypto" model="finance.interest.tag">
            <field name="name">Criptomoedas</field>
            <field name="color">4</field>
        </record>
        <record id="interest_international" model="finance.interest.tag">
            <field name="name">Investimentos Internacionais</field>
            <field name="color">5</field>
        </record>
        <record id="interest_retirement" model="finance.interest.tag">
            <field name="name">Previdência Privada</field>
            <field name="color">6</field>
        </record>
    </data>
</odoo>
```

---

### **Fase 5: Segurança** (15min)

**Arquivo:** `finance_core/security/ir.model.access.csv`

```csv
# Adicionar linha:
access_finance_interest_tag_consultant,finance.interest.tag consultant,model_finance_interest_tag,finance_core.group_finance_consultant,1,1,1,1
```

---

### **Fase 6: Atualizar __manifest__.py** (5min)

```python
'data': [
    # ... arquivos existentes ...
    'data/finance_interest_tag_data.xml',
],
```

---

## 📊 Resumo da Integração

### **O que SERÁ adicionado ao Finance Core:**

| Categoria | Campos | Motivo |
|-----------|--------|--------|
| **Dados Pessoais** | 8 campos | Relacionamento wealth management |
| **Objetivos** | 6 campos + 1 computed | Resumo inicial (detalhes em finance_planning) |
| **Diagnóstico** | 5 campos | SWOT inicial do onboarding |
| **Proposta** | 6 campos + 1 computed | Dados comerciais do contrato |
| **Qualificação** | 3 campos | Qualificação inicial do perfil |
| **Visibilidade** | 4 campos computed | UX progressiva baseada em estágio |

**Total:** ~30 campos novos

---

### **O que NÃO SERÁ trazido:**

| Funcionalidade | Motivo |
|----------------|--------|
| Documentos/Compliance | Já existe em `finance_compliance` |
| Carteiras/Portfolio | Já existe em `finance_investments` |
| Faixas de renda/patrimônio | Finance Core tem valores exatos (melhor) |
| SLA/Crons | Não faz sentido fora do contexto CRM |
| Acompanhamento mensal | Já existe em `finance_calendar_integration` |
| Completude por aba | Complexidade desnecessária |

---

## ✅ Próximos Passos

1. **Revisar este plano** e confirmar campos a adicionar
2. **Implementar Fase 1** (modelo)
3. **Implementar Fase 2** (modelo auxiliar)
4. **Implementar Fase 3** (views)
5. **Implementar Fase 4** (dados)
6. **Implementar Fase 5** (segurança)
7. **Atualizar módulo** e testar
8. **Desativar CRM Wealth** após validação

---

**Estimativa total:** 4-5 horas de desenvolvimento + 2 horas de testes = **1 dia de trabalho** 🚀
