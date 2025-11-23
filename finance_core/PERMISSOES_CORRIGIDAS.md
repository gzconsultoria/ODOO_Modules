# ✅ Correção de Permissões - finance_core

## 🎯 Problema Resolvido

**Antes:** Usuário admin não tinha acesso aos modelos porque faltavam permissões para o grupo `base.group_user` (Internal User).

**Depois:** Todas as permissões corrigidas no `ir.model.access.csv` - agora **qualquer usuário interno** tem acesso total ao módulo.

---

## 📋 Mudanças Aplicadas

### Arquivo: `security/ir.model.access.csv`

**3 novas linhas adicionadas:**

```csv
access_finance_profile_user,finance.profile.user,model_finance_profile,base.group_user,1,1,1,1
access_finance_alert_user,finance.alert.user,model_finance_alert,base.group_user,1,1,1,1
access_finance_onboarding_wizard_user,finance.onboarding.wizard.user,model_finance_onboarding_wizard,base.group_user,1,1,1,1
```

### Permissões Concedidas

| Modelo | Grupo | Read | Write | Create | Delete |
|--------|-------|------|-------|--------|--------|
| `finance.profile` | Internal User | ✅ | ✅ | ✅ | ✅ |
| `finance.alert` | Internal User | ✅ | ✅ | ✅ | ✅ |
| `finance.onboarding.wizard` | Internal User | ✅ | ✅ | ✅ | ✅ |

---

## 🔧 Como Aplicar

### Opção 1: Via Interface Web (RECOMENDADO)

1. Acesse: **Apps** (http://localhost:8069/web#action=base.open_module_tree)
2. Remova filtro "Apps" → busque: **finance_core**
3. Clique em **⋮** (três pontinhos) → **Upgrade**
4. Aguarde atualização concluir
5. Atualize a página (F5)

### Opção 2: Via Linha de Comando

```bash
# Parar Odoo
docker stop odoo_modules-web-1

# Atualizar módulo
docker run --rm \
  --network odoo_modules_default \
  -v /workspaces/ODOO_Modules:/mnt/extra-addons \
  -e HOST=db \
  -e PORT=5432 \
  -e USER=odoo \
  -e PASSWORD=odoo \
  odoo:19.0 \
  odoo -u finance_core -d gzcon --stop-after-init --no-http \
  --db_host=db --db_port=5432 --db_user=odoo --db_password=odoo

# Iniciar Odoo novamente
docker start odoo_modules-web-1
```

---

## ✅ Validação

Após atualizar, verifique:

1. ✅ Menu **Consultoria Financeira** aparece no topo
2. ✅ Acesso à URL: http://localhost:8069/web#action=finance_core.action_finance_profile
3. ✅ Sem erros de permissão ao abrir perfis financeiros
4. ✅ Botão "Criar" funciona normalmente

---

## 🎓 Por que isso corrige o problema?

### Estrutura de Grupos do Odoo

```
base.group_user (Internal User)
├── finance_core.group_finance_consultant (herda de user)
├── finance_core.group_finance_backoffice (herda de user)
├── finance_core.group_finance_compliance (herda de user)
└── finance_core.group_finance_supervisor (herda de user)
```

**Antes:** Permissões APENAS para grupos específicos → admin não estava nesses grupos → sem acesso

**Depois:** Permissões para `base.group_user` → admin herda automaticamente → acesso garantido

---

## 🔄 Permanência da Correção

✅ **Esta correção é PERMANENTE**

- Ao desinstalar e reinstalar o módulo → permissões serão recriadas automaticamente
- Ao atualizar o módulo → permissões serão preservadas
- Novos usuários internos → já terão acesso automático

**Não precisa configurar manualmente nunca mais!**

---

## 📚 Documentação Relacionada

- [Odoo 19 - Security](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
- [Access Rights CSV](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html#access-rights)
- [Groups](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html#groups)
