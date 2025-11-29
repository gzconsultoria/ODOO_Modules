# Diretrizes Funcionais do `gz_finance_core`

> Visão funcional de alto nível, focada no dia a dia de um escritório de consultoria financeira e investimentos. Este documento **não é técnico**; serve como guia de produto/negócio para orientar todos os módulos.

---

## 1. Papel do Core no Dia a Dia

O `gz_finance_core` é o **registro mestre financeiro do cliente**. Ele não cuida de telas de CRM nem de operações de investimento, mas:

- Garante que **exista um único "cliente financeiro" por pessoa** (`finance.profile`).
- Armazena **todos os dados estáveis** de perfil, patrimônio, objetivos, ciclo de vida e compliance.
- Serve como **ponte** entre:
  - CRM (captação, qualificação, reuniões, propostas)
  - Investimentos (carteiras, posições, performance)
  - Compliance & Suitability
  - Documentos e Assinaturas
  - Portal do Cliente

Ou seja: tudo acontece **ao redor** do Core.

---

## 2. Jornada do Cliente no Escritório

Do ponto de vista funcional, a jornada típica é:

1. **Captação** (Marketing / CRM)
2. **Qualificação** (Perfil inicial, interesse, potencial)
3. **Reunião Estratégica** (Diagnóstico profundo)
4. **Proposta** (Plano de investimentos / serviço)
5. **Onboarding** (Documentos, cadastros, contas em corretoras)
6. **Suitability & Compliance** (Perfil de risco, questionários, KYC)
7. **Plano de Investimentos** (Alocação alvo, objetivos, horizonte)
8. **Execução & Acompanhamento** (Operações, rebalanceamento, revisões periódicas)

O `gz_finance_core` precisa **enxergar e consolidar** essa jornada, mesmo que a execução prática de cada etapa fique em módulos satélites.

---

## 3. Como o Core Enxerga Cada Etapa

### 3.1. Captação

**O que acontece no dia a dia:**
- Marketing gera leads (indicados, inbound, eventos, redes sociais).
- Time comercial faz o primeiro contato.

**Papel do Core:**
- Nesta fase, o cliente ainda **não é** um `finance.profile` obrigatório.
- O Core só precisa garantir que, quando o lead for convertido, não serão criados perfis duplicados.

**Diretrizes Core:**
- `crm.lead` pode existir sem `finance.profile`.
- Quando o lead "vira cliente" (ganho), módulo de integração deve:
  - Criar ou apontar para um `res.partner` existente.
  - Criar um `finance.profile` único associado a esse partner.
- Core expõe **regras de unicidade** e métodos de validação (ex.: CPF, e-mail, nome + data de nascimento) para evitar duplicidade de perfis.

### 3.2. Qualificação

**No dia a dia:**
- Time comercial coleta:
  - Renda aproximada
  - Patrimônio estimado
  - Capacidade de aporte
  - Horizonte de investimento
  - Nível de conhecimento financeiro
- Muitas vezes isso ainda é "informal" ou preliminar.

**Papel do Core:**
- Receber esses dados de forma consolidada **apenas quando fizer sentido**.
- Não guardar ruído operacional de CRM, apenas as conclusões relevantes.

**Diretrizes Core:**
- `finance.profile` armazena:
  - `estimated_net_worth`
  - `monthly_income`
  - `monthly_investment_capacity`
  - Indicadores de potencial (ex.: `internal_risk_score` inicial ou campo de segmentação).
- Informações muito voláteis (ex.: "está avaliando vender um imóvel este mês") devem ficar no CRM ou em módulos de planejamento, não no Core.

### 3.3. Reunião Estratégica

**No dia a dia:**
- Reunião (online/presencial) para entender:
  - Situação de vida (família, carreira, negócios)
  - Estrutura patrimonial
  - Objetivos principais (aposentadoria, filhos, imóveis, empresa)
  - Preocupações (risco, liquidez, sucessão)

**Papel do Core:**
- Tornar-se o lugar onde as **decisões estáveis** dessa conversa ficam registradas.

**Diretrizes Core:**
- Registrar no `finance.profile`:
  - Estrutura de `household` (quem faz parte do núcleo familiar econômico).
  - Objetivo(s) financeiro(s) principais via `finance.goal`.
  - Dados consolidados de patrimônio (não o detalhe de cada ativo).
- Notas detalhadas, atas e históricos de reunião podem ficar em módulos de CRM/atendimento (ex.: `mail.message` ligados a outros modelos), mas o **resumo estratégico** deve estar no Core.

### 3.4. Proposta

**No dia a dia:**
- Escritório monta uma proposta:
  - Tipo de serviço (consultoria, gestão, financial planning contínuo).
  - Nível de risco adequado.
  - Alocação alvo por classe de ativo.
  - Honorários / modelo de cobrança.

**Papel do Core:**
- Armazenar as **decisões finais** sobre:
  - Perfil de risco consolidado (não o questionário em si).
  - Objetivos alvo (valor, prazo, prioridade).
  - Parametrizações-chave que afetarão investimentos/compliance.

**Diretrizes Core:**
- `finance.profile` guarda campos como:
  - `internal_risk_score` ou status de risco consolidado.
  - Objetivos aprovados em `finance.goal`.
  - Eventual status de engajamento (ex.: se cliente aceitou avançar).
- Documentos de proposta, PDFs e versões ficam em módulos de documentos/assinatura; o Core só armazena o **estado resultante**.

### 3.5. Onboarding

**No dia a dia:**
- Coleta de documentos (RG, CPF, comprovante de endereço, renda).
- Abertura de conta(s) em corretora / banco.
- Cadastros em sistemas de parceiros.

**Papel do Core:**
- Saber **se o cliente está apto** a operar/investir do ponto de vista estrutural.

**Diretrizes Core:**
- Campos de estado, por exemplo:
  - `lifecycle_status` = `onboarding` / `active` / etc.
  - Campos booleanos ou agregados indicando pendências críticas (que podem ser abastecidos por módulos de compliance/documentos).
- O Core **não** deve guardar cópias de documentos binários nem fluxos de assinatura.
- Apenas armazena **resultado**: onboarding concluído, data de ativação, se há pendências importantes.

### 3.6. Suitability e Compliance

**No dia a dia:**
- Aplicação de questionário de perfil de investidor.
- Coleta de informações regulatórias: origem de recursos, PEP, restrições.
- Revisões periódicas (suitability expira).

**Papel do Core:**
- Manter o **estado atual** do suitability/compliance e referências temporais.

**Diretrizes Core:**
- Armazenar em `finance.profile`:
  - `suitability_status` (válido, expirado, pendente, não iniciado).
  - `suitability_expires_on`.
  - `is_pep` e bandeiras de risco relevantes.
- Módulos satélites de compliance/suitability devem:
  - Gerenciar questionários, scoring detalhado, anexos e revisões.
  - Atualizar o Core apenas com o **resultado final**.
- Regras chave:
  - Não permitir `lifecycle_status = active` se `suitability_status` não for adequado.
  - Registrar no chatter mudanças de estado para auditoria.

### 3.7. Plano de Investimentos

**No dia a dia:**
- Traduzir objetivos e perfil em um plano prático:
  - Alocação por classe de ativo.
  - Veículos sugeridos (fundos, ações, FII, renda fixa, previdência, offshore, etc.).
  - Horizonte temporal e marcos (ex.: aposentadoria em 20 anos).

**Papel do Core:**
- Ter **visão consolidada e estável** do que foi definido como plano.

**Diretrizes Core:**
- Registro de objetivos em `finance.goal` com:
  - `target_amount`, `target_date`, `priority`.
- Campos de visão macro no `finance.profile`, como:
  - `asset_allocation_snapshot` (ex.: renda fixa 40%, renda variável 30%, etc.).
  - `aum_total` (consolidado vinda de `finance_investments`).
- Os detalhes finos de alocação (por ativo, por conta, por corretora) ficam no módulo de investimentos; o Core guarda a visão "plano mestre".

### 3.8. Execução e Acompanhamento

**No dia a dia:**
- Execução de ordens via corretora/parceiros.
- Rebalanceamento periódico.
- Reuniões de revisão (trimestral, semestral, anual).
- Comunicação constante com o cliente.

**Papel do Core:**
- Ser a **linha do tempo estável** do relacionamento financeiro.

**Diretrizes Core:**
- Manter no `finance.profile`:
  - `lifecycle_status` (active, dormant, churn).
  - Datas importantes (ativação, dormência, churn).
  - `churn_reason_id` quando aplicável.
- Módulos de investimentos/compliance/CRM fazem:
  - Registro detalhado de operações, atividades, reuniões.
  - Dashboards operacionais.
- O Core foca em:
  - Estado atual do cliente.
  - Consolidado financeiro de alto nível.
  - Histórico de estados para auditoria (via chatter + modelos auxiliares de history).

---

## 4. Princípios Gerais para Todos os Módulos Satélites

1. **O Core nunca deve depender de fluxos específicos de um satélite.**
   - Ex.: se um escritório opera com 2 corretoras hoje e 5 amanhã, o `finance.profile` continua igual.

2. **Tudo que é volátil e operacional fica fora do Core.**
   - Tarefas, atividades, agendas, detalhes de cada ordem/ativo → outros módulos.

3. **O Core guarda o que é "verdade duradoura" sobre o cliente:**
   - Quem é, qual o papel econômico da família, qual o patrimônio aproximado, quais os grandes objetivos, qual o status de compliance, qual o estágio de relacionamento.

4. **O Core deve ser estável ao longo dos anos.**
   - Mudanças de produto/estratégia podem exigir novos módulos; o Core permanece como base.

5. **Toda integração externa (CRM, Portal, outras plataformas) fala com o Core como referência de cliente financeiro.**
   - `res.partner` é a pessoa/contato.
   - `finance.profile` é a visão financeira dessa pessoa.

---

## 5. Como Usar Estas Diretrizes na Fase de Desenvolvimento

- Ao desenhar qualquer nova funcionalidade, perguntar:
  1. "Isso é um dado duradouro do cliente?" → então provavelmente pertence ao Core.
  2. "Isso é um processo, tarefa ou detalhe operacional?" → então é de um módulo satélite.
  3. "Esse campo é essencial para compliance, risco ou ciclo de vida?" → deve ao menos ter um reflexo no Core.
- Garantir que o `finance.profile` tenha sempre:
  - Visão mínima das etapas que o cliente já passou.
  - Estado atual de elegibilidade, risco e relacionamento.

Estas diretrizes serão a **bússola funcional** para todas as próximas decisões de modelagem e implementação no ecossistema financeiro.
