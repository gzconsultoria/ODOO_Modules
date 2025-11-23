# Finance CRM Integration

**Versão:** 1.0  
**Autor:** GZ Consultoria  
**Categoria:** Sales / Financial Planning  
**Licença:** LGPL-3  

## 📋 Visão Geral

Módulo de integração entre **CRM Nativo do Odoo** e **Finance Core** que:

1. **Sincroniza automaticamente** o perfil financeiro com o estágio do Lead no CRM
2. **Cria Finance Profile** automaticamente quando Lead é marcado como ganho (`is_won=True`)
3. **Atualiza visibilidade de abas** conforme Lead avança no funil de vendas baseado em `stage.sequence`

## ⚠️ IMPORTANTE: Módulo Independente

Este módulo **NÃO depende de `crm_wealth`**. Ele funciona com:

- ✅ **CRM Nativo do Odoo** (qualquer versão)
- ✅ **CRM Wealth** (se instalado, copia campos extras automaticamente)
- ✅ **Qualquer customização de CRM** que tenha `stage.sequence`

### Como Funciona

O módulo usa **detecção inteligente de campos** (`hasattr()`):

```python
# Se campo existe no Lead → copia para Finance Profile
if hasattr(self, 'cliente_nascimento') and self.cliente_nascimento:
    vals['client_birthdate'] = self.cliente_nascimento
    
# Se campo NÃO existe → simplesmente ignora (sem erros)
```

**Resultado:**
- Com CRM nativo: cria Finance Profile básico com partner, advisor, investor_type
- Com CRM Wealth: copia também dados pessoais, objetivos, diagnóstico, proposta, etc.
- Com outro CRM customizado: copia campos que coincidirem com os nomes esperados

## 🎯 Funcionamento

### Funil de Vendas → Visibilidade de Abas

A visibilidade das abas no Finance Profile é controlada pelo campo `stage.sequence` do Lead no CRM.

**Regra Simples:** Quanto maior a sequência do estágio, mais abas ficam visíveis.

| Sequence | Aba Visível no Finance Profile                          |
|----------|----------------------------------------------------------|
| >= 10    | 👤 Dados Pessoais                                        |
| >= 20    | + 🎯 Objetivos                                           |
| >= 30    | + 🔍 Diagnóstico                                         |
| >= 40    | + 💼 Proposta                                            |
| >= 50    | + 🟡 Onboarding                                          |
| >= 60    | + 🟤 Execução & Acompanhamento (cliente ativo)           |

**Exemplo com estágios padrão do CRM:**

```
Novo (seq 1)           → Nenhuma aba visível
Qualificado (seq 5)    → Nenhuma aba visível  
Proposta (seq 10)      → Dados Pessoais
Negociação (seq 20)    → Dados Pessoais + Objetivos
Ganho (is_won=True)    → Finance Profile criado automaticamente
```

**Exemplo com estágios customizados (tipo CRM Wealth):**

```
🔵 Captação (seq 10)            → Dados Pessoais
🟢 Qualificação (seq 20)         → + Objetivos
🟣 Reunião Estratégica (seq 30)  → + Diagnóstico
🟠 Proposta (seq 40)             → + Proposta
🟡 Onboarding (seq 50)           → + Onboarding
🟤 Execução (seq 60, is_won)     → Todas as abas
```

### Sincronização Automática

```python
# Quando Lead muda de estágio
Lead.stage_id = stage_execucao
  ↓
Finance Profile criado/atualizado automaticamente
  ↓
profile.stage_sequence = 60
  ↓
Todas as abas ficam visíveis
```

## 🔧 Campos Sincronizados

### CRM Lead → Finance Profile

| Campo CRM                  | Campo Finance Profile         | Mapeamento                          |
|----------------------------|-------------------------------|-------------------------------------|
| `partner_id`               | `partner_id`                  | Direto                              |
| `user_id`                  | `advisor_id`                  | Consultor responsável               |
| `cliente_nascimento`       | `client_birthdate`            | Data de nascimento                  |
| `estado_civil`             | `marital_status`              | Estado civil                        |
| `conjuge_nome`             | `spouse_name`                 | Nome do cônjuge                     |
| `conjuge_nascimento`       | `spouse_birthdate`            | Data nascimento cônjuge             |
| `filhos_qtd`               | `children_count`              | Quantidade de filhos                |
| `filhos_nomes`             | `children_names`              | Nomes dos filhos                    |
| `time_coracao`             | `favorite_team`               | Time do coração                     |
| `hobbies`                  | `hobbies`                     | Hobbies/Interesses                  |
| `objetivo_principal`       | `main_goal`                   | Objetivo principal                  |
| `valor_objetivo`           | `goal_amount`                 | Valor do objetivo                   |
| `prazo_objetivo`           | `goal_deadline_years`         | Prazo em anos                       |
| `diagnostico_situacao`     | `diagnosis_current_situation` | Situação atual                      |
| `diagnostico_forcas`       | `diagnosis_strengths`         | Pontos fortes                       |
| `diagnostico_fraquezas`    | `diagnosis_weaknesses`        | Pontos fracos                       |
| `diagnostico_oportunidades`| `diagnosis_opportunities`     | Oportunidades                       |
| `data_diagnostico`         | `diagnosis_date`              | Data do diagnóstico                 |
| `plano_contrato`           | `contract_plan`               | Plano contratado                    |
| `valor_proposta`           | `proposal_amount`             | Valor da proposta                   |
| `fee_gestao`               | `management_fee`              | Taxa de gestão (%)                  |
| `tipo_contrato`            | `contract_type`               | Tipo de contrato                    |
| `data_proposta`            | `proposal_date`               | Data da proposta                    |
| `justificativa_proposta`   | `proposal_justification`      | Justificativa                       |
| `data_reuniao`             | `meeting_date`                | Data da reunião                     |
| `estrategias_discutidas`   | `meeting_strategies_discussed`| Estratégias discutidas              |
| `objecoes_identificadas`   | `meeting_objections`          | Objeções identificadas              |
| `score_potencial`          | `potential_score`             | Score de potencial                  |

## 📦 Dependências

- `crm` - CRM nativo do Odoo (já vem instalado por padrão)
- `finance_core` - Perfis financeiros de clientes

**Nota:** `crm_wealth` é **OPCIONAL**. Se instalado, campos extras serão copiados automaticamente.

## 🚀 Instalação

```bash
# Atualizar módulo
docker exec odoo_modules-web-1 odoo -u finance_crm_integration -d nome_database
```

## 💡 Casos de Uso

### 1. Lead avança para Execução
```python
# Usuário arrasta Lead para estágio "Execução & Acompanhamento"
lead.stage_id = stage_execucao

# Sistema automaticamente:
# 1. Cria Finance Profile se não existir
# 2. Associa profile.crm_lead_id = lead
# 3. Copia todos os dados do Lead para o Profile
# 4. Todas as abas ficam visíveis (stage_sequence = 60)
```

### 2. Lead retorna para estágio anterior
```python
# Usuário move Lead de volta para "Proposta"
lead.stage_id = stage_proposta

# Sistema automaticamente:
# 1. profile.stage_sequence atualiza para 40
# 2. Abas Onboarding e Execução ficam ocultas
# 3. Dados permanecem salvos
```

### 3. Consulta reversa
```python
# No Finance Profile, ver qual Lead originou
profile.crm_lead_id  # → Link direto para oportunidade no CRM
```

## 🔐 Permissões

Mesmas permissões dos módulos base:
- `group_finance_consultant` - Acesso total
- `group_finance_compliance` - Leitura de compliance

## 📚 Documentação Relacionada

- [Finance Core - Documentação](../finance_core/README.md)
- [Odoo CRM - Documentação Oficial](https://www.odoo.com/documentation/19.0/applications/sales/crm.html)

**Referências para CRM Wealth (opcional):**
- Se você tiver `crm_wealth` instalado, veja: `../crm_wealth/BOAS_PRATICAS_ODOO19.md`
- Plano de integração usado como base: `../PLANO_INTEGRACAO_CRM_WEALTH_FINANCE_CORE.md`
