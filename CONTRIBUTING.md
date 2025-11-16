# Guia de Contribuição

Obrigado por considerar contribuir com o CRM Wealth Management! 🎉

## 🤝 Como Contribuir

### Reportar Bugs

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/gzconsultoria/crm_wealth_odoo/issues)
2. Se não encontrou, abra uma nova issue incluindo:
   - Versão do Odoo
   - Passos detalhados para reproduzir
   - Comportamento esperado vs atual
   - Screenshots (se aplicável)
   - Logs de erro

### Sugerir Melhorias

1. Abra uma issue com a tag `enhancement`
2. Descreva claramente:
   - Problema que a melhoria resolve
   - Como você imagina a solução
   - Benefícios para os usuários

### Contribuir com Código

#### 1. Fork e Clone

```bash
# Fork via GitHub, depois:
git clone https://github.com/SEU_USUARIO/crm_wealth_odoo.git
cd crm_wealth_odoo
```

#### 2. Crie uma Branch

```bash
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bugfix
```

**Convenção de nomes:**
- `feature/nome-da-feature` - Nova funcionalidade
- `fix/nome-do-fix` - Correção de bug
- `docs/nome-da-doc` - Documentação
- `refactor/nome` - Refatoração de código

#### 3. Desenvolva Seguindo os Padrões

**Python (PEP 8):**
```python
# Bom
def calculate_portfolio_value(self):
    """Calcula o valor total do portfólio."""
    total = 0.0
    for investment in self.investments:
        total += investment.value
    return total

# Ruim
def calc(self):
    t=0
    for i in self.inv:t+=i.val
    return t
```

**XML (Odoo):**
```xml
<!-- Bom: indentação consistente, atributos claros -->
<record id="view_form_custom" model="ir.ui.view">
    <field name="name">nome.descritivo</field>
    <field name="model">crm.lead</field>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <field name="novo_campo"/>
        </xpath>
    </field>
</record>

<!-- Ruim: sem indentação, id genérico -->
<record id="view1" model="ir.ui.view">
<field name="name">v1</field>
<field name="arch" type="xml">
<xpath expr="//field[@name='name']" position="after"><field name="novo_campo"/></xpath>
</field>
</record>
```

**Boas Práticas Específicas:**

1. **Sempre adicione docstrings:**
   ```python
   def _compute_show_tabs(self):
       """
       Calcula visibilidade das abas baseado no estágio atual.
       
       Regra: mostra a aba atual e todas as anteriores.
       Sequências: Captação(10), Qualificação(20), Reunião(30)...
       """
   ```

2. **Use nomes descritivos:**
   ```python
   # Bom
   patrimonio_aproximado = fields.Selection(...)
   
   # Ruim
   pat = fields.Selection(...)
   ```

3. **Adicione comentários em lógicas complexas:**
   ```python
   # Verifica se o lead está no estágio de execução ou posterior
   if lead.stage_sequence >= 60:
       # Mostra todas as abas
   ```

#### 4. Teste Suas Mudanças

**Checklist de Testes:**

- [ ] Testado em banco de dados limpo
- [ ] Testado instalação do zero
- [ ] Testado upgrade do módulo
- [ ] Todos os campos salvam corretamente
- [ ] Abas aparecem nos estágios corretos
- [ ] Sem erros no log do Odoo
- [ ] Views carregam sem erro
- [ ] Security rules funcionam (user e manager)
- [ ] Dados iniciais carregam corretamente

**Como Testar:**

```bash
# 1. Criar banco de teste
createdb odoo_test_wealth

# 2. Instalar módulo
odoo-bin -c /etc/odoo.conf -d odoo_test_wealth -i crm_wealth --stop-after-init

# 3. Verificar logs
tail -f /var/log/odoo/odoo-server.log

# 4. Testar via interface
# Abrir Odoo e testar manualmente cada funcionalidade
```

#### 5. Commit com Mensagens Claras

**Formato:**
```
tipo: descrição curta (máx 50 caracteres)

Descrição detalhada do que foi feito e por quê.
Pode ter múltiplas linhas.

Relacionado: #123
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (sem mudança de código)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

**Exemplos:**

```bash
# Bom
git commit -m "feat: adiciona campo email na aba captação

Adiciona campo de email secundário para melhor comunicação
com leads que têm múltiplos contatos.

Relacionado: #45"

# Bom
git commit -m "fix: corrige visibilidade da aba onboarding

A aba estava aparecendo no estágio de proposta quando
deveria aparecer apenas no onboarding.

Corrigido comparação de sequence de >= 40 para >= 50.

Fixes: #67"

# Ruim
git commit -m "mudanças"
git commit -m "fix"
```

#### 6. Push e Pull Request

```bash
git push origin feature/minha-feature
```

No GitHub:
1. Abra Pull Request
2. Preencha o template:
   - O que foi feito
   - Por que foi feito
   - Como testar
   - Screenshots (se aplicável)
3. Aguarde review

### Code Review

Seu PR será revisado considerando:

1. **Funcionalidade:** Resolve o problema proposto?
2. **Código:** Segue as boas práticas?
3. **Testes:** Foi testado adequadamente?
4. **Documentação:** Está documentado?
5. **Compatibilidade:** Não quebra funcionalidades existentes?

## 📝 Convenções de Código

### Python

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class ModelName(models.Model):
    _name = 'module.model.name'
    _description = 'Descrição do Modelo'
    _order = 'sequence, name'

    # Campos sempre nesta ordem:
    # 1. Básicos (Char, Text, Integer, etc)
    name = fields.Char(string='Nome', required=True)
    
    # 2. Seleção
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('done', 'Concluído'),
    ], string='Estado', default='draft')
    
    # 3. Relacionamentos
    partner_id = fields.Many2one('res.partner', string='Parceiro')
    
    # 4. Computados
    total = fields.Float(compute='_compute_total', store=True)
    
    # Métodos sempre nesta ordem:
    # 1. Constrains
    @api.constrains('name')
    def _check_name(self):
        pass
    
    # 2. Depends (computeds)
    @api.depends('field1', 'field2')
    def _compute_total(self):
        pass
    
    # 3. Onchanges
    @api.onchange('partner_id')
    def _onchange_partner(self):
        pass
    
    # 4. CRUD overrides
    def create(self, vals):
        return super().create(vals)
    
    # 5. Métodos de ação
    def action_confirm(self):
        pass
    
    # 6. Métodos auxiliares privados
    def _get_domain(self):
        pass
```

### XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <!-- Sempre comentar seções -->
    <!-- ============================================ -->
    <!-- VIEWS -->
    <!-- ============================================ -->
    
    <record id="model_view_form" model="ir.ui.view">
        <field name="name">model.name.form</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <field name="name"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
    
    <!-- ============================================ -->
    <!-- ACTIONS -->
    <!-- ============================================ -->
    
    <record id="model_action" model="ir.actions.act_window">
        <field name="name">Nome</field>
        <field name="res_model">module.model</field>
        <field name="view_mode">tree,form</field>
    </record>
    
</odoo>
```

## 🐛 Reportando Problemas de Segurança

**NÃO** abra issue pública para problemas de segurança.

Envie email para: **security@gzconsultoria.com.br**

Inclua:
- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial

## 📚 Recursos

- [Documentação Odoo 19](https://www.odoo.com/documentation/19.0/)
- [Boas Práticas Odoo](crm_wealth/BOAS_PRATICAS_ODOO19.md)
- [Guia de Estilo Python (PEP 8)](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Dúvidas

Tem dúvidas sobre como contribuir?

- Abra uma [Discussion](https://github.com/gzconsultoria/crm_wealth_odoo/discussions)
- Entre em contato: contato@geovanezomer.com.br

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a LGPL-3.

---

**Obrigado por contribuir! 🙏**
