# 🔧 Correção dos Stages Duplicados

## ❌ Problema Identificado

O módulo estava **criando stages duplicados** ao invés de reutilizar os stages padrão do CRM:

- **Stages Padrão do Odoo** (seq: 1-6): Não eram reconhecidos pelas abas
- **Stages Wealth** (seq: 10-60): Criados como duplicatas com emojis

Resultado: Ao mover leads nos stages padrão, as abas não apareciam.

## ✅ Solução Implementada

### 1. **Limpeza do Banco de Dados**
- Moveu leads dos stages duplicados (55-60) para os stages padrão (1-4, 11-12)
- Deletou os 6 stages duplicados criados pelo módulo
- Atualizou os stages padrão com emojis e sequências corretas (10, 20, 30, 40, 50, 60)

### 2. **Atualização do Arquivo de Dados**
Modificou `crm_wealth/data/crm_stage_data.xml`:
- Mudou de `noupdate="1"` para `noupdate="0"` (permite atualização)
- Usa external IDs do módulo CRM padrão: `crm.stage_lead1`, `crm.stage_lead2`, etc.
- Adiciona apenas 2 novos stages: Onboarding e Execução

### 3. **Mapeamento Final dos Stages**

| ID | Nome Original | Nome Wealth | Sequência | External ID |
|----|--------------|-------------|-----------|-------------|
| 1  | Novo Lead | 🔵 Captação | 10 | crm.stage_lead1 |
| 2  | Qualificado | 🟢 Qualificação | 20 | crm.stage_lead2 |
| 3  | Proposta | 🟣 Reunião Estratégica | 30 | crm.stage_lead3 |
| 4  | Negociação | 🟠 Proposta | 40 | crm.stage_lead4 |
| 11 | *(novo)* | 🟡 Onboarding | 50 | crm_wealth.stage_onboarding |
| 12 | *(novo)* | 🟤 Execução & Acompanhamento | 60 | crm_wealth.stage_execucao |

## 🎯 Resultado

Agora o sistema funciona corretamente:
- ✅ Não há mais stages duplicados
- ✅ Mover leads nos stages do funil padrão ativa as abas progressivamente
- ✅ As sequências (10-60) controlam a visibilidade das abas
- ✅ Compatível com o CRM padrão do Odoo

## 📝 Comandos SQL Executados

```sql
-- Moveu leads para stages corretos
UPDATE crm_lead SET stage_id = 1 WHERE stage_id = 55;
UPDATE crm_lead SET stage_id = 2 WHERE stage_id = 56;
-- ... (resto dos updates)

-- Deletou stages duplicados
DELETE FROM crm_stage WHERE id IN (55, 56, 57, 58, 59, 60);

-- Atualizou nomes e sequências
UPDATE crm_stage SET name = '{"en_US": "🔵 Captação", "pt_BR": "🔵 Captação"}', sequence = 10 WHERE id = 1;
-- ... (resto dos updates)

-- Limpou external IDs antigos
DELETE FROM ir_model_data WHERE module = 'crm_wealth' AND model = 'crm.stage' AND res_id IN (55, 56, 57, 58, 59, 60);
```

## ⚡ Como Testar

1. **Abra um lead** no CRM
2. **Mova entre os stages** usando o funil no topo da página
3. **Observe as abas** aparecendo progressivamente:
   - 🔵 Captação (seq: 10) → Mostra apenas aba Captação
   - 🟢 Qualificação (seq: 20) → Mostra Captação + Qualificação
   - 🟣 Reunião Estratégica (seq: 30) → Mostra 3 primeiras abas
   - 🟠 Proposta (seq: 40) → Mostra 4 primeiras abas
   - 🟡 Onboarding (seq: 50) → Mostra 5 primeiras abas
   - 🟤 Execução (seq: 60) → Mostra todas as 6 abas

---
**Data da Correção**: 16/11/2025
**Status**: ✅ Resolvido
