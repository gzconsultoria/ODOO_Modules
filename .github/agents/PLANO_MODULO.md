# Plano do Módulo `gz_finance_core`

## 1. Visão Geral

O módulo `gz_finance_core` será o núcleo do ecossistema financeiro, responsável por centralizar e orquestrar todos os dados financeiros, de suitability, perfil, objetivos e ciclo de vida do cliente, funcionando como **Single Source of Truth**.

Ele **não** implementa fluxos de CRM, operações de carteira, documentos físicos, assinaturas ou suitability dinâmico – isso fica para módulos satélites. O foco é **modelo de dados, integridade, governança e orquestração**.

---

## 2. Objetivos Principais

- Centralizar os dados financeiros e de perfil do cliente no modelo `finance.profile`.
- Garantir relação 1:1 entre `res.partner` e `finance.profile`.
- Ser a base de dados para CRM, Investimentos, Compliance, Documentos, Assinaturas e Portal.
- Controlar o ciclo de vida do cliente: onboarding → ativo → dormente → churn.
- Fornecer estrutura para relatórios, dashboards e auditoria.
- Garantir privacidade, LGPD e histórico de alterações.
- 2FA obrigatório para assessores
Tokenização de dados sensíveis

---

## 3. Arquitetura de Alto Nível

### 3.1. Módulo `gz_finance_core`

- Modelo central: `finance.profile`.
- Modelos auxiliares (minimalistas):
  - `finance.household` (estrutura familiar / núcleo econômico)
  - `finance.goal` (objetivos financeiros)
  - `finance.churn.reason` (motivos de churn)
  - `finance.suitability.history` (histórico de suitability / compliance)
- Sem dependências fortes de módulos satélites (apenas `base`, `contacts`, `mail`).

### 3.2. Relação com Módulos Satélites (futuros)

- `finance_crm_integration`: cria / alimenta `finance.profile` a partir de `crm.lead`.
- `finance_compliance`: estende suitability, KYC, pendências regulatórias.
- `finance_documents`: adiciona documentos vinculados ao profile.
- `finance_approve_sign`: controla assinaturas/aceites ligados ao profile.
- `finance_investments`: consolida patrimônio, AUM e distribuição de ativos.
- `finance_portal`: expõe dados do profile para o cliente final.

O `gz_finance_core` **não depende** desses módulos; eles herdam/estendem o core.

---

## 4. Modelo Central: `finance.profile`

### 4.1. Requisitos

- Relação 1:1 com `res.partner`.
- Pode ser alimentado inicialmente por `crm.lead` (via módulo de integração).
- Extensível por herança (`_inherit`) em módulos satélites.
- Armazena apenas informações **estáveis, duradouras e perenes**.

### 4.2. Categorias de Dados

#### 4.2.1. Identificação e Relação

- `partner_id` (Many2one → `res.partner`, required, unique)
- `household_id` (Many2one → `finance.household`)
- `advisor_id` (Many2one → `res.users` ou `res.partner` do assessor)
- `company_id` (Many2one → `res.company`)

#### 4.2.2. Dados Pessoais Não-Sensíveis

- `marital_status` (Selection)
- `spouse_name` / `spouse_partner_id` (Char / Many2one)
- `children_count` (Integer)
- `is_pep` (Boolean)

#### 4.2.3. Dados Financeiros Consolidados

- `estimated_net_worth` (Monetary)
- `monthly_income` (Monetary)
- `annual_income` (Monetary, computado opcional)
- `monthly_investment_capacity` (Monetary)
- `internal_risk_score` (Float ou Integer, 0-100)
- `aum_total` (Monetary, tipicamente `compute` a partir de `finance_investments`)
- `asset_allocation_snapshot` (JSON / Text estruturado ou campos agregados simplificados)

#### 4.2.4. Objetivos Financeiros

- One2many → `finance.goal` (`goal_ids`)
- Campo de conveniência `main_goal_id` (Many2one opcional)

`finance.goal` (modelo auxiliar) contendo:
- `name`
- `profile_id` (Many2one → `finance.profile`)
- `target_amount` (Monetary)
- `target_date` (Date)
- `monthly_contribution_needed` (Monetary, futuro compute)
- `priority` (Selection / Integer)

#### 4.2.5. Suitability & Compliance (núcleo)

No core, apenas o estado consolidado:
- `suitability_status` (Selection: válido, expirado, pendente, não iniciado)
- `suitability_expires_on` (Date)
- `has_pending_compliance` (Boolean, derivado de módulos satélites posteriormente)

Histórico detalhado ficará em `finance.suitability.history` e/ou em módulo `finance_compliance`.

#### 4.2.6. Ciclo de Vida do Cliente

- `lifecycle_status` (Selection: prospect, onboarding, active, dormant, churn)
- `lifecycle_stage_changed_on` (DateTime)
- `activated_on` (Date)
- `churned_on` (Date)
- `churn_reason_id` (Many2one → `finance.churn.reason`)

Modelo auxiliar `finance.churn.reason`:
- `name`
- `code`
- `active`

#### 4.2.7. Preferências de Relacionamento

- `preferred_channel` (Selection: email, phone, whatsapp, portal, presencial)
- `reporting_frequency` (Selection: mensal, trimestral, semestral, anual)
- `engagement_level` (Selection ou Integer: low/medium/high)

#### 4.2.8. LGPD / Privacidade

- `lgpd_consent_given` (Boolean)
- `lgpd_consent_date` (Date)
- `lgpd_opt_out` (Boolean)
- `lgpd_opt_out_date` (Date)
- Ganchos para **anonimização** (future wizard em `wizard/`)

### 4.3. Regras

- Constraint: apenas um `finance.profile` por `partner_id`.
- Record rules: isolamento por `company_id` quando necessário.
- Tracking (`mail.thread`) em campos críticos: ciclo de vida, suitability, LGPD.

---

## 5. Modelos Auxiliares

### 5.1. `finance.household`

Representa o "household" ou núcleo econômico familiar.

- `name`
- `company_id`
- `primary_profile_id` (Many2one → `finance.profile`)
- One2many → `profile_ids`
- Regras de integridade: evitar loops/dependências circulares.

### 5.2. `finance.goal`

Já descrito acima; fica neste módulo como estrutura básica de objetivos financeiros.

### 5.3. `finance.churn.reason`

Tabela estável de motivos de churn (pode ser populada via `data/*.xml`).

### 5.4. `finance.suitability.history` (opcional no core ou movido para compliance)

Se ficar no core, será apenas um log minimalista:

- `profile_id`
- `status_before`
- `status_after`
- `changed_on`
- `changed_by`
- `note`

Módulos de compliance podem herdar/expandir.

---

## 6. Fluxo de Dados: CRM → Core → Partner

### 6.1. Princípios

- `crm.lead` é **provisório**, `finance.profile` é **definitivo**.
- A conversão de lead (ganho) dispara a criação/população do `finance.profile` via módulo `finance_crm_integration` (não neste core).
- O core fornece apenas o modelo e os métodos utilitários para garantir integridade.

### 6.2. Responsabilidade do Core

- Expor métodos estáveis para criação/atualização de `finance.profile` dados:
  - Um `res.partner` existente.
  - Um dicionário de dados iniciais (patrimônio, objetivos, etc.).
- Garantir que não existam perfis duplicados.
- Fornecer APIs para que módulos satélites consultem/atualizem campos específicos sem quebrar integridade.

---

## 7. Validações e Regras de Negócio

### 7.1. Integridade

- Constraint de unicidade `partner_id` em `finance.profile`.
- Não permitir loops em `finance.household` (ex.: um household primário referindo-se a si mesmo de forma cíclica).
- Objetivos (`finance.goal`) não duplicados para o mesmo nome + prazo + valor (regra opcional).

### 7.2. Ciclo de Vida

- Não permitir `lifecycle_status = 'active'` se `suitability_status` não for válido.
- Não permitir `churn` sem `churn_reason_id`.
- Atualizar datas de marco automaticamente ao mudar o `lifecycle_status`.

### 7.3. Suitability

- Alteração de `suitability_status` deve ser rastreada (chatter) e registrada historicamente.
- Impedir alterações manuais diretas em certos campos quando módulos de compliance estiverem instalados (feito via herança neles, não no core).

### 7.4. LGPD

- Registro das datas de consentimento e opt-out.
- Hooks para wizard de anonimização futura.

---

## 8. Segurança e Acesso

- `finance.profile` com `_inherit = ['mail.thread', 'mail.activity.mixin']`.
- Grupos base (a definir futuramente):
  - `group_finance_user`
  - `group_finance_manager`
- `ir.model.access.csv` inicial minimalista permitindo apenas administrador acessar tudo; finetuning posterior.
- Regra multi-company: `_check_company_auto = True` onde aplicável.

---

## 9. Views e UI (alto nível, sem detalhe de código)

### 9.1. Formulário `finance.profile`

- Header limpo, focado na pessoa (`partner_id`) – SEM nome de empresa.
- Seções sugeridas (tabs ou groups):
  - Identificação & Household
  - Dados Pessoais
  - Dados Financeiros
  - Objetivos
  - Suitability & Compliance (resumo)
  - Ciclo de Vida
  - Preferências & LGPD

### 9.2. List / Search Views

- Lista com colunas principais: parceiro, advisor, status, patrimônio, AUM, lifecycle_status.
- Search view com filtros por: status, advisor, suitability_status, lifecycle_status.

---

## 10. Plano de Implementação por Fases

### Fase 0 – Infraestrutura do Módulo

- [x] Criar pasta `gz_finance_core/`.
- [x] Criar `__manifest__.py` minimalista (sem dependências complexas).
- [x] Criar `__init__.py`, estrutura de `models/`, `views/`, `security/`, `data/`, `wizard/`.
- [x] Criar este plano (`PLANO_MODULO.md`).

### Fase 1 – Modelo Base `finance.profile`

- [ ] Definir modelo `finance.profile` com campos:
  - Identificação & Relações mínimas.
  - Dados pessoais não sensíveis.
  - Dados financeiros consolidados básicos.
  - Ciclo de vida (sem regras complexas).
- [ ] Adicionar constraints principais (unicidade `partner_id`).
- [ ] Ativar tracking em campos críticos.
- [ ] Criar views básicas (form, list, search) apenas para uso interno/dev.

### Fase 2 – Modelos Auxiliares

- [ ] Implementar `finance.goal` e link com `finance.profile`.
- [ ] Implementar `finance.churn.reason` com dados em `data/*.xml`.
- [ ] Implementar `finance.household` minimalista.
- [ ] (Opcional nesta fase) Implementar `finance.suitability.history`.

### Fase 3 – Regras de Negócio & Validações

- [ ] Implementar regras de ciclo de vida (status + datas).
- [ ] Implementar validações básicas de suitability x lifecycle.
- [ ] Adicionar testes unitários simples (se aplicável).

### Fase 4 – LGPD & Privacidade (estrutura)

- [ ] Campos de consentimento, opt-out e datas.
- [ ] Ganchos para futura anonimização (sem lógica pesada ainda).

### Fase 5 – Integrações Internas (Preparação)

- [ ] Métodos de conveniência para criação/atualização segura de profile.
- [ ] Hooks para uso por `finance_crm_integration` e outros.

### Fase 6 – Polimento e Documentação

- [ ] Refinar views (UX, grupos, tooltips, help nos campos).
- [ ] Completar segurança (`ir.model.access.csv`, grupos padrão).
- [ ] Documentar extensões previstas para módulos satélites.

---

## 11. Decisões de Design Importantes

- `gz_finance_core` deve permanecer **minimalista**: sem lógica de CRM, investimentos ou compliance pesada.
- O módulo é pensado para Odoo 19, seguindo boas práticas:
  - `_inherit` correto em extensões futuras.
  - Campos computados com `@api.depends` e `store=True` quando usados em views/domínios.
  - Uso das novas convenções de views do Odoo 19 (sem attrs/states legados).
- Toda lógica de negócio mais rica (suitability engine, cálculos complexos, onboarding guiado) deve ser implementada em módulos específicos, herdando `finance.profile`.

---

## 12. Próximos Passos

1. Validar este plano funcional e técnico com o time.
2. Ajustar ou priorizar campos/regras conforme realidade do escritório.
3. Iniciar **Fase 1** implementando `finance.profile` de forma enxuta.
4. Iterar de forma incremental, sempre mantendo o módulo coeso e desacoplado.
