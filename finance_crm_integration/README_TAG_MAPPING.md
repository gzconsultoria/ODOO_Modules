# 🏷️ Mapeamento de Tags Many2many: CRM Wealth → Finance Profile

## Visão Geral

O módulo `finance_crm_integration` sincroniza **tags Many2many** entre CRM Wealth e Finance Profile usando **mapeamento por nome**.

### Como Funciona

1. **Quando um Lead é ganho**, o método `_sync_to_finance_profile()` é acionado
2. O método `_prepare_finance_profile_vals()` mapeia campos Many2many
3. **Para cada tag do CRM Wealth**, busca tag equivalente no Finance Profile por nome (case-insensitive)
4. Se encontrar, **cria link Many2many**
5. Se NÃO encontrar, **ignora silenciosamente** (sem erros)

---

## 🔄 Mapeamentos Implementados

### 1️⃣ Interesses
```python
CRM Wealth: crm.wealth.interesse
Finance Profile: finance.interest.tag
Campo: investor_interests_ids
```

**Exemplo:**
- CRM Wealth: Lead tem tag "Renda Fixa"
- Finance Profile: Busca `finance.interest.tag` com nome "Renda Fixa"
- Se existe → adiciona ao campo `investor_interests_ids`

---

### 2️⃣ Estratégias
```python
CRM Wealth: crm.wealth.estrategia
Finance Profile: finance.strategy.tag
Campo: recommended_strategies_ids
```

**Exemplo:**
- CRM Wealth: Lead tem tag "Buy and Hold"
- Finance Profile: Busca `finance.strategy.tag` com nome "Buy and Hold"
- Se existe → adiciona ao campo `recommended_strategies_ids`

---

### 3️⃣ Objeções
```python
CRM Wealth: crm.wealth.objecao
Finance Profile: finance.objection.tag
Campo: proposal_objections_ids
```

**Exemplo:**
- CRM Wealth: Lead tem tag "Preço Alto"
- Finance Profile: Busca `finance.objection.tag` com nome "Preço Alto"
- Se existe → adiciona ao campo `proposal_objections_ids`

---

## 📋 Tags Pré-cadastradas

O arquivo `data/finance_tag_mapping.xml` cria tags padrão que correspondem às do CRM Wealth:

### Interesses (8 tags)
- ✅ Renda Fixa
- ✅ Ações
- ✅ Fundos Imobiliários
- ✅ Previdência Privada
- ✅ Criptomoedas
- ✅ Investimentos no Exterior
- ✅ Planejamento Financeiro
- ✅ Planejamento Sucessório

### Estratégias (7 tags)
- ✅ Buy and Hold
- ✅ Dividendos
- ✅ Growth Investing
- ✅ Value Investing
- ✅ Diversificação
- ✅ Alocação de Ativos
- ✅ Rebalanceamento

### Objeções (7 tags)
- ✅ Preço Alto
- ✅ Falta de Confiança
- ✅ Sem Tempo
- ✅ Falta de Conhecimento
- ✅ Precisa Consultar Terceiros
- ✅ Percepção de Risco
- ✅ Sem Urgência

---

## 🛠️ Adicionando Novas Tags

### Opção 1: Via Interface Odoo
1. Acesse **Settings → Technical → Database Structure → Models**
2. Busque por:
   - `finance.interest.tag`
   - `finance.strategy.tag`
   - `finance.objection.tag`
3. Adicione novos registros manualmente

### Opção 2: Via XML (Recomendado)
Edite `data/finance_tag_mapping.xml`:

```xml
<record id="finance_interest_nova_tag" model="finance.interest.tag">
    <field name="name">Nome da Nova Tag</field>
</record>
```

**Importante:** Use **EXATAMENTE o mesmo nome** que existe no CRM Wealth para o mapeamento funcionar.

---

## 🔍 Como Verificar se Funciona

### Teste 1: Lead com Tags no CRM Wealth

1. **Crie um Lead no CRM**
2. **Vá para aba "🔵 Captação"** (se módulo CRM Wealth instalado)
3. **Adicione tags:**
   - Interesses: "Renda Fixa", "Ações"
   - Estratégias: "Buy and Hold"
   - Objeções: "Preço Alto"
4. **Mova Lead para estágio "🟤 Execução"** (is_won=True)
5. **Veja Finance Profile criado com as mesmas tags**

### Teste 2: Verificar Logs

```python
# No Finance Profile, adicione log temporário:
def _prepare_finance_profile_vals(self):
    # ... código existente ...
    
    if hasattr(self, 'interesse_inicial') and self.interesse_inicial:
        _logger.info("🏷️ Tags CRM: %s", self.interesse_inicial.mapped('name'))
        # ... código de mapeamento ...
        _logger.info("🏷️ Tags Finance: %s", interesse_ids)
```

---

## ⚠️ Limitações Conhecidas

### 1. **Mapeamento é unidirecional** (CRM → Finance)
- ✅ Lead → Finance Profile: **FUNCIONA**
- ❌ Finance Profile → Lead: **NÃO IMPLEMENTADO**

**Solução futura:** Adicionar `write()` override no Finance Profile para sincronizar de volta.

### 2. **Tags devem ter nomes IGUAIS**
- ✅ "Renda Fixa" (CRM) → "Renda Fixa" (Finance): **FUNCIONA**
- ❌ "Renda Fixa" (CRM) → "RF" (Finance): **NÃO FUNCIONA**

**Solução:** Use nomes padronizados em ambos os módulos.

### 3. **Tags não são criadas automaticamente**
- Se tag existe no CRM mas NÃO existe no Finance → **IGNORA**
- Não gera erro, mas tag não é copiada

**Solução:** Pré-cadastre todas as tags possíveis em `data/finance_tag_mapping.xml`

---

## 💡 Boas Práticas

### ✅ DO (Faça isso)
1. **Mantenha tags sincronizadas** entre CRM Wealth e Finance Core
2. **Use nomes descritivos e padronizados** ("Renda Fixa" melhor que "RF")
3. **Pré-cadastre tags comuns** no XML de dados
4. **Use busca case-insensitive** (`=ilike`) para flexibilidade
5. **Documente tags customizadas** no README

### ❌ DON'T (Evite isso)
1. ❌ Criar tags manualmente sem padronização
2. ❌ Usar nomes diferentes para mesma tag
3. ❌ Esperar que tags sejam criadas automaticamente
4. ❌ Modificar código de mapeamento sem testar
5. ❌ Deletar tags que já estão em uso

---

## 🧪 Testes Automatizados (Futuro)

```python
def test_tag_mapping_interesses(self):
    """Testa mapeamento de interesse_inicial → investor_interests_ids"""
    
    # Criar tag no CRM
    crm_tag = self.env['crm.wealth.interesse'].create({'name': 'Renda Fixa'})
    
    # Criar tag no Finance
    finance_tag = self.env['finance.interest.tag'].create({'name': 'Renda Fixa'})
    
    # Criar Lead com tag
    lead = self.env['crm.lead'].create({
        'name': 'Test Lead',
        'interesse_inicial': [(4, crm_tag.id)],
    })
    
    # Sincronizar
    lead._sync_to_finance_profile()
    
    # Verificar
    self.assertIn(finance_tag, lead.finance_profile_id.investor_interests_ids)
```

---

## 📊 Estatísticas de Mapeamento

Para ver quantas tags foram mapeadas:

```python
# Executar no shell Odoo
finance_profiles = env['finance.profile'].search([])

total_interests = sum(len(p.investor_interests_ids) for p in finance_profiles)
total_strategies = sum(len(p.recommended_strategies_ids) for p in finance_profiles)
total_objections = sum(len(p.proposal_objections_ids) for p in finance_profiles)

print(f"📊 Interesses mapeados: {total_interests}")
print(f"📊 Estratégias mapeadas: {total_strategies}")
print(f"📊 Objeções mapeadas: {total_objections}")
```

---

## 🚀 Roadmap

### Versão Futura (v2.0)
- [ ] **Sincronização bidirecional** (Finance → CRM também)
- [ ] **Auto-criação de tags** se não existirem
- [ ] **Mapeamento por código** além de nome
- [ ] **Dashboard de tags** mais usadas
- [ ] **Sugestão inteligente** de tags baseada em ML

---

## 📞 Suporte

**Dúvidas sobre mapeamento de tags?**
- 📧 Email: suporte@gzconsultoria.com.br
- 📚 Documentação: `/docs/finance_crm_integration/`
- 🐛 Issues: GitHub repository

---

**Última atualização:** 22/11/2025  
**Versão do módulo:** 19.0.1.0.0
