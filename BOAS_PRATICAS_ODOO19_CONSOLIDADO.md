# 🎯 Boas Práticas Odoo 19 - Guia Consolidado

**Última atualização:** 22/11/2024  
**Baseado em:** Experiências reais de desenvolvimento e debugging de módulos Odoo 19

---

## 🌟 Regra de Ouro

### **"Na dúvida, SEMPRE buscar exemplos dentro dos próprios módulos nativos do Odoo"**

Os módulos nativos do Odoo 19 estão localizados em:
```bash
/usr/lib/python3/dist-packages/odoo/addons/
```

**Principais módulos de referência:**
- `base/` - Estruturas fundamentais (res.partner, res.users, ir.*)
- `contacts/` - Gestão de contatos e parceiros
- `crm/` - CRM e pipeline de vendas
- `sale/` - Vendas e cotações
- `account/` - Contabilidade e finanças
- `mail/` - Sistema de mensageria e tracking
- `website/` - Frontend e portal

**Como usar como referência:**
```bash
# Encontrar views de um modelo específico
grep -r "model=\"res.partner\"" /usr/lib/python3/dist-packages/odoo/addons/base/views/

# Buscar search views de exemplo
grep -A 30 "view_.*_filter" /usr/lib/python3/dist-packages/odoo/addons/base/views/*.xml

# Ver estrutura de um modelo
cat /usr/lib/python3/dist-packages/odoo/addons/base/models/res_partner.py

# Verificar como usar um widget específico
grep -r "widget=\"percentpie\"" /usr/lib/python3/dist-packages/odoo/addons/
```

---

## 📚 Estrutura de Desenvolvimento

### 1. Organização de Arquivos (Ordem Importa!)

```python
# __manifest__.py - ORDEM CRÍTICA
{
    'data': [
        # 1º SEMPRE security (carrega permissões antes de tudo)
        'security/ir.model.access.csv',
        'security/security_groups.xml',  # se houver grupos customizados
        
        # 2º data (dados mestres, stages, categorias)
        'data/initial_data.xml',
        'data/cron_jobs.xml',
        
        # 3º views (por último, pois referenciam modelos e dados)
        'views/model_views.xml',
        'views/menu_views.xml',
        
        # 4º wizards e reports (opcional)
        'wizard/wizard_views.xml',
        'report/report_templates.xml',
    ],
}
```

**Por quê essa ordem?**
- Security carrega primeiro → garante permissões antes de criar registros
- Data carrega segundo → cria registros que as views podem referenciar
- Views carrega por último → pode referenciar todos os campos e registros

### 2. Estrutura de Pastas Recomendada

```
meu_modulo/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── modelo_principal.py
│   ├── modelo_auxiliar.py
│   └── res_partner.py (heranças de modelos nativos)
├── views/
│   ├── modelo_principal_views.xml
│   ├── modelo_auxiliar_views.xml
│   ├── res_partner_views.xml
│   └── menu_views.xml
├── data/
│   ├── initial_data.xml
│   └── cron_jobs.xml
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml (opcional)
├── wizard/
│   ├── __init__.py
│   ├── wizard_model.py
│   └── wizard_views.xml
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       ├── css/
│       ├── js/
│       └── xml/ (templates Owl)
└── tests/
    ├── __init__.py
    └── test_modelo.py
```

---

## 🔧 Backend (Python) - Boas Práticas

### 1. Definição de Modelos

```python
# ✅ CORRETO - Modelo novo
class FinanceProfile(models.Model):
    _name = 'finance.profile'
    _description = 'Financial Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # tracking automático
    _order = 'create_date desc'
    
    # Campos sempre com help e string descritivos
    name = fields.Char(
        string='Nome do Perfil',
        required=True,
        tracking=True,  # rastreia mudanças
        help='Nome identificador do perfil financeiro'
    )
    
    total = fields.Monetary(
        string='Total Investido',
        currency_field='currency_id',  # OBRIGATÓRIO para Monetary
        compute='_compute_total',
        store=True,  # OBRIGATÓRIO se usado em views/search/graph
        help='Soma total dos investimentos do cliente'
    )

# ✅ CORRETO - Herança de modelo existente
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    finance_profile_ids = fields.One2many(
        'finance.profile',
        'partner_id',
        string='Perfis Financeiros'
    )
    
    finance_profile_count = fields.Integer(
        compute='_compute_finance_profile_count',
        string='Qtd. Perfis'
    )
```

### 2. Campos Computados (SEMPRE iterar!)

```python
# ✅ CORRETO
@api.depends('investment_ids', 'investment_ids.amount')
def _compute_total(self):
    for record in self:  # ← OBRIGATÓRIO iterar
        record.total = sum(record.investment_ids.mapped('amount'))

# ❌ ERRADO - Sem iteração
@api.depends('investment_ids')
def _compute_total(self):
    self.total = sum(self.investment_ids.mapped('amount'))  # QUEBRA com recordsets múltiplos
```

### 3. Validações (Constraints)

```python
# ✅ CORRETO - Validações claras e informativas
@api.constrains('suitability_score')
def _check_suitability_score_range(self):
    for record in self:
        if record.suitability_score < 0 or record.suitability_score > 100:
            raise ValidationError(
                _("Suitability Score deve estar entre 0 e 100. "
                  "Valor atual: %s") % record.suitability_score
            )

@api.constrains('investment_amount', 'monthly_income')
def _check_monetary_fields_positive(self):
    for record in self:
        if record.investment_amount < 0:
            raise ValidationError(_("Valor de investimento não pode ser negativo"))
        if record.monthly_income < 0:
            raise ValidationError(_("Renda mensal não pode ser negativa"))
```

### 4. Onchange (Feedback Imediato)

```python
# ✅ CORRETO - Onchange para UX
@api.onchange('risk_profile')
def _onchange_risk_profile(self):
    if self.risk_profile == 'conservative':
        self.recommended_allocation = 'Renda Fixa: 80%, Ações: 20%'
    elif self.risk_profile == 'moderate':
        self.recommended_allocation = 'Renda Fixa: 50%, Ações: 50%'
    else:
        self.recommended_allocation = 'Renda Fixa: 20%, Ações: 80%'
```

### 5. Performance (Indexação)

```python
# ✅ CORRETO - Campos com index=True quando usados em:
# - Search/filter frequente
# - Foreign keys
# - Group by
# - Ordenação

state = fields.Selection(
    [('draft', 'Rascunho'), ('active', 'Ativo'), ('expired', 'Expirado')],
    default='draft',
    index=True,  # ← usado frequentemente em filtros
    tracking=True
)

partner_id = fields.Many2one(
    'res.partner',
    string='Cliente',
    required=True,
    index=True,  # ← foreign key sempre com index
    ondelete='cascade'
)
```

---

## 🎨 Frontend (Views XML) - Boas Práticas

### 1. Search Views (COPIAR PADRÃO NATIVO!)

```xml
<!-- ✅ CORRETO - Padrão EXATO do Odoo nativo -->
<record id="finance_profile_search" model="ir.ui.view">
    <field name="name">finance.profile.search</field>
    <field name="model">finance.profile</field>
    <field name="arch" type="xml">
        <search string="Search Financial Profile">
            <!-- Campos de busca -->
            <field name="name" string="Nome"/>
            <field name="partner_id" string="Cliente"/>
            
            <!-- Filtros -->
            <filter string="Meus Clientes" name="my_clients"
                    domain="[('create_uid', '=', uid)]"/>
            <filter string="Pessoa Física" name="individual"
                    domain="[('partner_id.company_type', '=', 'person')]"/>
            
            <!-- Separador obrigatório antes de group_by -->
            <separator/>
            
            <!-- Group By - SEMPRE dentro de <group name="group_by"> -->
            <group name="group_by">
                <filter string="Por Cliente" name="group_partner"
                        domain="[]"  <!-- ← primeiro filter SEMPRE com domain="[]" -->
                        context="{'group_by': 'partner_id'}"/>
                <filter string="Por Estágio" name="group_stage"
                        context="{'group_by': 'stage_id'}"/>
            </group>
        </search>
    </field>
</record>
```

**Anatomia de uma Search View correta:**
1. Tag `<search string="...">` com descrição clara
2. `<field>` para campos pesquisáveis
3. `<filter>` para filtros pré-definidos
4. `<separator/>` antes do group_by
5. `<group name="group_by">` contendo filters de agrupamento
6. Primeiro filter de group_by com `domain="[]"`
7. Demais filters com `context="{'group_by': 'campo'}"`

### 2. Form Views (Organização e UX)

```xml
<!-- ✅ CORRETO - Form view organizada -->
<record id="finance_profile_form" model="ir.ui.view">
    <field name="name">finance.profile.form</field>
    <field name="model">finance.profile</field>
    <field name="arch" type="xml">
        <form string="Perfil Financeiro">
            <header>
                <!-- Botões de ação -->
                <button name="action_validate" type="object"
                        string="Validar" class="btn-primary"
                        invisible="state != 'draft'"/>
                
                <!-- Status bar -->
                <field name="state" widget="statusbar"
                       statusbar_visible="draft,active,expired"/>
            </header>
            
            <sheet>
                <!-- Button box (smart buttons no topo direito) -->
                <div class="oe_button_box" name="button_box">
                    <button name="action_view_investments" type="object"
                            class="oe_stat_button" icon="fa-money">
                        <field name="investment_count" widget="statinfo"
                               string="Investimentos"/>
                    </button>
                </div>
                
                <!-- Título -->
                <div class="oe_title">
                    <h1><field name="name" placeholder="Nome do Perfil"/></h1>
                </div>
                
                <!-- Campos principais organizados em groups -->
                <group>
                    <group string="Informações Básicas">
                        <field name="partner_id"/>
                        <field name="risk_profile"/>
                    </group>
                    <group string="Valores">
                        <field name="investment_amount" widget="monetary"/>
                        <field name="monthly_income" widget="monetary"/>
                    </group>
                </group>
                
                <!-- Notebook com abas -->
                <notebook>
                    <page string="Investimentos" name="investments">
                        <field name="investment_ids">
                            <tree editable="bottom">
                                <field name="name"/>
                                <field name="amount"/>
                            </tree>
                        </field>
                    </page>
                    
                    <page string="Histórico" name="history">
                        <field name="message_ids" widget="mail_thread"/>
                    </page>
                </notebook>
            </sheet>
            
            <!-- Chatter (mensagens e atividades) -->
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

### 3. List Views (Tree)

```xml
<!-- ✅ CORRETO - List view com decorators -->
<record id="finance_profile_tree" model="ir.ui.view">
    <field name="name">finance.profile.tree</field>
    <field name="model">finance.profile</field>
    <field name="arch" type="xml">
        <list string="Perfis Financeiros"
              decoration-success="state == 'active'"
              decoration-danger="state == 'expired'"
              decoration-muted="state == 'draft'">
            
            <field name="name"/>
            <field name="partner_id"/>
            <field name="investment_amount" widget="monetary"/>
            <field name="suitability_score" widget="percentpie"/>
            <field name="state" widget="badge"
                   decoration-success="state == 'active'"
                   decoration-danger="state == 'expired'"/>
        </list>
    </field>
</record>
```

### 4. Herança de Views (XPath)

```xml
<!-- ✅ CORRETO - Herdar view existente -->
<record id="res_partner_form_inherit_finance" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.finance</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        
        <!-- Adicionar botão no button_box -->
        <xpath expr="//div[@name='button_box']" position="inside">
            <button name="action_open_finance_profile" type="object"
                    class="oe_stat_button" icon="fa-chart-line">
                <field name="finance_profile_count" widget="statinfo"
                       string="Perfis"/>
            </button>
        </xpath>
        
        <!-- Adicionar aba nova no notebook -->
        <xpath expr="//notebook" position="inside">
            <page string="Finanças" name="finance">
                <field name="finance_profile_ids">
                    <tree>
                        <field name="name"/>
                        <field name="state"/>
                    </tree>
                </field>
            </page>
        </xpath>
        
    </field>
</record>
```

---

## 🔐 Segurança (Security)

### 1. Permissões em CSV

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_finance_profile_user,finance.profile.user,model_finance_profile,base.group_user,1,1,1,1
access_finance_profile_manager,finance.profile.manager,model_finance_profile,base.group_system,1,1,1,1
access_finance_alert_user,finance.alert.user,model_finance_alert,base.group_user,1,1,1,0
```

**Grupos comuns:**
- `base.group_user` - Usuários internos (acesso básico)
- `base.group_system` - Administradores (acesso total)
- `base.group_portal` - Usuários portal (acesso limitado)
- `base.group_public` - Público (sem login)

### 2. Record Rules (Regras de Registro)

```xml
<!-- ✅ CORRETO - Regra clara e específica -->
<record id="finance_profile_user_rule" model="ir.rule">
    <field name="name">Finance Profile: User can see own records</field>
    <field name="model_id" ref="model_finance_profile"/>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
</record>

<!-- Regra para managers verem tudo -->
<record id="finance_profile_manager_rule" model="ir.rule">
    <field name="name">Finance Profile: Managers see all</field>
    <field name="model_id" ref="model_finance_profile"/>
    <field name="groups" eval="[(4, ref('base.group_system'))]"/>
    <field name="domain_force">[(1, '=', 1)]</field>  <!-- sempre verdadeiro -->
</record>
```

---

## ⚡ Performance e Otimização

### 1. Campos Store vs Compute

```python
# ✅ store=True quando o campo é usado em:
# - Views (list, form, kanban)
# - Search/filters
# - Graph/pivot
# - Group by
# - Ordenação

total = fields.Float(
    compute='_compute_total',
    store=True,  # ← permite indexação e busca
    index=True   # ← acelera filtros e ordenação
)

# ❌ store=False apenas quando:
# - Campo calculado em tempo real (data atual, user atual)
# - Nunca usado em filtros/busca
# - Muda frequentemente com dados externos

current_user_name = fields.Char(
    compute='_compute_current_user',
    store=False  # ← sempre mostra user atual
)
```

### 2. Métodos de Busca Otimizados

```python
# ✅ CORRETO - Busca otimizada
def _get_expired_profiles(self):
    return self.env['finance.profile'].search([
        ('expiry_date', '<', fields.Date.today()),
        ('state', '=', 'active')
    ])

# ❌ EVITAR - Busca e filtragem em Python
def _get_expired_profiles(self):
    all_profiles = self.env['finance.profile'].search([])
    return all_profiles.filtered(
        lambda p: p.expiry_date < fields.Date.today() and p.state == 'active'
    )
```

### 3. Cron Jobs Otimizados

```xml
<!-- ✅ CORRETO - Cron eficiente -->
<record id="cron_check_expired_profiles" model="ir.cron">
    <field name="name">Finance: Check Expired Profiles</field>
    <field name="model_id" ref="model_finance_profile"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_expired_profiles()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active" eval="True"/>
    <!-- ODOO 19: Não usar numbercall, doall -->
</record>
```

```python
# Método do cron
def _cron_check_expired_profiles(self):
    """Verifica perfis expirados e cria alertas."""
    expired = self.search([
        ('expiry_date', '<', fields.Date.today()),
        ('state', '=', 'active')
    ])
    
    for profile in expired:
        profile.state = 'expired'
        profile.message_post(
            body='Perfil expirado automaticamente.',
            subject='Perfil Expirado'
        )
```

---

## 🧪 Debugging e Troubleshooting

### 1. Logs Úteis

```python
import logging
_logger = logging.getLogger(__name__)

def _compute_total(self):
    for record in self:
        _logger.info(f"Calculando total para {record.name}")
        record.total = sum(record.investment_ids.mapped('amount'))
        _logger.debug(f"Total calculado: {record.total}")
```

### 2. Verificar Erros de Views

```bash
# Ver logs do container Odoo
docker logs -f odoo_modules-web-1

# Validar XML manualmente
xmllint --noout /caminho/para/view.xml

# Buscar padrão nativo similar
grep -r "model=\"res.partner\"" /usr/lib/python3/dist-packages/odoo/addons/base/views/
```

### 3. Testar Módulo

```bash
# Atualizar módulo
docker exec odoo_modules-web-1 odoo -u meu_modulo -d database_name

# Ou via interface: Apps → Meu Módulo → Upgrade
```

---

## 📋 Checklist de Desenvolvimento

Antes de fazer commit/deploy, verificar:

### Backend (Python)
- [ ] Todos os campos computados têm `for record in self:`?
- [ ] Campos usados em views têm `store=True`?
- [ ] Campos Many2one e Selection têm `index=True`?
- [ ] Validações têm mensagens claras com `_("Texto traduzível")`?
- [ ] Campos monetários têm `currency_field='currency_id'`?
- [ ] Métodos write/create chamam `super()` corretamente?

### Frontend (Views)
- [ ] Search views seguem padrão nativo (group_by dentro de `<group name="group_by">`)?
- [ ] Form views têm estrutura organizada (header, sheet, chatter)?
- [ ] List views têm decorators para visual feedback?
- [ ] Views herdam corretamente com XPath?
- [ ] Campos invisíveis de controle estão com `invisible="1"`?

### Segurança
- [ ] Todos os modelos têm linha em `ir.model.access.csv`?
- [ ] Permissões corretas para cada grupo?
- [ ] Record rules definidas quando necessário?
- [ ] Campos sensíveis têm `groups="base.group_system"`?

### Performance
- [ ] Campos frequentemente filtrados têm `index=True`?
- [ ] Buscas usam domain ao invés de `filtered()`?
- [ ] Cron jobs não têm `numbercall` ou `doall`?

### Qualidade
- [ ] Campos importantes têm `help='...'`?
- [ ] Campos críticos têm `tracking=True`?
- [ ] Código tem logging adequado?
- [ ] README.md atualizado?

---

## 🎓 Recursos de Aprendizado

### Documentação Oficial
- **ORM API:** https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html
- **Views:** https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html
- **Security:** https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html

### Módulos Nativos para Estudar
```bash
# Ver estrutura de um módulo completo
ls -la /usr/lib/python3/dist-packages/odoo/addons/crm/

# Estudar views complexas
cat /usr/lib/python3/dist-packages/odoo/addons/crm/views/crm_lead_views.xml

# Ver como fazer herança
grep -r "_inherit" /usr/lib/python3/dist-packages/odoo/addons/sale/models/
```

### Comandos Úteis
```bash
# Encontrar uso de um widget
grep -r "widget=\"percentpie\"" /usr/lib/python3/dist-packages/odoo/addons/

# Ver como um campo é definido
grep -r "fields.Monetary" /usr/lib/python3/dist-packages/odoo/addons/base/models/

# Buscar search views de exemplo
find /usr/lib/python3/dist-packages/odoo/addons -name "*views.xml" -exec grep -l "view_.*_filter" {} \;
```

---

## 💡 Dicas Finais

1. **Sempre consulte o código nativo primeiro** - É a fonte mais confiável
2. **Mantenha simplicidade** - Odoo já tem muita funcionalidade pronta
3. **Use ORM ao máximo** - Evite SQL direto (`cr.execute`)
4. **Teste incremental** - Atualize o módulo frequentemente durante desenvolvimento
5. **Documente claramente** - `help='...'` em campos, docstrings em métodos
6. **Siga convenções** - `snake_case` em Python, `kebab-case` em XML IDs
7. **Performance importa** - `index=True`, `store=True`, buscas otimizadas
8. **Segurança primeiro** - Sempre defina permissões adequadas

---

**Happy Odoo 19 Coding! 🚀**
