# 📊 Comparativo Detalhado: CRM Wealth vs Finance Core

**Data:** 22/11/2024  
**Objetivo:** Identificar gaps no `finance_core` em relação ao `crm_wealth`

---

## 🎯 Resumo Executivo

O `finance_core` é **mais enxuto e focado**, enquanto o `crm_wealth` é **mais completo e detalhado** para consultoria financeira.

### **Estatísticas:**

| Aspecto | CRM Wealth | Finance Core | Gap |
|---------|------------|--------------|-----|
| **Campos totais** | ~80 campos | ~25 campos | **-55 campos** |
| **Dados pessoais** | ✅ Completo | ❌ Ausente | **100%** |
| **Objetivos financeiros** | ✅ Detalhado | ⚠️ Resumido | **70%** |
| **Suitability** | ✅ Preliminar + Final | ✅ Completo | **0%** |
| **Proposta comercial** | ✅ Completo | ❌ Ausente | **100%** |
| **Acompanhamento** | ✅ One2many tracking | ⚠️ Via módulos | **50%** |
| **Cálculos financeiros** | ✅ Automáticos | ❌ Manuais | **100%** |

---

## 📋 Análise Detalhada por Categoria

### 1️⃣ **DADOS PESSOAIS (Relacionamento)**

#### ✅ **CRM Wealth tem:**
```python
# Campos para conexão emocional com cliente
data_aniversario_cliente       # Data de aniversário
estado_civil                   # Solteiro/Casado/Divorciado/Viúvo
nome_conjuge                   # Nome do cônjuge
data_aniversario_conjuge       # Aniversário do cônjuge
quantidade_filhos              # Número de filhos
nomes_filhos                   # "João (5), Maria (8)"
time_coracao                   # Time de futebol
hobbies                        # Hobbies e interesses
```

#### ❌ **Finance Core tem:**
```python
household_notes                # Notas genéricas (não estruturado)
```

**📉 GAP: 87.5%** - Finance Core não tem estrutura para relacionamento pessoal

---

### 2️⃣ **OBJETIVOS FINANCEIROS**

#### ✅ **CRM Wealth tem:**
```python
# Objetivos muito detalhados
objetivo_curto_prazo           # Texto livre (12 meses)
objetivo_longo_prazo           # Texto livre (5+ anos)
objetivo_principal             # Selection: Aposentadoria/FIRE/Imóvel/Educação/etc
valor_objetivo                 # R$ 1.000.000
prazo_objetivo                 # 10 anos
aporte_mensal_necessario       # CALCULADO AUTOMATICAMENTE (PMT)
```

#### ⚠️ **Finance Core tem:**
```python
objective_summary              # Texto livre genérico
# Objetivos detalhados estão em finance_planning (módulo separado)
```

**📉 GAP: 70%** - Precisa instalar `finance_planning` para ter funcionalidade similar

---

### 3️⃣ **SUITABILITY E PERFIL DE RISCO**

#### ✅ **CRM Wealth tem:**
```python
# Suitability em 2 estágios
perfil_investidor             # PRELIMINAR (captação)
perfil_risco_final            # FINAL (pós-oficial)
suitability_oficial           # Boolean: preencheu oficial?
```

#### ✅ **Finance Core tem:**
```python
suitability_score             # 0-100 pontos
suitability_profile           # Conservador/Moderado/Arrojado
suitability_last_review       # Data última revisão
suitability_next_review       # Data próxima (calculado)
suitability_state             # draft/valid/expiring/expired
```

**✅ GAP: 0%** - Finance Core tem abordagem **mais robusta** com versionamento temporal

---

### 4️⃣ **DIAGNÓSTICO FINANCEIRO**

#### ✅ **CRM Wealth tem:**
```python
# Diagnóstico estruturado (aba Reunião)
diagnostico_situacao_atual    # Texto: situação atual
diagnostico_pontos_fortes     # Texto: o que está bom
diagnostico_pontos_melhorar   # Texto: pontos fracos
diagnostico_oportunidades     # Texto: sugestões
estrategias_recomendadas      # Many2many tags
data_reuniao                  # Data da reunião
estrategias_discutidas        # Notas da reunião
objecoes_identificadas        # Objeções levantadas
```

#### ❌ **Finance Core tem:**
```python
# Nada estruturado para diagnóstico
```

**📉 GAP: 100%** - Funcionalidade completamente ausente

---

### 5️⃣ **PROPOSTA COMERCIAL**

#### ✅ **CRM Wealth tem:**
```python
# Proposta e precificação
plano_contratado              # Mensal/FIRE/Premium/Gestão/Mentoria
valor_proposta                # R$ 5.000/mês
justificativa_valor           # Texto: por que vale?
objecoes_apresentadas         # Many2many: Preço/Tempo/Medo/etc
fee_gestao                    # 1.5% a.a.
tipo_contrato                 # Mensal/Trimestral/% AUM
receita_anual_estimada        # CALCULADO: valor × fee
```

#### ❌ **Finance Core tem:**
```python
# Nada relacionado a proposta comercial
```

**📉 GAP: 100%** - Funcionalidade completamente ausente

---

### 6️⃣ **CAPTAÇÃO E QUALIFICAÇÃO**

#### ✅ **CRM Wealth tem:**
```python
# Dados de captação
momento_financeiro            # Organizando/Iniciando/Planejamento
patrimonio_aproximado         # Faixas: <50k, 50-200k, 200-500k, etc
renda_mensal                  # Faixas: <5k, 5-10k, 10-20k, etc
interesse_inicial             # Many2many tags
dor_principal                 # Tempo/Estratégia/Medo/Organização
```

#### ⚠️ **Finance Core tem:**
```python
annual_income                 # Valor exato (não faixas)
net_worth                     # Patrimônio líquido
saving_capacity               # Capacidade de poupança
```

**📉 GAP: 40%** - Finance Core tem dados, mas sem **qualificação inicial**

---

### 7️⃣ **ONBOARDING E DOCUMENTAÇÃO**

#### ✅ **CRM Wealth tem:**
```python
# Onboarding estruturado
suitability_oficial           # Boolean
documentos_entregues          # Many2many: ID/Comprovante/Extratos
perfil_risco_final            # Após suitability oficial
estrutura_inicial_montada     # Boolean checklist
contas_corretoras             # Many2many: Clear/XP/BTG/etc
```

#### ⚠️ **Finance Core tem:**
```python
onboarding_stage              # new/diagnosis/planning/execution/review
# Documentos estão em finance_compliance (módulo separado)
```

**📉 GAP: 60%** - Precisa instalar `finance_compliance`

---

### 8️⃣ **EXECUÇÃO E ACOMPANHAMENTO**

#### ✅ **CRM Wealth tem:**
```python
# Execução integrada
valor_investido_atual         # AUM atual
distribuicao_portfolio        # Texto/JSON com alocação
acompanhamento_mensal_ids     # One2many: reuniões mensais
historico_mudancas            # Log de mudanças de estratégia
```

**Modelo auxiliar completo:**
```python
class CrmWealthAcompanhamento(models.Model):
    name                      # Título da reunião
    lead_id                   # Link ao lead
    data_reuniao              # Data
    valor_portfolio           # Valor na data
    rentabilidade_periodo     # % no período
    observacoes              # Notas da reunião
```

#### ⚠️ **Finance Core tem:**
```python
portfolio_value               # AUM consolidado
# Carteiras estão em finance_investments (versionadas com snapshots)
# Reuniões estão em finance_calendar_integration
```

**📉 GAP: 50%** - Funcionalidade distribuída em módulos

---

### 9️⃣ **CÁLCULOS FINANCEIROS AUTOMÁTICOS**

#### ✅ **CRM Wealth tem:**
```python
@api.depends('valor_objetivo', 'prazo_objetivo')
def _compute_calculos_financeiros(self):
    # CÁLCULO 1: Aporte Mensal (PMT)
    # FV / [((1 + i)^n - 1) / i]
    aporte_mensal_necessario
    
    # CÁLCULO 2: Receita Anual
    # Valor Proposta × Fee Gestão
    receita_anual_estimada
```

#### ❌ **Finance Core tem:**
```python
# Sem cálculos automáticos financeiros
```

**📉 GAP: 100%** - Funcionalidade ausente

---

### 🔟 **SCORES E INDICADORES**

#### ✅ **CRM Wealth tem:**
```python
# Sistema de scoring completo
score_qualificacao            # 0-100 (completude + potencial)
lead_temperature              # Cold/Warm/Hot
dias_em_pipeline              # Dias desde criação
progresso_geral               # % média de completude
score_potencial               # ⭐ 0-5 estrelas
alertas_resumo                # HTML com alertas
perfil_pessoal_resumo         # HTML com dados pessoais

# Completude por aba (6 indicadores)
captacao_completude           # 0-100%
qualificacao_completude       # 0-100%
reuniao_completude            # 0-100%
proposta_completude           # 0-100%
onboarding_completude         # 0-100%
execucao_completude           # 0-100%
```

#### ⚠️ **Finance Core tem:**
```python
advisory_score                # 0-100 (saúde financeira)
goals_progress                # % progresso metas
cashflow_balance              # Saldo fluxo caixa
portfolio_value               # AUM total
pending_documents             # Docs pendentes
```

**📉 GAP: 30%** - Finance Core tem indicadores, mas sem **completude de processo**

---

### 1️⃣1️⃣ **SLA E RASTREAMENTO**

#### ✅ **CRM Wealth tem:**
```python
# SLA por estágio
stage_date                    # Timestamp entrada no estágio
days_in_current_stage         # Dias no estágio atual
sla_status                    # OK/Warning/Exceeded

# 3 Cron jobs diários
action_check_sla_captacao()   # Verifica estagnação
action_check_sla_proposta()
action_check_sla_reuniao()
```

#### ⚠️ **Finance Core tem:**
```python
# Alertas genéricos (sem SLA de estágios)
advisory_alert_ids            # Alertas inteligentes
_generate_smart_alerts()      # Gera alertas automáticos
```

**📉 GAP: 70%** - Finance Core tem alertas, mas sem **SLA de processo**

---

### 1️⃣2️⃣ **VISIBILIDADE PROGRESSIVA**

#### ✅ **CRM Wealth tem:**
```python
# Sistema de abas progressivas (6 estágios)
show_captacao                 # Visível em seq >= 10
show_qualificacao             # Visível em seq >= 20
show_reuniao                  # Visível em seq >= 30
show_proposta                 # Visível em seq >= 40
show_onboarding               # Visível em seq >= 50
show_execucao                 # Visível em seq >= 60

@api.depends('stage_id', 'stage_sequence')
def _compute_show_tabs(self):
    # Mostra abas conforme progressão
```

#### ❌ **Finance Core tem:**
```python
# Tudo visível sempre
# Não tem conceito de progressão/estágios
```

**📉 GAP: 100%** - Funcionalidade ausente

---

## 🎨 Tabela Comparativa Consolidada

| Funcionalidade | CRM Wealth | Finance Core | Requer Módulo Extra | Gap |
|----------------|------------|--------------|---------------------|-----|
| **Dados Pessoais** | ✅ 8 campos | ❌ 1 campo | - | 87% |
| **Objetivos** | ✅ 6 campos + cálculo | ⚠️ 1 campo | finance_planning | 70% |
| **Suitability** | ✅ 2 estágios | ✅ Robusto | - | 0% |
| **Diagnóstico** | ✅ 7 campos | ❌ Ausente | - | 100% |
| **Proposta** | ✅ 7 campos | ❌ Ausente | - | 100% |
| **Captação** | ✅ 5 campos | ⚠️ 3 campos | - | 40% |
| **Onboarding** | ✅ 5 campos | ⚠️ 1 campo | finance_compliance | 60% |
| **Execução** | ✅ 4 campos + One2many | ⚠️ Distribuído | finance_investments | 50% |
| **Cálculos** | ✅ 2 automáticos | ❌ Ausente | - | 100% |
| **Scores** | ✅ 6 indicadores | ⚠️ 5 indicadores | - | 30% |
| **SLA** | ✅ 3 crons | ⚠️ Alertas genéricos | - | 70% |
| **Progressão** | ✅ 6 abas dinâmicas | ❌ Ausente | - | 100% |

---

## 💡 Recomendações

### **Opção A: Enriquecer Finance Core** ⭐ RECOMENDADO

Adicionar ao `finance_core` os campos ausentes mais críticos:

#### **Prioridade ALTA (fazer agora):**
1. ✅ Dados pessoais estruturados (aniversários, família, hobbies)
2. ✅ Objetivos financeiros detalhados (curto/longo prazo)
3. ✅ Cálculos financeiros automáticos (PMT, receita estimada)
4. ✅ Diagnóstico estruturado (situação/pontos fortes/oportunidades)

#### **Prioridade MÉDIA (próxima sprint):**
5. ⚠️ Proposta comercial (plano/valor/fee/objeções)
6. ⚠️ Dados de captação (momento/faixas de renda/interesses)
7. ⚠️ Sistema de completude (% preenchimento)

#### **Prioridade BAIXA (futuro):**
8. ⏳ SLA por estágio com crons
9. ⏳ Visibilidade progressiva de abas
10. ⏳ Score de temperatura (cold/warm/hot)

### **Opção B: Usar Finance + Módulos Adicionais**

Aceitar arquitetura modular e instalar:
- `finance_planning` - Para objetivos e metas
- `finance_investments` - Para carteiras versionadas
- `finance_compliance` - Para documentos e onboarding
- `finance_crm_integration` - Para ponte com CRM

**Vantagem:** Separação de responsabilidades  
**Desvantagem:** Múltiplos módulos para instalar

---

## 📊 Conclusão

O `crm_wealth` é **monolítico e completo**, ideal para quem quer tudo em um lugar.

O `finance_core` é **modular e profissional**, mas **requer módulos adicionais** para ter todas as funcionalidades.

**Sugestão:** Criar módulo `finance_relationship` para adicionar campos pessoais e diagnóstico ao `finance_core`, mantendo arquitetura limpa.

---

**Próximos passos:** Definir quais campos adicionar ao `finance_core` baseado nas prioridades acima. 🚀
