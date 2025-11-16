# Configuração de Menus - Wealth Management

## 📋 Resumo

Todos os menus de configuração do módulo **CRM Wealth Management** foram movidos para o menu **Técnico**, com acesso restrito apenas para desenvolvedores.

## 🎯 Localização

**Menu Principal**: `Técnico → Wealth Management`

**Visibilidade**: Apenas em modo desenvolvedor (requer grupo `base.group_no_one` - "Procedimentos técnicos")

## 📂 Estrutura de Menus

### Menu Principal
- **Nome**: Wealth Management
- **ID XML**: `crm_wealth.menu_crm_wealth_root`
- **Parent**: `base.menu_custom` (Menu Técnico)
- **Grupos**: `base.group_no_one` (Procedimentos técnicos)

### Submenus (6)

| Seq | Nome | Modelo | Descrição |
|-----|------|--------|-----------|
| 1 | Taxas e SLAs | `res.config.settings` | Configurar taxas de rendimento e SLAs |
| 10 | Interesses | `crm.wealth.interesse` | Gerenciar interesses de investimento |
| 20 | Estratégias | `crm.wealth.estrategia` | Gerenciar estratégias de investimento |
| 30 | Objeções | `crm.wealth.objecao` | Cadastrar objeções e tratativas |
| 40 | Documentos | `crm.wealth.documento` | Tipos de documentos para onboarding |
| 50 | Corretoras | `crm.wealth.corretora` | Corretoras parceiras |

Todos os submenus também possuem acesso restrito ao grupo `base.group_no_one`.

## 🔐 Como Acessar

### 1. Ativar Modo Desenvolvedor
```
Configurações → Ativar modo desenvolvedor
```
Ou adicionar `?debug=1` na URL:
```
https://seu-odoo.com/web?debug=1
```

### 2. Acessar o Menu
```
Menu Superior → Técnico → Wealth Management → [escolher submenu]
```

## 📝 Arquivos Modificados

### `/crm_wealth/views/crm_wealth_menus.xml`

```xml
<!-- Menu principal -->
<menuitem 
    id="menu_crm_wealth_root"
    name="Wealth Management"
    parent="base.menu_custom"
    sequence="100"
    groups="base.group_no_one"/>

<!-- Submenus -->
<menuitem 
    id="menu_crm_wealth_interesse"
    name="Interesses"
    parent="menu_crm_wealth_root"
    action="action_crm_wealth_interesse"
    sequence="10"
    groups="base.group_no_one"/>
<!-- ... outros submenus seguem o mesmo padrão -->
```

## ✅ Mudanças Implementadas

1. ✅ Menu movido de `base.menu_administration` (Configuração) para `base.menu_custom` (Técnico)
2. ✅ Adicionado grupo `groups="base.group_no_one"` a todos os menus
3. ✅ Removidos menus duplicados antigos do banco de dados
4. ✅ Reparentados todos os submenus órfãos para o menu correto
5. ✅ Verificada estrutura final: 1 menu principal + 6 submenus

## 🔍 Verificação

Para verificar a estrutura atual via Odoo shell:

```python
wealth_menu = env.ref('crm_wealth.menu_crm_wealth_root')
print(f"Parent: {wealth_menu.parent_id.name}")  # → Técnico
print(f"Grupos: {wealth_menu.group_ids.mapped('name')}")  # → ['Administrador', 'Procedimentos técnicos']

submenus = env['ir.ui.menu'].search([('parent_id', '=', wealth_menu.id)], order='sequence')
print(f"Total submenus: {len(submenus)}")  # → 6
```

## 💡 Benefícios

- **Segurança**: Apenas desenvolvedores podem acessar configurações técnicas
- **Organização**: Menus técnicos separados de configurações do usuário
- **Consistência**: Segue padrões do Odoo para menus administrativos
- **Manutenção**: Fácil identificação de configurações avançadas

## 📚 Referências

- **Menu Técnico**: `base.menu_custom` (Technical)
- **Grupo de Acesso**: `base.group_no_one` (Technical Features)
- **Documentação**: https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html
