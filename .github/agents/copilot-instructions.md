# Global Copilot Instructions -- Odoo 19 (Revisado)

## 🧠 Objetivo

Este documento estabelece diretrizes rígidas para IA/Copilot gerar
código 100% compatível com **Odoo 19**, usando Owl, arquitetura moderna
e clean code.

## 🎯 Princípios Centrais

-   Sempre assumir **Odoo 19** como padrão.
-   Rejeitar código legado (Odoo ≤ 16).
-   Usar Owl, registries, assets modernos.
-   Gerar módulos escaláveis, seguros e com boa engenharia.
- 2FA obrigatório para assessores
Tokenização de dados sensíveis

## 🚫 Padrões Proibidos

-   `attrs=""`, `states=""`
-   QWeb JS legacy
-   Widgets antigos (`Widget.extend`, `many2many_tags` legado...)
-   `<record model="board.board">`
-   Inline JS/XML legado
-   Views usando sintaxe antiga de invisibilidade
-   Computed fields sem `store=True` em views
-   Contexto com `active_id` errado

## ✅ Padrões Obrigatórios

-   Owl Components (`Component`, `useState`, `useService`)
-   Registries (`views`, `fields`, `actions`)
-   `<list>` no lugar do antigo `<tree>`
-   `<form>` moderno
-   Domínios válidos e limpos
-   SCSS modular
-   Segurança (`ir.model.access.csv` + checks)
-   Código Python com boas práticas

## 📁 Estrutura Obrigatória do Módulo

    module/
    ├── __manifest__.py
    ├── models/
    ├── views/
    ├── security/
    ├── data/
    └── static/src/{js,scss,xml}

## 📌 Manifest Modelo

``` python
{
    "name": "Module Name",
    "version": "19.0.1.0.0",
    "depends": ["base", "web"],
    "data": ["security/ir.model.access.csv", "views/views.xml"],
    "assets": {
        "web.assets_backend": [
            "module/static/src/js/**/*",
            "module/static/src/xml/**/*",
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
```

## 🧩 Python -- Backend Moderno

``` python
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class Model(models.Model):
    _name = "my.model"
    _description = "My Model"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)

    @api.depends("amount")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.amount * 2
```

### Regras Python

-   Sempre documentar métodos
-   Evitar `cr.execute`, usar ORM
-   Implementar `_check_company`
-   Implementar `_name_search` se necessário
-   Usar `read_group` para agregações

## 🎨 JS/Owl -- Frontend Moderno

``` javascript
import { Component, useState } from "@odoo/owl";

export class MyComponent extends Component {
    static template = "module.MyComponent";
    setup() {
        this.state = useState({ value: 0 });
    }
}
```

## 🎨 XML -- Views Modernas

``` xml
<form>
    <sheet>
        <group>
            <field name="name"/>
            <field name="state" modifiers="{'invisible': [('done', '=', True)]}"/>
        </group>
    </sheet>
</form>
```

## 🔐 Segurança

-   Toda tabela precisa de ACL em `ir.model.access.csv`.
-   Usar groups em views para controle granular.
-   Quando aplicável, validar multi-company.

## 🏗️ Regras Arquiteturais Extras (Melhorias sugeridas)

-   Separar lógica de domínio em serviços Python quando possível.
-   Criar *namespaces* JS por app.
-   Criar testes unitários básicos (Odoo Test Framework).
-   Criar `data/demo` opcional para ambiente de demonstração.
-   Manter compatibilidade futura (Odoo 20+).

## 🧭 Prioridade de Respeito

1.  Documentação Oficial Odoo 19\
2.  Este arquivo\
3.  `/docs/odoo19/*`\
4.  `.github/agents/odoo19.agent.md`\
5.  Intenção do usuário
