# GZ Finance CRM

**Versão:** 19.0.1.0.0  
**Categoria:** Sales/CRM  
**Autor:** GZ Consultoria

## 📋 Visão Geral

Módulo CRM especializado para **consultoria financeira e wealth management**, integrado perfeitamente com o `gz_finance_core`.

### Objetivo Principal

Gerenciar o **pipeline de vendas** de novos clientes de consultoria financeira, com integração automática para criação de **perfis financeiros completos** quando o lead é convertido.

---

## 🎯 Funcionalidades Principais

### 1. 🔥 Pipeline de Vendas Especializado

**8 Estágios Customizados** (criar manualmente no Odoo CRM):

1. **Captação** (seq 10) - Primeiro contato, coleta de interesse inicial
2. **Qualificação** (seq 20) - Validação de perfil e potencial
3. **Reunião** (seq 30) - Apresentação e diagnóstico
4. **Onboarding** (seq 40, `is_won=True`) ✅ - Cliente ganho!
5. **Aporte Inicial** (seq 50) - Transferência de recursos
6. **Proposta de Alocação** (seq 60) - Apresentação de portfólio
7. **Em Acompanhamento** (seq 70) - Gestão ativa
8. **Alerta de Churn** (seq 80) - Risco de perda

### 2. 🤖 Popup Automático de Criação de Perfil

**Trigger:** Quando lead atinge estágio **Onboarding** (`is_won=True`)

**Comportamento:**
- Se o cliente **NÃO tem** perfil financeiro → abre popup
- Popup pergunta: **"Deseja criar um perfil financeiro agora?"**
- **SIM** → Cria perfil + abre formulário em modo edição
- **NÃO** → Fecha popup, pode criar depois via botão

### 3. 💼 Botão Inteligente "PERFIL FINANCEIRO"

**Localização:** Button box do formulário do lead

**Comportamento Inteligente:**

| Situação | Badge | Ação ao Clicar |
|----------|-------|----------------|
| ✅ **TEM** perfil | 🟢 "Perfil Ativo" + ID | Abre perfil existente (readonly) |
| ❌ **NÃO TEM** perfil | ⚪ "Criar Perfil" | Cria perfil + abre em modo edição |

### 4. 📊 Campos de Qualificação Comercial

**Aba: 💰 Qualificação Financeira**

#### Estimativas Iniciais
- `estimated_wealth` - Patrimônio estimado (bruto, para qualificação)
- `estimated_income_range` - Faixa de renda mensal

#### Perfil e Urgência
- `preliminary_risk_profile` - Perfil preliminar (Conservador/Moderado/Arrojado)
- `main_pain_point` - Dor principal do cliente
- `urgency_level` - Baixa/Média/Alta

#### Interesses e Objeções
- `investment_interest_ids` - Tags de interesses (Renda Fixa, Ações, FIIs, etc.)
- `objection_ids` - Tags de objeções levantadas

#### Proposta Comercial
- `proposal_sent_date` - Data de envio da proposta
- `proposed_fee` - Fee proposto (%)
- `competitor_comparison` - Concorrentes mencionados

#### Score e Temperatura
- `lead_score` - 0-100 (calculado automaticamente)
- `lead_temperature` - 🔵 Frio / 🟡 Morno / 🔴 Quente

---

## 🔗 Integração com Finance Core

### Princípio: ZERO Duplicação

**CRM** → Dados **temporários** de qualificação comercial  
**Finance Core** → Dados **permanentes** (SSOT - Single Source of Truth)

### Transferência de Dados (One-Way)

**Quando:** Ao criar perfil financeiro (popup ou botão)

**O que é transferido:**
```python
CRM → Finance Core
├── preliminary_risk_profile → risk_profile
├── expected_revenue → proposal_amount
├── proposed_fee → management_fee
├── proposal_sent_date → proposal_date
└── estimated_wealth → primeiro snapshot de patrimônio
```

### Campos que FICAM APENAS no CRM
- `investment_interest_ids` (tags comerciais)
- `objection_ids` (vendas)
- `urgency_level` (pipeline)
- `main_pain_point` (vendas)
- `competitor_comparison` (vendas)
- `lead_score` e `lead_temperature` (qualificação)

---

## 📦 Modelos Incluídos

### `crm.lead` (herança)
- Adiciona campos de qualificação financeira
- Popup automático no estágio Onboarding
- Botão inteligente "Perfil Financeiro"
- Cálculo de score e temperatura

### `finance.crm.interest`
- Tags de interesses de investimento
- Exemplos demo: Renda Fixa, Ações, FIIs, Fundos, Previdência, Cripto, Internacional

### `finance.crm.objection`
- Tags de objeções comerciais
- Exemplos demo: Preço alto, Consultar cônjuge, Comparando, Não urgente, Falta conhecimento
- Campo `suggested_response` com scripts de contorno

### `finance.profile.wizard` (transient)
- Popup de criação de perfil financeiro
- Preview de informações do lead
- Opção "Criar agora" ou "Depois"

---

## 🚀 Instalação

### 1. Instalar Módulo

```bash
# Via interface
Apps → Atualizar lista → Buscar "GZ Finance CRM" → Instalar

# Via linha de comando
docker exec odoo_modules-web-1 odoo -i gz_finance_crm -d nome_database
```

### 2. Criar Estágios do Pipeline (MANUAL)

**Ir em:** CRM → Configuração → Estágios do Pipeline

**Criar 8 estágios:**

| Nome | Sequência | is_won |
|------|-----------|---------|
| Captação | 10 | ❌ |
| Qualificação | 20 | ❌ |
| Reunião | 30 | ❌ |
| **Onboarding** | 40 | ✅ **TRUE** |
| Aporte Inicial | 50 | ❌ |
| Proposta de Alocação | 60 | ❌ |
| Em Acompanhamento | 70 | ❌ |
| Alerta de Churn | 80 | ❌ |

⚠️ **CRÍTICO:** Estágio "Onboarding" DEVE ter `is_won=True` para trigger do popup!

### 3. Configurar Dados Demo (Opcional)

Os seguintes dados demo são criados automaticamente:

**Interesses:** Renda Fixa, Ações, FIIs, Fundos, Previdência, Cripto, Internacional  
**Objeções:** Preço alto, Consultar cônjuge, Comparando, Não urgente, Falta conhecimento

**Editar em:** CRM → Configuração → Finance CRM

---

## 📖 Casos de Uso

### Caso 1: Lead Novo → Conversão

1. Criar novo lead em "Captação"
2. Preencher aba "💰 Qualificação Financeira"
   - Patrimônio estimado
   - Interesses
   - Perfil preliminar
3. Mover pelo pipeline (Qualificação → Reunião)
4. Ao chegar em **Onboarding** → Popup aparece
5. Clicar "Sim" → Perfil criado automaticamente
6. Formulário abre para preenchimento completo

### Caso 2: Criar Perfil Via Botão

1. Lead em qualquer estágio
2. Clicar botão "PERFIL FINANCEIRO"
3. Se não tem perfil → cria automaticamente
4. Se já tem perfil → abre existente

### Caso 3: Adiar Criação de Perfil

1. Lead chega em Onboarding → Popup aparece
2. Clicar "Não"
3. Popup fecha, nada é criado
4. **Depois:** Clicar botão "Criar Perfil" quando quiser

---

## 🔐 Permissões

### Grupos de Segurança

**Leitura/Escrita:**
- `crm.group_crm_user` (CRM User)
- `gz_finance_core.group_finance_user` (Finance User)

**Criação/Deleção:**
- `crm.group_crm_manager` (CRM Manager)

### Visibilidade do Botão

O botão "PERFIL FINANCEIRO" só aparece para usuários com grupo `gz_finance_core.group_finance_user`.

---

## 🧪 Testes

### Checklist de Validação

- [ ] Popup aparece ao atingir estágio Onboarding
- [ ] Popup não aparece se já tem perfil
- [ ] Botão mostra "Criar Perfil" quando não tem
- [ ] Botão mostra "Perfil Ativo" + ID quando tem
- [ ] Clicar "Sim" no popup cria perfil
- [ ] Clicar "Não" no popup fecha sem criar
- [ ] Botão cria perfil quando não existe
- [ ] Botão abre perfil quando existe
- [ ] Dados são transferidos corretamente (risk_profile, proposal_amount, etc.)
- [ ] Snapshot de patrimônio é criado com estimated_wealth
- [ ] Score do lead é calculado automaticamente
- [ ] Temperatura (frio/morno/quente) atualiza baseado no score

---

## 📊 Cálculo de Score do Lead

**Fórmula (0-100 pontos):**

| Critério | Pontos |
|----------|--------|
| **Patrimônio Estimado** | **40 pontos** |
| - R$ 5M+ | 40 |
| - R$ 1M - R$ 5M | 30 |
| - R$ 500k - R$ 1M | 20 |
| - Abaixo R$ 500k | 10 |
| **Urgência** | **30 pontos** |
| - Alta | 30 |
| - Média | 20 |
| - Baixa | 10 |
| **Interesses Definidos** | **20 pontos** |
| - 3+ interesses | 20 |
| - 1-2 interesses | 10 |
| **Perfil de Risco Definido** | **10 pontos** |
| - Sim | 10 |

**Temperatura:**
- 🔴 **Quente:** Score ≥ 70
- 🟡 **Morno:** Score 40-69
- 🔵 **Frio:** Score < 40

---

## 🛠️ Dependências

- `crm` (Odoo CRM nativo)
- `gz_finance_core` (v19.0.1.1.0+)

---

## 📝 Changelog

### v19.0.1.0.0 (2025-11-29)
- ✨ Versão inicial
- 🎯 Pipeline de 8 estágios
- 🤖 Popup automático em Onboarding
- 💼 Botão inteligente "Perfil Financeiro"
- 📊 Sistema de score e temperatura de leads
- 🏷️ Tags de interesses e objeções
- 🔗 Integração perfeita com Finance Core

---

## 🤝 Suporte

**Desenvolvedor:** GZ Consultoria  
**Licença:** LGPL-3  
**Versão Odoo:** 19.0

---

## ⚠️ Avisos Importantes

1. **Estágio Onboarding:** DEVE ter `is_won=True` para trigger funcionar
2. **Sem Duplicação:** NÃO criar campos que já existem no Finance Core
3. **Dados CRM:** São temporários, apenas para qualificação comercial
4. **SSOT:** Finance Core é a fonte única de verdade para dados permanentes
5. **One-Way:** Transferência CRM → Finance Core ocorre UMA VEZ (na criação)

---

## 📚 Documentação Adicional

- [Finance Core README](../gz_finance_core/README.md)
- [Comparativo CRM Wealth vs Finance Core](../COMPARATIVO_CRM_WEALTH_vs_FINANCE_CORE.md)
- [Ecossistema Finance](../ECOSSISTEMA_FINANCE_vs_CRM_WEALTH.md)
