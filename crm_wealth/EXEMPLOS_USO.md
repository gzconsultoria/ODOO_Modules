# Exemplos de Uso - CRM Wealth Management

Este documento fornece exemplos práticos de como usar o módulo CRM Wealth Management.

## 📋 Índice

1. [Fluxo Completo de um Lead](#fluxo-completo-de-um-lead)
2. [Configuração Inicial](#configuração-inicial)
3. [Casos de Uso Específicos](#casos-de-uso-específicos)
4. [Dicas e Truques](#dicas-e-truques)

---

## 🎯 Fluxo Completo de um Lead

### 1. Captação - Novo Lead Chegou

**Cenário:** Lead veio do Instagram interessado em investimentos.

```
CRM → Leads → Criar

Informações Básicas:
- Nome: João Silva
- Email: joao@email.com
- Telefone: +55 11 98765-4321
- Estágio: 🔵 Captação

Aba Captação:
- Origem do Lead: Instagram
- Momento Financeiro: Iniciando investimentos
- Patrimônio Aproximado: R$ 50.000 - R$ 200.000
- Renda Mensal: R$ 10.000 - R$ 20.000
- Interesses: [Bolsa de Valores, FIIs, Planejamento Financeiro]
```

**✅ Resultado:** Lead criado com informações básicas de captação.

---

### 2. Qualificação - Entendendo o Lead

**Ação:** Após primeira conversa, mova para estágio "🟢 Qualificação"

```
Aba Qualificação (agora visível):
- Perfil do Investidor: Moderado
- Dor Principal: Estratégia
- Objetivo Curto Prazo: "Começar a investir de forma estruturada 
  e aprender sobre diversificação"
- Objetivo Longo Prazo: "Alcançar independência financeira em 15 anos 
  para trabalhar meio período"
```

**✅ Resultado:** Lead qualificado com objetivos claros.

---

### 3. Reunião Estratégica - Diagnóstico

**Ação:** Após reunião de análise, mova para "🟣 Reunião Estratégica"

```
Aba Reunião Estratégica:

Diagnóstico:
- Situação Atual: "Tem R$ 150k em poupança e CDB. 
  Nunca investiu em renda variável. Organizado financeiramente."

- Pontos Fortes: "Disciplinado, consegue poupar 30% da renda. 
  Reserva de emergência constituída. Sem dívidas."

- Pontos a Melhorar: "Patrimônio concentrado em renda fixa conservadora. 
  Falta conhecimento sobre mercado. Medo de perder dinheiro."

- Oportunidades: "Grande potencial de crescimento com diversificação. 
  Perfil ideal para começar com FIIs e ações de dividendos."

Estratégias Recomendadas:
- [Renda Fixa, FIIs, Ações, ETFs]

Score de Potencial: ⭐⭐⭐⭐ 4 estrelas
```

**✅ Resultado:** Diagnóstico completo e estratégia definida.

---

### 4. Proposta - Apresentação do Plano

**Ação:** Mova para "🟠 Proposta"

```
Aba Proposta:
- Plano Sugerido: Plano Premium
- Valor da Proposta: R$ 497,00/mês
- Justificativa: "Plano Premium inclui: reuniões mensais, 
  rebalanceamento trimestral, acesso a grupo VIP, 
  suporte via WhatsApp, e relatórios personalizados."

Objeções Apresentadas:
- [Preço Alto, Preciso Pensar]

Notas (campo nativo do CRM):
"Cliente preocupado com mensalidade. Mostrei ROI 
comparando com custo de oportunidade de deixar 
dinheiro parado. Dei 3 dias para pensar."
```

**✅ Resultado:** Proposta registrada com objeções mapeadas.

---

### 5. Onboarding - Cliente Aceitou!

**Ação:** Cliente aceitou. Mova para "🟡 Onboarding"

```
Aba Onboarding:
☑ Suitability Oficial Preenchido: Sim

Documentos Entregues:
- [RG ou CNH, CPF, Comprovante de Residência, Extratos]

Perfil de Risco Final: Moderado

☑ Estrutura Inicial Montada: Sim

Contas de Corretoras:
- [Clear, XP Investimentos]

Notas:
"Abertura de conta na Clear concluída. 
Estratégia inicial definida: 60% RF, 30% FIIs, 10% Ações."
```

**✅ Resultado:** Cliente onboardado e pronto para começar.

---

### 6. Execução & Acompanhamento - Gestão Contínua

**Ação:** Mova para "🟤 Execução & Acompanhamento"

```
Aba Execução:
- Valor Investido Atual: R$ 150.000,00
- Distribuição de Portfólio: "60% Renda Fixa (CDB, Tesouro Selic), 
  30% FIIs (HGLG11, MXRF11, KNRI11), 10% Ações (ITUB4, BBAS3, WEGE3)"

Acompanhamento Mensal:
┌──────────────┬──────────────────────┬─────────────┬──────────────┬─────────────┐
│ Data         │ Título               │ Valor       │ Rentab. (%)  │ Satisfação  │
├──────────────┼──────────────────────┼─────────────┼──────────────┼─────────────┤
│ 01/12/2025   │ Reunião Mensal #1    │ 150.000,00  │ 0,00         │ Satisfeito  │
│ 01/01/2026   │ Reunião Mensal #2    │ 155.200,00  │ 3,47         │ Muito Sat.  │
│ 01/02/2026   │ Reunião Mensal #3    │ 158.900,00  │ 2,38         │ Muito Sat.  │
└──────────────┴──────────────────────┴─────────────┴──────────────┴─────────────┘

Detalhes da última reunião (01/02/2026):
- Mudanças Realizadas: "Aporte de R$ 2.000. Rebalanceamento: 
  vendeu parte da RF para comprar mais FIIs (oportunidade)."
- Próximos Passos: "Estudar sobre ações internacionais. 
  Considerar abertura de conta na Avenue."
- Satisfação: Muito Satisfeito

Histórico de Mudanças:
"01/12: Setup inicial 60/30/10
 15/01: Aporte R$ 3.000 em FIIs
 01/02: Rebalanceamento -5% RF +5% FIIs (agora 55/35/10)"
```

**✅ Resultado:** Cliente em gestão ativa com histórico completo.

---

## ⚙️ Configuração Inicial

### Cadastrar Novos Interesses

```
CRM → Configuração → Wealth Management → Interesses → Criar

Exemplo:
- Nome: Criptomoedas
- Ativo: ✓
```

### Cadastrar Nova Estratégia

```
CRM → Configuração → Wealth Management → Estratégias → Criar

Exemplo:
- Nome: Stocks Internacionais
- Descrição: "Ações americanas via BDRs ou Avenue/Nomad"
- Ativo: ✓
```

### Personalizar Objeções

```
CRM → Configuração → Wealth Management → Objeções → Criar

Exemplo:
- Nome: "Não tenho dinheiro agora"
- Tratativa Padrão: "Entender quando terá. Oferecer plano 
  de reserva de emergência. Manter no funil para follow-up futuro."
```

---

## 💡 Casos de Uso Específicos

### Caso 1: Lead de Alto Patrimônio

```
Captação:
- Patrimônio: Acima de R$ 1.000.000
- Renda: Acima de R$ 50.000
- Interesse: [Gestão de Patrimônio, Proteção Patrimonial]

Qualificação:
- Perfil: Qualificado
- Dor: Tempo (não tem tempo para gerenciar)

Proposta:
- Plano: Gestão Completa
- Valor: R$ 2.500/mês ou 0,5% a.a. sobre AUM
```

### Caso 2: Lead Iniciante sem Recursos

```
Captação:
- Patrimônio: Até R$ 50.000
- Renda: Até R$ 5.000
- Interesse: [Planejamento Financeiro, Organização]

Qualificação:
- Dor: Organização financeira
- Objetivo CP: Criar reserva de emergência

Proposta:
- Plano: Mentoria (valor acessível)
- Foco: Educação e organização antes de investir
```

### Caso 3: Lead que Quer FIRE

```
Qualificação:
- Objetivo LP: "Aposentar em 10 anos aos 45 anos (FIRE)"

Reunião Estratégica:
- Estratégias: [Ações, FIIs, Renda Fixa, ETFs]
- Score: ⭐⭐⭐⭐⭐ 5 estrelas

Proposta:
- Plano: Plano FIRE (customizado)
- Acompanhamento trimestral + projeções
```

---

## 🎨 Dicas e Truques

### 1. Usar Tags do CRM Nativo

Além dos campos customizados, use as tags nativas:
```
Tags Sugeridas:
- VIP
- Hot Lead
- Referência Indicou
- Evento XYZ
```

### 2. Atividades Automáticas

Configure atividades por estágio:
```
Settings → Technical → Automation Rules

Quando: Lead entra em "Qualificação"
Fazer: Criar atividade "Agendar Reunião Estratégica" para 2 dias depois
```

### 3. Filtros Personalizados

Crie filtros salvos:
```
Meus Leads Hot:
- Score de Potencial = 4 ou 5 estrelas
- Estágio = Proposta ou Reunião Estratégica

Leads Estagnados:
- Última Atualização > 7 dias
- Estágio != Execução
```

### 4. Relatórios Úteis

```
Relatórios → Funil de Vendas:
- Agrupar por Estágio
- Filtrar por período
- Ver taxa de conversão por estágio
```

### 5. Pipeline Kanban

```
CRM → Pipeline

Arrastar e soltar leads entre estágios
Cores automáticas por prioridade
```

---

## 📊 Métricas Sugeridas

### KPIs a Acompanhar

1. **Taxa de Conversão por Estágio:**
   - Captação → Qualificação: ~60%
   - Qualificação → Reunião: ~70%
   - Reunião → Proposta: ~80%
   - Proposta → Onboarding: ~40%
   - Onboarding → Execução: ~95%

2. **Tempo Médio por Estágio:**
   - Captação: 1-2 dias
   - Qualificação: 2-3 dias
   - Reunião: 3-7 dias
   - Proposta: 3-14 dias
   - Onboarding: 7-30 dias

3. **Valor Médio por Cliente (AUM):**
   - Acompanhar via campo "Valor Investido Atual"

4. **Satisfação do Cliente:**
   - Acompanhar via acompanhamentos mensais

---

## 🤝 Integrações Futuras

### Possíveis Integrações

1. **WhatsApp Business:**
   - Mensagens automáticas por estágio
   
2. **API de Corretoras:**
   - Sincronizar portfólio automaticamente

3. **Google Calendar:**
   - Reuniões mensais automáticas

4. **Email Marketing:**
   - Campanhas segmentadas por estágio

---

## 📚 Recursos Adicionais

- [README Principal](../README.md)
- [Boas Práticas Odoo 19](BOAS_PRATICAS_ODOO19.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
- [Documentação Odoo](https://www.odoo.com/documentation/19.0/)

---

**Dúvidas?** Abra uma issue no GitHub ou entre em contato!
