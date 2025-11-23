# Copilot Instructions - ODOO Modules para Wealth Management

## 🎯 Visão Geral do Projeto

Este repositório contém **módulos customizados para Odoo 19** especializados em **consultoria de investimentos e wealth management**. O módulo principal (`crm_wealth`) estende o CRM nativo do Odoo com funcionalidades específicas para gestão de clientes de alto patrimônio.

## 🏗️ Arquitetura do Sistema

### Módulo Principal: `crm_wealth`

**Conceito-Chave:** Sistema de abas progressivas que se revelam conforme o lead avança no funil de vendas (6 estágios).

#### Funil de Vendas (6 Estágios)
```
seq 10: 🔵 Captação → coleta interesse inicial
seq 20: 🟢 Qualificação → perfil e objetivos
seq 30: 🟣 Reunião Estratégica → diagnóstico profundo
seq 40: 🟠 Proposta → apresentação comercial
seq 50: 🟡 Onboarding → documentação e compliance
seq 60: 🟤 Execução & Acompanhamento → gestão ativa (is_won=True)
```

#### Visibilidade Progressiva de Abas
- **Lógica:** Campo computado `show_*` baseado em `stage_sequence`
- **Implementação:** `@api.depends('stage_id', 'stage_sequence')` no método `_compute_show_tabs()`
- **Regra:** `show_qualificacao = stage_sequence >= 20` (mostra aba atual + todas anteriores)
- **Aba especial:** "Resumo" (seq 0) sempre visível, agregando informações de todas as abas

### Modelos e Relacionamentos

```python
crm.lead (herança)
├── Many2many → crm.wealth.interesse (tags de interesses)
├── Many2many → crm.wealth.estrategia (estratégias recomendadas)
├── Many2many → crm.wealth.objecao (objeções mapeadas)
├── Many2many → crm.wealth.documento (docs entregues)
├── Many2many → crm.wealth.corretora (contas abertas)
└── One2many → crm.wealth.acompanhamento (reuniões mensais)
```

## 🔧 Padrões de Desenvolvimento Odoo 19

### Herança de Modelos
```python
class CrmLead(models.Model):
    _inherit = 'crm.lead'  # SEMPRE usar _inherit, nunca _name para extensões
```

### Campos Computados com Dependências
```python
@api.depends('stage_id', 'stage_id.sequence', 'stage_sequence')
def _compute_show_tabs(self):
    for lead in self:
        seq = lead.stage_sequence or 0
        lead.show_captacao = seq >= 10
```

### Validações com Bloqueio de Fluxo
```python
@api.constrains('stage_id')
def _check_required_fields_by_stage(self):
    # Bloqueia mudança de estágio se campos obrigatórios não preenchidos
    # Usa `raise ValidationError()` com mensagem clara
```

### Rastreamento de Mudanças de Estágio
```python
def write(self, vals):
    if 'stage_id' in vals:
        vals['stage_date'] = fields.Datetime.now()  # Marca timestamp da mudança
    return super(CrmLead, self).write(vals)
```

### Views XML - Herança com XPath
```xml
<xpath expr="//notebook" position="inside">
    <!-- Adiciona novas abas dentro do notebook existente -->
    <page string="🔵 Captação" invisible="not show_captacao">
        <field name="show_captacao" invisible="1"/>  <!-- Campo oculto para controle -->
```

## 💡 Funcionalidades Críticas

### 1. Sistema de Completude (0-100%)
- **Onde:** Cada aba tem indicador visual de preenchimento
- **Cálculo:** Método `_calcular_percentual(campos)` conta campos preenchidos
- **Uso:** Alertas visuais e bloqueio de progresso

### 2. Cálculos Financeiros Automáticos
```python
# Aporte Mensal Necessário (PMT com juros compostos)
@api.depends('valor_objetivo', 'prazo_objetivo')
def _compute_calculos_financeiros(self):
    # Taxa configurável em: Settings → CRM → Wealth Management
    taxa_anual = float(self.env['ir.config_parameter'].sudo().get_param('crm_wealth.taxa_padrao', default=10.0))
    # Fórmula PMT: FV / [((1 + i)^n - 1) / i]
```

### 3. Sistema de SLA e Notificações
- **Cron Jobs:** 3 crons diários verificam estágios estagnados
- **Métodos:** `action_check_sla_captacao()`, `action_check_sla_proposta()`, `action_check_sla_reuniao()`
- **Ações:** Cria atividades automáticas e notificações
- **Configuração:** `res.config.settings` com parâmetros `crm_wealth.sla_*`

### 4. Aba Resumo Executivo
- **Campos HTML computados:** `alertas_resumo`, `perfil_pessoal_resumo`
- **Score de qualificação:** 0-100 baseado em completude + potencial financeiro
- **Temperatura do lead:** cold/warm/hot baseado no score
- **Alertas de aniversário:** Cliente e cônjuge com contagem de dias

## 📁 Estrutura de Arquivos Crítica

```
crm_wealth/
├── __manifest__.py          # ORDEM IMPORTA: security → data → views
├── models/
│   ├── crm_lead.py          # 700+ linhas - modelo principal com TODAS as funcionalidades
│   ├── acompanhamento_mensal.py  # Modelo auxiliar para One2many
│   └── res_config_settings.py    # Taxas e SLAs configuráveis
├── views/
│   ├── crm_lead_views.xml   # Herança de views com 6 abas dinâmicas
│   ├── crm_wealth_auxiliar_views.xml  # Views dos modelos many2many
│   └── crm_wealth_menus.xml # Menus técnicos (visible apenas em dev mode)
├── data/
│   ├── crm_stage_data.xml   # noupdate="0" - Atualiza stages padrão do CRM
│   ├── crm_wealth_demo_data.xml  # noupdate="1" - Dados mestres
│   └── crm_wealth_sla_data.xml   # Cron jobs para SLAs
└── security/
    └── ir.model.access.csv  # Todos os modelos auxiliares + acompanhamento
```

## 🚨 Pontos de Atenção

### Ao Adicionar Novos Campos
1. Adicionar no modelo (`models/crm_lead.py`)
2. Adicionar na view XML apropriada (`views/crm_lead_views.xml`)
3. Se obrigatório, adicionar validação em `_check_required_fields_by_stage()`
4. Se impacta completude, adicionar em `_compute_completude_abas()`

### Ao Modificar Estágios
- **NÃO criar novos stages**, modificar os existentes em `data/crm_stage_data.xml`
- Sequências múltiplas de 10 (10, 20, 30...) para permitir inserções
- Usar `noupdate="0"` para permitir atualização de stages
- Manter `stage_execucao` com `is_won=True`

### Ao Adicionar Computed Fields
```python
# SEMPRE iterar com for record in self:
@api.depends('field1', 'field2')
def _compute_total(self):
    for record in self:  # ← OBRIGATÓRIO
        record.total = record.field1 + record.field2
```

### Widgets Importantes Usados
```xml
<field name="tags" widget="many2many_tags"/>           <!-- Tags coloridas -->
<field name="perfil" widget="radio"/>                   <!-- Radio buttons -->
<field name="suitability" widget="boolean_toggle"/>     <!-- Toggle switch -->
<field name="score" widget="priority"/>                 <!-- Estrelas (0-5) -->
<field name="fee_gestao" widget="percentage"/>          <!-- Percentual -->
```

## 🔄 Fluxo de Dados Típico

1. **Lead criado** → `stage_date` setado automaticamente
2. **Aba visível** → `show_*` computado baseado em `stage_sequence`
3. **Preenchimento** → `*_completude` recalculado automaticamente
4. **Mudança de estágio** → Validação `_check_required_fields_by_stage()` executada
5. **Stage atrasado** → Cron detecta e cria atividade + notificação
6. **Cálculos** → `aporte_mensal_necessario` e `receita_anual_estimada` computados

## 🎨 Convenções de Código

- **IDs XML:** `snake_case` (ex: `stage_captacao`, `interesse_bolsa`)
- **Modelos:** `crm.wealth.nome` (sempre pontos, minúsculas)
- **Campos Python:** `snake_case` (ex: `patrimonio_aproximado`)
- **Sequências:** 0 (Resumo), 10, 20, 30... (múltiplos de 10)
- **Emojis:** Usados consistentemente nos nomes de estágios e abas
- **Tracking:** `tracking=True` em campos críticos para auditoria

## 🧪 Ambiente de Desenvolvimento

### Docker Setup
```bash
docker-compose up -d  # Odoo 19 + PostgreSQL 15
# Acesso: http://localhost:8069
# Addons path: /mnt/extra-addons (mapeado para raiz do projeto)
```

### Modo Desenvolvedor
- **Ativar:** Settings → Activate Developer Mode
- **Menus técnicos:** Technical → Wealth Management (apenas em dev mode)
- **Ver logs:** `docker logs -f odoo_modules-web-1`

### Atualizar Módulo
```bash
# Via interface: Apps → CRM Wealth Management → Upgrade
# Via linha de comando:
docker exec odoo_modules-web-1 odoo -u crm_wealth -d nome_database
```

## 📚 Recursos de Referência

- **Odoo 19 ORM:** https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- **Views Reference:** https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html
- **Docs internas:** 
  - `crm_wealth/BOAS_PRATICAS_ODOO19.md` - Padrões detalhados
  - `crm_wealth/EXEMPLOS_USO.md` - Casos de uso práticos
  - `crm_wealth/README.md` - Visão geral funcional

## 🎯 Para Agentes de IA

### 🌟 REGRA DE OURO: "Na dúvida, SEMPRE buscar exemplos dentro dos próprios módulos nativos do Odoo"

**Localização dos módulos nativos:**
```bash
/usr/lib/python3/dist-packages/odoo/addons/
```

**Módulos de referência essenciais:**
- `base/` - res.partner, res.users, ir.* (estruturas fundamentais)
- `contacts/` - Gestão de contatos
- `crm/` - CRM e pipeline de vendas
- `sale/` - Vendas e cotações
- `account/` - Contabilidade
- `mail/` - Mensageria e tracking

**Comandos úteis para consultar código nativo:**
```bash
# Encontrar views de um modelo
grep -r "model=\"res.partner\"" /usr/lib/python3/dist-packages/odoo/addons/base/views/

# Buscar search views de exemplo
grep -A 30 "view_.*_filter" /usr/lib/python3/dist-packages/odoo/addons/base/views/*.xml

# Ver estrutura de modelo
cat /usr/lib/python3/dist-packages/odoo/addons/base/models/res_partner.py

# Verificar uso de widget
grep -r "widget=\"percentpie\"" /usr/lib/python3/dist-packages/odoo/addons/
```

### Ferramentas e Extensões Disponíveis

**VS Code Extensions instaladas:**
- **Odoo Snippets** (jigar-patel) - Use snippets: `omodel`, `ofield`, `omethod`, `oview`
- **Odoo IDE** (trinhanhngoc) - IntelliSense e navegação entre modelos
- **Odoo Language Server** (oficial) - Validação automática de código
- **Odoo Development Pack** (scapigliato) - Bundle completo
- **Odoo Scaffold** (mstuttgart) - Gerador de módulos: use para criar estrutura inicial
- **Odoo Code Snippets** (mstuttgart) - Snippets adicionais sem erros de digitação
- **XML Language Support** (Red Hat) - Validação e formatação XML
- **Rainbow CSV** - Visualização colorida de `ir.model.access.csv`

**Como usar Snippets Odoo:**
```python
# Digite "omodel" + Tab → Gera estrutura completa de modelo
# Digite "ofield" + Tab → Gera campo com todos atributos
# Digite "ocompute" + Tab → Gera método computado completo
# Digite "oview" + Tab → Gera estrutura de view XML
```

**Como usar Odoo Scaffold:**
- Comando: `Odoo: Create Module` (Ctrl+Shift+P)
- Preenche automaticamente: __manifest__.py, __init__.py, models/, views/, security/
- Acelera criação de novos módulos

### Ao Criar Novos Campos
- **USE SNIPPETS:** Digite `ofield` + Tab ao invés de escrever manualmente
- Sempre use `help='...'` para documentação inline
- Use `tracking=True` se o campo for importante para histórico
- Para Many2many, considere se precisa widget `many2many_tags`
- Campos monetários SEMPRE com `currency_field='company_currency'`

### Ao Criar Novos Modelos
- **USE SNIPPETS:** Digite `omodel` + Tab para estrutura completa
- **OU USE SCAFFOLD:** `Odoo: Create Module` para módulo completo
- Sempre defina `_name`, `_description`, `_order` (opcional)
- Adicione `_inherit = ['mail.thread', 'mail.activity.mixin']` se precisar tracking

### Ao Modificar Lógica de Negócio
- **USE SNIPPETS:** `ocompute`, `oconstrains`, `oonchange`
- Validações vão em `@api.constrains()`
- Cálculos automáticos vão em `@api.depends()` com `compute=`
- Onchange para feedback imediato vão em `@api.onchange()`
- Side-effects de mudanças vão em `write()` ou `create()`

### Ao Criar Views XML
- **USE SNIPPETS:** Digite `oview` + Tab para estrutura base
- **USE XML Language Support:** Auto-complete de tags Odoo
- SEMPRE herdar views existentes, nunca substituir
- Use `invisible` (Odoo 19+) ao invés de `attrs={'invisible': ...}`
- Campos usados em expressões devem estar na view com `invisible="1"`
- Organize em grupos (`<group>`) para layout responsivo

### Ao Editar CSV (security/ir.model.access.csv)
- **Rainbow CSV está ativo:** Colunas aparecerão coloridas automaticamente
- Formato: `id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`
- Sempre criar permissões para todos os modelos customizados

### Validação de Código
- **Odoo Language Server** valida automaticamente
- Erros aparecem em tempo real no editor
- Use `xmllint` para validação XML adicional se necessário

### Padrão de Commits
```
feat(crm_wealth): adiciona campo xyz na aba qualificação
fix(crm_wealth): corrige cálculo de aporte mensal
docs(crm_wealth): atualiza exemplos de uso
```

### Checklist Antes de Criar Código
1. ✅ **Consultei módulos nativos do Odoo para padrão de referência?**
2. ✅ Posso usar um snippet ao invés de escrever manualmente?
3. ✅ O Odoo Language Server está validando sem erros?
4. ✅ Usei Rainbow CSV para verificar permissões?
5. ✅ A view XML tem auto-complete funcionando?
6. ✅ Segui os padrões de nomenclatura snake_case?
7. ✅ Campos computados têm `for record in self:`?
8. ✅ Campos usados em views/search têm `store=True`?
9. ✅ Search views seguem padrão nativo com `<group name="group_by">`?

### Workflow de Desenvolvimento Recomendado

1. **Pesquise primeiro:** `grep` nos módulos nativos para encontrar padrão similar
2. **Copie a estrutura:** Use o código nativo como template
3. **Adapte:** Modifique para seu caso de uso específico
4. **Valide:** Use Language Server e xmllint
5. **Teste incremental:** Atualize módulo frequentemente durante desenvolvimento

### Recursos Adicionais

📚 **Guia Completo:** `/workspaces/ODOO_Modules/BOAS_PRATICAS_ODOO19_CONSOLIDADO.md`
- Exemplos práticos de todos os padrões
- Checklist completo de desenvolvimento
- Comandos úteis para debugging
- Anatomia detalhada de search views, form views, etc.
