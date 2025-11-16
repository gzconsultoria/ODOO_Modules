# 🎯 Boas Práticas de Desenvolvimento Odoo 19

Este documento descreve as principais boas práticas implementadas no módulo CRM Wealth Management e serve como guia para desenvolvimento de módulos Odoo 19.

## 📁 Estrutura de Diretórios

```
crm_wealth/
├── __init__.py                 # Importa subpacotes
├── __manifest__.py             # Metadados do módulo
├── models/                     # Modelos Python
│   ├── __init__.py
│   ├── crm_lead.py            # Herança e novos modelos
│   └── acompanhamento_mensal.py
├── views/                      # Views XML
│   └── crm_lead_views.xml
├── data/                       # Dados iniciais
│   └── crm_stage_data.xml
├── security/                   # Controle de acesso
│   └── ir.model.access.csv
├── static/                     # Arquivos estáticos
│   └── description/
│       └── index.html
└── README.md                   # Documentação
```

## 🏗️ Arquitetura e Design

### 1. Manifesto (__manifest__.py)

**Boas práticas:**
- ✅ Versão compatível com Odoo (19.0.x.y.z)
- ✅ Categoria correta (Sales/CRM)
- ✅ Dependências explícitas
- ✅ Licença definida (LGPL-3)
- ✅ Ordem correta dos arquivos de dados

```python
{
    'name': 'Nome Descritivo',
    'version': '19.0.1.0.0',  # Odoo.Major.Minor.Patch
    'category': 'Sales/CRM',
    'depends': ['crm', 'sale_crm'],
    'data': [
        'security/ir.model.access.csv',  # Primeiro!
        'data/crm_stage_data.xml',
        'views/crm_lead_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

### 2. Modelos (models/)

**Herança de Modelos:**

```python
class CrmLead(models.Model):
    _inherit = 'crm.lead'  # Herda e estende
    
    # Novos campos
    campo_customizado = fields.Char()
```

**Tipos de Campos Odoo 19:**

```python
# Texto
name = fields.Char(string='Nome', required=True)
description = fields.Text(string='Descrição')

# Numéricos
idade = fields.Integer()
preco = fields.Float(digits=(16, 2))
valor = fields.Monetary(currency_field='currency_id')

# Booleanos
ativo = fields.Boolean(default=True)

# Seleção
estado = fields.Selection([
    ('draft', 'Rascunho'),
    ('done', 'Concluído'),
], string='Estado', default='draft')

# Relacionamentos
partner_id = fields.Many2one('res.partner', string='Cliente')
tag_ids = fields.Many2many('crm.tag', string='Tags')
line_ids = fields.One2many('crm.line', 'lead_id', string='Linhas')

# Computados
total = fields.Float(compute='_compute_total', store=True)
```

**Campos Computados:**

```python
@api.depends('field1', 'field2')
def _compute_total(self):
    for record in self:
        record.total = record.field1 + record.field2
```

**Boas práticas:**
- ✅ Use `store=True` quando o campo é usado em buscas/filtros
- ✅ Use `readonly=True` em campos computados sem método inverse
- ✅ Sempre itere com `for record in self:` em métodos computados
- ✅ Use `tracking=True` para campos importantes (auditoria)
- ✅ Use `help` para documentar campos complexos

### 3. Segurança (security/)

**ir.model.access.csv:**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,access.model.user,model_crm_wealth_interesse,crm.group_crm_user,1,1,1,0
access_model_manager,access.model.manager,model_crm_wealth_interesse,crm.group_crm_manager,1,1,1,1
```

**Boas práticas:**
- ✅ Sempre criar permissões para user e manager
- ✅ model_id usa o padrão `model_nome_do_modelo` (underscores)
- ✅ Managers geralmente têm todas permissões (1,1,1,1)
- ✅ Users podem ter restrições (ex: 1,1,1,0 - sem delete)

### 4. Views (views/)

**Herança de Views:**

```xml
<record id="view_custom" model="ir.ui.view">
    <field name="name">nome.da.view</field>
    <field name="model">crm.lead</field>
    <field name="inherit_id" ref="crm.crm_lead_view_form"/>
    <field name="arch" type="xml">
        <!-- Adicionar dentro de elemento existente -->
        <xpath expr="//notebook" position="inside">
            <page string="Nova Aba">
                <field name="novo_campo"/>
            </page>
        </xpath>
        
        <!-- Adicionar depois de elemento -->
        <xpath expr="//field[@name='name']" position="after">
            <field name="campo_adicional"/>
        </xpath>
        
        <!-- Substituir elemento -->
        <xpath expr="//field[@name='user_id']" position="replace">
            <field name="user_id" options="{'no_create': True}"/>
        </xpath>
    </field>
</record>
```

**Widgets Úteis:**

```xml
<!-- Tags coloridas -->
<field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>

<!-- Radio buttons -->
<field name="tipo" widget="radio"/>

<!-- Checkbox booleano -->
<field name="ativo" widget="boolean_toggle"/>

<!-- Priority (estrelas) -->
<field name="priority" widget="priority"/>

<!-- Badge/status -->
<field name="state" widget="badge"/>

<!-- Kanban com imagem -->
<field name="image" widget="image" options="{'size': [90, 90]}"/>
```

**Invisibilidade Condicional:**

```xml
<!-- Campo computado controla visibilidade -->
<page string="Aba" invisible="not show_aba">
    <field name="show_aba" invisible="1"/>  <!-- Campo oculto -->
    <field name="campo_visivel"/>
</page>

<!-- Baseado no estado -->
<field name="campo" invisible="state != 'done'"/>

<!-- Múltiplas condições -->
<field name="campo" invisible="state != 'done' and tipo != 'A'"/>
```

**Boas práticas:**
- ✅ Use XPath para herança precisa
- ✅ Sempre defina `name` único para a view
- ✅ Use `invisible` ao invés de `attrs` quando possível (Odoo 19)
- ✅ Coloque campos invisíveis usados em expressões

### 5. Dados (data/)

**Dados Mestres:**

```xml
<odoo>
    <data noupdate="1">  <!-- Não atualizar em upgrade -->
        <record id="record_unique_id" model="crm.stage">
            <field name="name">Nome</field>
            <field name="sequence">10</field>
            <field name="fold" eval="False"/>
        </record>
    </data>
</odoo>
```

**Boas práticas:**
- ✅ Use `noupdate="1"` para dados que usuário pode modificar
- ✅ Use `eval="False"` ou `eval="True"` para booleanos
- ✅ IDs únicos e descritivos
- ✅ Sequências múltiplas de 10 (10, 20, 30...) para permitir inserções

### 6. Python - Boas Práticas

**Imports:**

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
```

**Métodos API:**

```python
# Decoradores comuns
@api.depends('field1', 'field2')  # Para computeds
@api.onchange('field')             # Para onchanges
@api.constrains('field')           # Para validações
@api.model                         # Método da classe (não de record)
```

**Validações:**

```python
@api.constrains('valor')
def _check_valor(self):
    for record in self:
        if record.valor < 0:
            raise ValidationError(_('Valor não pode ser negativo!'))
```

**Boas práticas:**
- ✅ Use `_` para strings traduzíveis
- ✅ Sempre itere `for record in self:`
- ✅ Use `self.env['model']` para acessar outros modelos
- ✅ Use `self.ensure_one()` em métodos que esperam 1 registro
- ✅ Nomeie métodos privados com `_nome_metodo`
- ✅ Docstrings em métodos complexos

### 7. Nomenclatura

**Modelos:**
```python
'crm.wealth.interesse'     # Sempre pontos, minúsculas
'crm.wealth.acompanhamento'
```

**IDs XML:**
```xml
stage_captacao              <!-- Snake_case -->
crm_wealth_interesse_action
menu_crm_wealth_config
```

**Campos Python:**
```python
nome_campo                  # Snake_case
patrimonio_aproximado
valor_investido_atual
```

## 🔍 Debugging e Testes

**Modo Desenvolvedor:**
```
Settings → Activate Developer Mode
```

**Ver erros:**
```python
import logging
_logger = logging.getLogger(__name__)

_logger.info('Mensagem info')
_logger.warning('Mensagem warning')
_logger.error('Mensagem erro')
```

**Console Python (odoo shell):**
```bash
odoo shell -c /etc/odoo.conf -d database_name
```

## 📚 Recursos Adicionais

- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [ORM API Reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Views Reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html)
- [Guidelines](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)

## ✅ Checklist antes de Deploy

- [ ] Todos os modelos têm `_description`
- [ ] Campos importantes têm `help` e `string`
- [ ] Security rules criadas (ir.model.access.csv)
- [ ] Views testadas (form, tree, search)
- [ ] Dados iniciais validados
- [ ] Sem hardcode de IDs de registros
- [ ] Logs de debug removidos
- [ ] README atualizado
- [ ] Versão correta no manifest
- [ ] Testes realizados em banco limpo
