# Guia de Troubleshooting - CRM Wealth Management

Este documento lista problemas comuns e suas soluções.

## 🔧 Problemas Comuns

### 1. Módulo não aparece na lista de Apps

**Sintomas:**
- Após copiar o módulo, ele não aparece na lista de aplicativos

**Soluções:**

1. **Atualizar lista de aplicativos:**
   ```
   Settings → Activate Developer Mode
   Apps → Update Apps List
   ```

2. **Verificar o caminho do addon:**
   ```bash
   # Conferir se o módulo está no diretório correto
   ls -la /caminho/para/odoo/addons/crm_wealth
   ```

3. **Verificar configuração do Odoo:**
   ```bash
   # No arquivo odoo.conf
   addons_path = /caminho/para/addons,/outro/caminho
   ```

4. **Reiniciar o Odoo:**
   ```bash
   sudo systemctl restart odoo
   ```

### 2. Erro ao instalar o módulo

**Sintomas:**
- Erro de permissão
- Erro de dependência

**Soluções:**

1. **Erro de permissão:**
   ```bash
   # Ajustar permissões
   sudo chown -R odoo:odoo /caminho/para/addons/crm_wealth
   sudo chmod -R 755 /caminho/para/addons/crm_wealth
   ```

2. **Erro de dependência:**
   - Certifique-se de que os módulos `crm` e `sale_crm` estão instalados
   - No Odoo: Apps → Remover filtro "Apps" → Buscar "crm" → Instalar

3. **Erro de sintaxe Python:**
   ```bash
   # Testar sintaxe
   python3 -m py_compile /caminho/para/addons/crm_wealth/models/crm_lead.py
   ```

### 3. Abas não aparecem ou aparecem todas de uma vez

**Sintomas:**
- Todas as abas estão visíveis independente do estágio
- Nenhuma aba aparece

**Soluções:**

1. **Verificar sequência dos estágios:**
   - CRM → Configuration → Stages
   - Certifique-se de que as sequências estão corretas:
     - Captação: 10
     - Qualificação: 20
     - Reunião: 30
     - Proposta: 40
     - Onboarding: 50
     - Execução: 60

2. **Forçar recálculo:**
   - Edite o lead
   - Mude para outro estágio e volte
   - Salve

3. **Verificar campo computado:**
   ```python
   # No modo desenvolvedor
   # Debug → View Metadata → Ver se stage_sequence está correto
   ```

### 4. Campos não salvam os valores

**Sintomas:**
- Ao preencher campos e salvar, os valores não ficam gravados

**Soluções:**

1. **Verificar permissões:**
   - Settings → Users & Companies → Users
   - Verificar grupo "Sales / User" ou "Sales / Administrator"

2. **Verificar security rules:**
   ```bash
   # Conferir se o arquivo existe
   cat crm_wealth/security/ir.model.access.csv
   ```

3. **Atualizar o módulo:**
   - Apps → CRM Wealth Management → Upgrade

### 5. Erro 500 ao abrir formulário do lead

**Sintomas:**
- Erro 500 Internal Server Error
- Odoo trava ao abrir lead

**Soluções:**

1. **Verificar logs do Odoo:**
   ```bash
   # Ubuntu/Debian
   sudo tail -f /var/log/odoo/odoo-server.log
   
   # Via journalctl
   sudo journalctl -u odoo -f
   ```

2. **Problemas comuns nos logs:**
   - `Field 'xxx' does not exist`: Campo não existe no modelo
   - `View not found`: View XML com erro
   - `Access Denied`: Problema de permissão

3. **Modo debug:**
   ```bash
   # Iniciar Odoo em modo debug
   odoo --config=/etc/odoo.conf --log-level=debug
   ```

### 6. Dados iniciais não carregam

**Sintomas:**
- Após instalar, os estágios personalizados não aparecem
- Interesses, estratégias, etc. não existem

**Soluções:**

1. **Verificar instalação completa:**
   - Apps → CRM Wealth Management → Verificar se status é "Installed"

2. **Instalar manualmente os dados:**
   ```bash
   # Via odoo-bin
   odoo-bin -c /etc/odoo.conf -d seu_database -i crm_wealth --stop-after-init
   ```

3. **Verificar noupdate:**
   - Se você reinstalar, dados com `noupdate="1"` não serão sobrescritos
   - Para forçar update, remova `noupdate` temporariamente

### 7. Campo Many2many não mostra opções

**Sintomas:**
- Campos como "Interesses" ou "Estratégias" estão vazios

**Soluções:**

1. **Criar dados manualmente:**
   - CRM → Configuration → Wealth Management → Interesses
   - Adicionar novos registros

2. **Verificar dados XML:**
   ```bash
   # Verificar se arquivo foi carregado
   grep "crm.wealth.interesse" /var/log/odoo/odoo-server.log
   ```

3. **Reinstalar módulo:**
   - Apps → CRM Wealth Management → Uninstall
   - Apps → CRM Wealth Management → Install

### 8. Performance lenta ao abrir leads

**Sintomas:**
- Formulário demora muito para carregar
- Sistema trava com muitos leads

**Soluções:**

1. **Adicionar índices ao banco:**
   ```sql
   CREATE INDEX idx_crm_lead_stage_sequence ON crm_lead(stage_sequence);
   ```

2. **Usar store=True em campos computados críticos:**
   - Já implementado no módulo para `stage_sequence`

3. **Limitar registros carregados:**
   - Em listas, usar paginação
   - Filtrar por período

## 🔍 Como Debugar

### Modo Desenvolvedor Avançado

1. **Ativar:**
   ```
   Settings → Developer Tools → Activate Developer Mode (with assets)
   ```

2. **View Metadata:**
   - No formulário: Debug → View Metadata
   - Veja IDs, modelo, view usada

3. **Edit View:**
   - Debug → Edit View: Form
   - Editar XML diretamente (cuidado!)

### Python Debug

```python
# Adicionar no código
import logging
_logger = logging.getLogger(__name__)

def _compute_show_tabs(self):
    for lead in self:
        _logger.info(f"Lead {lead.id} - Stage: {lead.stage_id.name} - Seq: {lead.stage_sequence}")
        # ... resto do código
```

### SQL Debug

```sql
-- Ver dados do lead
SELECT id, name, stage_id, stage_sequence FROM crm_lead WHERE id = 1;

-- Ver estágios
SELECT id, name, sequence FROM crm_stage ORDER BY sequence;

-- Ver interesses associados
SELECT * FROM crm_wealth_interesse;
```

## 📞 Suporte

Se nenhuma solução acima resolver seu problema:

1. Abra uma [Issue no GitHub](https://github.com/gzconsultoria/crm_wealth_odoo/issues)
2. Inclua:
   - Versão do Odoo
   - Logs de erro
   - Passos para reproduzir
   - Screenshots se aplicável

## 🔄 Atualização do Módulo

Para atualizar o módulo após mudanças:

```bash
# 1. Copiar novos arquivos
cp -r crm_wealth /caminho/para/addons/

# 2. Reiniciar Odoo
sudo systemctl restart odoo

# 3. No Odoo
Apps → CRM Wealth Management → Upgrade
```

## 🗑️ Desinstalação Limpa

```bash
# 1. No Odoo
Apps → CRM Wealth Management → Uninstall

# 2. Remover arquivos
rm -rf /caminho/para/addons/crm_wealth

# 3. Reiniciar
sudo systemctl restart odoo
```

**Nota:** A desinstalação remove os dados customizados (estágios, interesses, etc.)
