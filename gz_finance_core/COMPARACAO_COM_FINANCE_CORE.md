# 📊 Comparação: finance_core vs gz_finance_core

## 🏗️ Arquitetura Fundamental

| Aspecto | finance_core | gz_finance_core |
|---------|-------------|-----------------|
| **Modelo Base** | `finance.profile` (separado) | `res.partner` (herança) |
| **Total de Campos** | 72 campos | 20 campos |
| **Abordagem** | SSOT com modelo dedicado | SSOT via extensão Partner |
| **Duplicação de Dados** | Não (mas cria registro extra) | Não (usa Partner nativo) |

---

## 📋 Análise por Categoria

### 🔐 **Compliance & KYC**

**finance_core (9 campos):**
- `suitability_score`, `suitability_profile`, `suitability_state`
- `suitability_last_review`, `suitability_next_review`
- `compliance_status`, `risk_warnings`
- `privacy_deletion_requested`, `privacy_requested_date`

**gz_finance_core (5 campos):**
- `kyc_status`, `kyc_completed_date`, `kyc_expiry_date`
- `is_pep`, `risk_profile`

**Análise:** gz_finance_core tem KYC básico, mas falta sistema completo de suitability com reviews.

---

### 💰 **Patrimônio & AUM**

**finance_core (5 campos):**
- `net_worth`, `portfolio_value`
- `annual_income`, `saving_capacity`, `cashflow_balance`

**gz_finance_core (3 campos):**
- `aum`, `aum_updated_at`
- `finance_patrimony_ids` (One2many → modelo separado com histórico)

**Análise:** gz_finance_core tem vantagem com modelo `finance.patrimony` para snapshots históricos.

---

### 🎯 **Objetivos & Metas**

**finance_core (9 campos):**
- `short_term_goal`, `long_term_goal`, `main_goal`
- `goal_amount`, `goal_deadline_years`, `monthly_contribution_needed`
- `goals_progress`, `goals_progress_percentage`, `objective_summary`

**gz_finance_core (0 campos):**
- ❌ **GAP CRÍTICO:** Nenhum campo de objetivos

**Análise:** Necessita módulo `finance_planning` ou adicionar campos.

---

### 📊 **Lifecycle & Estágios**

**finance_core (2 campos):**
- `crm_lead_id`, `last_sync_date`

**gz_finance_core (4 campos):**
- `finance_lifecycle_state`, `lifecycle_changed_date`
- `finance_lifecycle_ids` (One2many → histórico completo)
- `client_segment` (Retail, Affluent, HNW, UHNW)

**Análise:** gz_finance_core SUPERIOR com modelo `finance.lifecycle` para tracking completo.

---

### 🔍 **Diagnóstico**

**finance_core (5 campos):**
- `diagnosis_date`, `diagnosis_current_situation`
- `diagnosis_strengths`, `diagnosis_weaknesses`, `diagnosis_opportunities`

**gz_finance_core (0 campos):**
- ❌ **GAP CRÍTICO:** Sem análise SWOT

**Análise:** Necessita adicionar campos de diagnóstico ao `res.partner`.

---

### 💼 **Proposta Comercial**

**finance_core (7 campos):**
- `proposal_date`, `proposal_amount`, `proposal_justification`
- `contract_plan`, `contract_type`
- `management_fee`, `estimated_annual_revenue`

**gz_finance_core (0 campos):**
- ❌ **GAP CRÍTICO:** Sem campos comerciais

**Análise:** Crítico para consultoria. Adicionar urgentemente.

---

### 👥 **Dados Pessoais Estendidos**

**finance_core (9 campos):**
- `client_birthdate`, `spouse_name`, `spouse_birthdate`
- `marital_status`, `children_count`, `children_names`
- `hobbies`, `favorite_team`, `household_notes`

**gz_finance_core (0 campos):**
- ❌ **GAP:** Sem dados pessoais estendidos

**Análise:** `res.partner` nativo já tem alguns (birthdate via contacts), mas faltam campos específicos.

---

### 🏷️ **Tags & Categorias**

**finance_core (3 campos):**
- `investor_interests_ids` (Many2many → finance.interest.tag)
- `recommended_strategies_ids` (Many2many → finance.strategy.tag)
- `proposal_objections_ids` (Many2many → finance.objection.tag)

**gz_finance_core (1 campo):**
- `finance_category_ids` (Many2many → finance.category)

**Análise:** gz_finance_core tem sistema básico. finance_core tem tags especializadas.

---

### 📅 **Reuniões & Follow-up**

**finance_core (6 campos):**
- `meeting_date`, `last_meeting_id`, `next_meeting_id`
- `days_since_last_meeting`
- `meeting_strategies_discussed`, `meeting_objections`

**gz_finance_core (0 campos):**
- ❌ **GAP:** Sem integração com reuniões

**Análise:** Odoo nativo tem `calendar.event`. Integração pode ser via módulo externo.

---

### ⚙️ **Outros Campos**

**finance_core:**
- `advisor_id`, `investor_type`, `financial_readiness`
- `primary_pain_point`, `potential_score`
- `advisory_score`, `advisory_alert_ids`
- `pending_documents`, `event_count`, `emergency_fund_months`

**gz_finance_core:**
- `advisor_id`, `advisor_team_id`
- `is_finance_client`, `finance_notes`
- `finance_invoice_count`

---

## 🎯 Resumo Executivo

### ✅ **Vantagens gz_finance_core**
1. **Arquitetura nativa:** Usa `res.partner` diretamente
2. **Lifecycle tracking:** Modelo `finance.lifecycle` com histórico completo
3. **AUM histórico:** Modelo `finance.patrimony` para snapshots
4. **Simplicidade:** Menos campos = mais focado
5. **Integração natural:** Aprovecha recursos nativos do Partner

### ❌ **GAPS Críticos gz_finance_core**

| Categoria | Campos Faltando | Prioridade |
|-----------|----------------|------------|
| Objetivos & Metas | 9 campos | 🔴 ALTA |
| Proposta Comercial | 7 campos | 🔴 ALTA |
| Diagnóstico | 5 campos | 🟡 MÉDIA |
| Dados Pessoais | 9 campos | 🟡 MÉDIA |
| Reuniões | 6 campos | 🟢 BAIXA |
| Suitability Avançado | 4 campos | 🟡 MÉDIA |

---

## 💡 Recomendações

### **Curto Prazo (MVP Funcional)**
1. ✅ **Manter arquitetura atual** (res.partner)
2. ➕ **Adicionar campos comerciais:**
   ```python
   # Proposta
   proposal_date = fields.Date()
   proposal_amount = fields.Monetary()
   management_fee = fields.Float(digits=(5,2))
   estimated_annual_revenue = fields.Monetary(compute='...')
   ```
3. ➕ **Adicionar objetivos básicos:**
   ```python
   main_goal = fields.Selection([...])
   goal_amount = fields.Monetary()
   monthly_contribution_needed = fields.Monetary(compute='...')
   ```

### **Médio Prazo (Consultoria Completa)**
4. 📦 **Criar módulo `gz_finance_planning`**
   - Modelo `finance.goal` (One2many)
   - Cálculos de aportes mensais
   - Tracking de progresso

5. 📦 **Criar módulo `gz_finance_meetings`**
   - Integrar com `calendar.event`
   - Wizard pré-reunião
   - Wizard pós-reunião

6. ➕ **Adicionar campos de diagnóstico:**
   ```python
   diagnosis_date = fields.Date()
   diagnosis_swot = fields.Html()  # SWOT completo
   ```

### **Longo Prazo (Ecosystem Completo)**
7. 📦 **Módulos especializados:**
   - `gz_finance_suitability` (questionário completo)
   - `gz_finance_reports` (relatórios customizados)
   - `gz_finance_portal` (portal do cliente)

---

## 🔄 Estratégia de Migração (se necessário)

Se já usa `finance_core` e quer migrar para `gz_finance_core`:

```python
# Script de migração
for profile in env['finance.profile'].search([]):
    partner = profile.partner_id
    partner.write({
        'is_finance_client': True,
        'advisor_id': profile.advisor_id.id,
        'kyc_status': map_suitability_to_kyc(profile.suitability_state),
        'risk_profile': profile.suitability_profile,
        # ... migrar campos compatíveis
    })
    
    # Criar lifecycle history
    env['finance.lifecycle'].create({
        'partner_id': partner.id,
        'stage': map_onboarding_to_lifecycle(profile.onboarding_stage),
        'changed_date': profile.create_date,
    })
```

---

## 📌 Conclusão

**gz_finance_core é MELHOR arquiteturalmente** (res.partner nativo), mas **finance_core é MAIS COMPLETO funcionalmente**.

**Recomendação:** 
- ✅ Manter `gz_finance_core` como base
- ➕ Adicionar campos críticos (proposta, objetivos)
- 📦 Criar módulos complementares (planning, meetings)
- 🎯 Resultado: **Melhor dos dois mundos**
