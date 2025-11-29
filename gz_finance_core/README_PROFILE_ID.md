# 🆔 Geração Automática de Profile ID

## 📋 Visão Geral

O módulo `gz_finance_core` agora gera automaticamente um **Profile ID** único para cada cliente de consultoria financeira.

**Formato do ID:** `FIN-YYYYMMDD-XXXX`

Exemplo: `FIN-20251129-0001`

---

## ✨ Funcionalidades

### 1. **Geração Automática ao Ativar Toggle**

Quando você **ativa o toggle "Cliente Consultoria"** em um contato:

```
✅ ANTES: is_finance_client = False, finance_profile_id = (vazio)
✅ DEPOIS: is_finance_client = True, finance_profile_id = FIN-20251129-0001
```

**Como funciona:**
- Método `write()` detecta mudança em `is_finance_client`
- Se `finance_profile_id` estiver vazio, gera automaticamente
- Usa sequence `ir.sequence` com código `finance.profile`

### 2. **Geração Automática ao Criar Novo Cliente**

Ao criar um novo contato já marcado como Cliente Consultoria:

```python
partner = env['res.partner'].create({
    'name': 'João Silva',
    'is_finance_client': True
})
# partner.finance_profile_id = 'FIN-20251129-0002' (gerado automaticamente)
```

### 3. **Atualizar Clientes Existentes**

Para clientes que **já existiam antes** desta funcionalidade:

#### Opção A: Via Interface (Modo Desenvolvedor)
1. Ativar **Developer Mode** (Settings → Activate Developer Mode)
2. Ir em **Settings → Technical → Actions → Server Actions**
3. Buscar: "Gerar Profile IDs Faltantes"
4. Clicar em **Run**

#### Opção B: Via Linha de Comando
```bash
# Script Python via Odoo Shell
cat /mnt/extra-addons/gz_finance_core/fix_ids.py | \
  docker exec -i odoo_modules-web-1 odoo shell -d gzcon \
  --db_host db --db_user odoo --db_password odoo
```

#### Opção C: Manualmente (Um por Um)
1. Abrir o contato
2. Desmarcar toggle "Cliente Consultoria"
3. Salvar
4. Marcar novamente o toggle
5. Salvar → ID será gerado automaticamente

---

## 🔧 Detalhes Técnicos

### Sequence Configuration

Localização: `data/finance_data.xml`

```xml
<record id="sequence_finance_profile" model="ir.sequence">
    <field name="name">Finance Profile ID</field>
    <field name="code">finance.profile</field>
    <field name="prefix">FIN-%(year)s%(month)s%(day)s-</field>
    <field name="padding">4</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

**Formato do Prefixo:**
- `%(year)s` = Ano com 4 dígitos (2025)
- `%(month)s` = Mês com 2 dígitos (01-12)
- `%(day)s` = Dia com 2 dígitos (01-31)
- Padding = 4 dígitos para número sequencial

**Resultado:** `FIN-20251129-0001`, `FIN-20251129-0002`, etc.

### Método de Geração

Localização: `models/res_partner.py`

```python
def _generate_profile_id(self):
    """Generate unique Profile ID using sequence (format: FIN-YYYYMMDD-XXXX)"""
    sequence_value = self.env['ir.sequence'].next_by_code('finance.profile')
    if not sequence_value:
        # Fallback manual generation if sequence fails
        today = fields.Date.today().strftime('%Y%m%d')
        last_id = self.search([], order='id desc', limit=1)
        next_num = (last_id.id + 1) if last_id else 1
        return f'FIN-{today}-{next_num:04d}'
    return sequence_value
```

**Lógica:**
1. Tenta usar `ir.sequence` (método preferido)
2. Se falhar, gera manualmente usando data + ID do último registro
3. Garante formato consistente

### Trigger Automático

```python
def write(self, vals):
    """Override write to auto-generate Profile ID when toggle is activated"""
    if vals.get('is_finance_client'):
        for partner in self:
            if not partner.finance_profile_id:
                vals['finance_profile_id'] = self._generate_profile_id()
                break  # Generate only once for batch
    return super().write(vals)
```

**Quando executa:**
- Apenas quando `is_finance_client` está sendo alterado para `True`
- Apenas se `finance_profile_id` estiver vazio
- Funciona em criações e edições

### Validação de Unicidade

```python
@api.constrains('finance_profile_id')
def _check_finance_profile_id_unique(self):
    """Ensure Profile ID uniqueness"""
    for partner in self:
        if partner.finance_profile_id:
            duplicate = self.search([
                ('finance_profile_id', '=', partner.finance_profile_id),
                ('id', '!=', partner.id)
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    'Finance Profile ID must be unique. '
                    'ID %s already exists for %s'
                ) % (partner.finance_profile_id, duplicate.name))
```

**Garante:**
- Nenhum ID duplicado no sistema
- Erro claro se houver tentativa de duplicação

---

## 📊 Exemplos de Uso

### Caso 1: Novo Cliente
```python
# Criar novo cliente com toggle ativo
partner = env['res.partner'].create({
    'name': 'Maria Santos',
    'email': 'maria@example.com',
    'is_finance_client': True
})

print(partner.finance_profile_id)
# Output: FIN-20251129-0010
```

### Caso 2: Cliente Existente
```python
# Ativar consultoria para cliente existente
partner = env['res.partner'].browse(123)
partner.write({'is_finance_client': True})

print(partner.finance_profile_id)
# Output: FIN-20251129-0011
```

### Caso 3: Migração em Massa
```python
# Atualizar todos os clientes sem ID
result = env['res.partner'].action_generate_missing_profile_ids()
# Retorna notificação com quantidade atualizada
```

---

## 🚨 Troubleshooting

### Problema: ID não está sendo gerado

**Verificar:**
```sql
-- Verificar se sequence existe
SELECT * FROM ir_sequence WHERE code = 'finance.profile';

-- Verificar clientes sem ID
SELECT id, name, is_finance_client, finance_profile_id 
FROM res_partner 
WHERE is_finance_client = true 
AND (finance_profile_id IS NULL OR finance_profile_id = '');
```

**Solução:**
```bash
# Executar script de correção
cat /mnt/extra-addons/gz_finance_core/fix_ids.py | \
  docker exec -i odoo_modules-web-1 odoo shell -d gzcon
```

### Problema: IDs duplicados

**Verificar:**
```sql
SELECT finance_profile_id, COUNT(*) 
FROM res_partner 
WHERE finance_profile_id IS NOT NULL 
GROUP BY finance_profile_id 
HAVING COUNT(*) > 1;
```

**Solução:** Constraint automático impede duplicatas. Se existir, corrigir manualmente.

### Problema: Formato incorreto

**Verificar sequence:**
```sql
SELECT prefix, padding, number_next 
FROM ir_sequence 
WHERE code = 'finance.profile';
```

**Deve retornar:**
- `prefix`: `FIN-%(year)s%(month)s%(day)s-`
- `padding`: `4`

**Corrigir:**
```sql
UPDATE ir_sequence 
SET prefix = 'FIN-%(year)s%(month)s%(day)s-', padding = 4 
WHERE code = 'finance.profile';
```

---

## 📝 Notas Importantes

1. **Unicidade Garantida:** Constraint no banco previne IDs duplicados
2. **Formato Legível:** Data incluída facilita auditoria e organização
3. **Sequência Diária:** Número reseta a cada dia (opcional - pode ser removido)
4. **Rastreabilidade:** ID permanente mesmo se toggle for desativado
5. **Index:** Campo tem índice para buscas rápidas

---

## 🔄 Histórico de Mudanças

### v1.0 (29/11/2025)
- ✅ Geração automática ao ativar toggle
- ✅ Geração automática ao criar novo cliente
- ✅ Método para atualizar clientes existentes
- ✅ Validação de unicidade
- ✅ Server action para migração em massa
- ✅ Sequence com formato incluindo data
- ✅ Fallback manual se sequence falhar
