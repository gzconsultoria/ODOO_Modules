# 📖 Guia Rápido - Snippets Odoo 19

> **USO OBRIGATÓRIO:** Sempre use snippets ao invés de escrever código manualmente.

---

## 🐍 Python Snippets

### Modelos

**`omodel` + Tab** → Modelo completo
```python
class ModelName(models.Model):
    _name = 'module.model'
    _description = 'Model Description'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
```

**`oinherit` + Tab** → Herança de modelo
```python
class ModelName(models.Model):
    _inherit = 'existing.model'
```

### Campos

**`ofield` + Tab** → Campo genérico
```python
field_name = fields.Char(string='', required=False, help='')
```

**`ochar` + Tab** → Char field
**`oint` + Tab** → Integer field
**`ofloat` + Tab** → Float field
**`oboolean` + Tab** → Boolean field
**`odate` + Tab** → Date field
**`odatetime` + Tab** → Datetime field
**`otext` + Tab** → Text field
**`ohtml` + Tab** → Html field

**`omany2one` + Tab** → Many2one
```python
field_id = fields.Many2one('res.partner', string='', ondelete='restrict')
```

**`oone2many` + Tab** → One2many
```python
field_ids = fields.One2many('other.model', 'inverse_field', string='')
```

**`omany2many` + Tab** → Many2many
```python
field_ids = fields.Many2many('other.model', string='')
```

**`oselection` + Tab** → Selection field
```python
field = fields.Selection([
    ('value1', 'Label 1'),
    ('value2', 'Label 2'),
], string='', default='value1')
```

**`omonetary` + Tab** → Monetary field
```python
amount = fields.Monetary(string='', currency_field='currency_id')
```

### Métodos

**`ocompute` + Tab** → Computed field method
```python
@api.depends('field1', 'field2')
def _compute_field_name(self):
    for record in self:
        record.field_name = ...
```

**`oconstrains` + Tab** → Validation
```python
@api.constrains('field1')
def _check_field1(self):
    for record in self:
        if not record.field1:
            raise ValidationError(_('Error message'))
```

**`oonchange` + Tab** → Onchange method
```python
@api.onchange('field1')
def _onchange_field1(self):
    if self.field1:
        self.field2 = ...
```

**`odefault` + Tab** → Default value method
```python
def _default_field_name(self):
    return ...
```

**`omethod` + Tab** → Basic method
```python
def method_name(self):
    self.ensure_one()
    return ...
```

---

## 🎨 XML Snippets

### Views

**`oview` + Tab** → View record
```xml
<record id="view_model_form" model="ir.ui.view">
    <field name="name">model.form</field>
    <field name="model">model.name</field>
    <field name="arch" type="xml">
        <form>
            ...
        </form>
    </field>
</record>
```

**`oform` + Tab** → Form view
```xml
<form>
    <sheet>
        <group>
            <field name="name"/>
        </group>
    </sheet>
</form>
```

**`otree` / `olist`** + Tab → List/Tree view
```xml
<list>
    <field name="name"/>
</list>
```

**`osearch` + Tab** → Search view
```xml
<search>
    <field name="name"/>
    <filter string="Filter" name="filter" domain="[]"/>
    <group expand="1" string="Group By">
        <filter string="Group" name="group" context="{'group_by': ['field']}"/>
    </group>
</search>
```

**`okanban` + Tab** → Kanban view
```xml
<kanban>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <field name="name"/>
            </div>
        </t>
    </templates>
</kanban>
```

### Actions & Menus

**`oaction` + Tab** → Window action
```xml
<record id="action_model" model="ir.actions.act_window">
    <field name="name">Model Name</field>
    <field name="res_model">model.name</field>
    <field name="view_mode">tree,form</field>
</record>
```

**`omenu` + Tab** → Menu item
```xml
<menuitem id="menu_model"
          name="Model"
          action="action_model"
          parent="parent_menu"
          sequence="10"/>
```

### Data

**`odata` + Tab** → Data record
```xml
<record id="record_id" model="model.name">
    <field name="name">Value</field>
</record>
```

---

## 🔧 Security Snippets

**`oaccess` + Tab** → ir.model.access.csv line
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

**`orule` + Tab** → Record rule
```xml
<record id="rule_name" model="ir.rule">
    <field name="name">Rule Name</field>
    <field name="model_id" ref="model_model_name"/>
    <field name="domain_force">[]</field>
</record>
```

---

## 🎯 Workflow de Uso

### 1. Criar Novo Modelo
```
1. Digite: omodel + Tab
2. Preencha: _name, _description
3. Digite: ofield + Tab (para cada campo)
4. Digite: ocompute + Tab (para campos computados)
```

### 2. Criar View
```
1. Digite: oview + Tab
2. Preencha: id, name, model
3. Digite: oform + Tab (dentro de arch)
4. Use Auto Close Tag (fecha automaticamente)
```

### 3. Criar Action + Menu
```
1. Digite: oaction + Tab
2. Preencha: res_model, view_mode
3. Digite: omenu + Tab
4. Referencie action criado
```

---

## 💡 Dicas Pro

### Auto-Complete Tags XML
- Digite `<fie` → sugere `<field>`
- Digite `<gro` → sugere `<group>`
- Fecha automaticamente com `</field>` ao digitar `>`

### IntelliSense Modelos
- Digite `fields.` → mostra todos os tipos disponíveis
- Digite `models.` → mostra Model, TransientModel, etc.
- Ctrl+Espaço força auto-complete

### Validação em Tempo Real
- Linha ondulada vermelha = erro real
- Passe mouse sobre erro para ver descrição
- Use Ctrl+. para quick fixes

---

## 🚨 Regras de Uso

1. ✅ **SEMPRE use snippets** para estruturas Odoo
2. ✅ **Confie no Language Server** - erros vermelhos são reais
3. ✅ **Use auto-complete** antes de procurar documentação
4. ❌ **NUNCA ignore** erros do validator
5. ❌ **NUNCA escreva** estruturas manualmente se há snippet

---

**Atalhos Úteis:**
- `Tab` - Avança entre campos do snippet
- `Shift+Tab` - Volta campo do snippet
- `Ctrl+Espaço` - Força auto-complete
- `Ctrl+.` - Quick fix
- `F2` - Rename symbol (renomeia em todo projeto)

---

📚 **Referência Completa:**
- Odoo Snippets: https://marketplace.visualstudio.com/items?itemName=jigar-patel.odoosnippets
- Odoo IDE: https://marketplace.visualstudio.com/items?itemName=trinhanhngoc.vscode-odoo
