# ✅ CHECKLIST RÁPIDO - Deploy Odoo 19 para Contabo

## 🎯 O QUE VOCÊ PRECISA FAZER AGORA

### **PASSO 1: Editar Arquivo .env** ⚠️ CRÍTICO

```bash
cd /workspaces/ODOO_Modules/deploy/config

# Copiar template
cp .env.production.template .env.production

# EDITAR COM SUAS INFORMAÇÕES REAIS
nano .env.production
```

**Mude estas linhas:**

```env
POSTGRES_PASSWORD=SuaSenhaSuperForte123!ABC
ODOO_ADMIN_PASSWORD=OutraSenhaSegura456!XYZ
DOMAIN=odoo.gzconsultoria.com.br         # SEU DOMÍNIO
EMAIL_ADMIN=admin@gzconsultoria.com.br    # SEU EMAIL
```

**❌ NUNCA commite este arquivo no Git!**

---

### **PASSO 2: Contratar VPS no Contabo**

1. Acesse: https://my.contabo.com
2. **Cloud VPS** → **Create VPS**
3. Configuração mínima:
   - **RAM:** 8GB
   - **CPU:** 4 vCPU
   - **Storage:** 50GB SSD
   - **OS:** Ubuntu 24.04 LTS
   - **Location:** Europa (melhor latência)
   - **Backup:** Ativar (diário)

4. Anote credenciais do email:
   ```
   IP: 123.456.789.10
   User: root
   Password: senha_temporaria_contabo
   ```

**Custo estimado:** €8-12/mês

---

### **PASSO 3: Configurar DNS**

No seu provedor de domínio (ex: Registro.br, Cloudflare):

```
Tipo: A
Nome: odoo (ou @)
Valor: 123.456.789.10  ← IP do Contabo
TTL: 3600
```

**Aguardar 5-30 minutos** para propagação.

Testar:
```bash
ping odoo.gzconsultoria.com.br
# Deve responder com o IP do Contabo
```

---

### **PASSO 4: Primeira Conexão SSH**

```bash
# Conectar ao servidor
ssh root@123.456.789.10

# Trocar senha (obrigatório)
passwd

# Atualizar sistema
apt update && apt upgrade -y

# Sair
exit
```

---

### **PASSO 5: Copiar Script de Deploy**

**No seu PC local:**

```bash
cd /workspaces/ODOO_Modules/deploy/config

# Copiar script para servidor
scp deploy_to_contabo.sh root@123.456.789.10:/root/

# Dar permissão
ssh root@123.456.789.10 "chmod +x /root/deploy_to_contabo.sh"
```

---

### **PASSO 6: Editar Variáveis no Script**

```bash
# Conectar
ssh root@123.456.789.10

# Editar script
nano /root/deploy_to_contabo.sh

# Mudar estas 2 linhas (aproximadamente linha 20-21):
DOMAIN="odoo.gzconsultoria.com.br"  # ← SEU DOMÍNIO
EMAIL="admin@gzconsultoria.com.br"  # ← SEU EMAIL

# Salvar: Ctrl+O, Enter, Ctrl+X
```

---

### **PASSO 7: Executar Deploy Automatizado**

**No servidor (via SSH):**

```bash
# Executar script
bash /root/deploy_to_contabo.sh

# O script irá:
# [1/10] Atualizar sistema ✅
# [2/10] Configurar firewall ✅
# [3/10] Instalar Docker ✅
# [4/10] Instalar Docker Compose ✅
# [5/10] Criar diretórios ✅
# [6/10] Configurar .env (senhas aleatórias) ✅
# [7/10] SSL Let's Encrypt ⏸️ (perguntar se quer)
# [8/10] Aguardar módulos ⏸️ (você copia)
# [9/10] Aguardar backup ⏸️ (você copia)
# [10/10] Iniciar Odoo ✅
```

**Quando o script pausar:**

---

### **PASSO 8: Transferir Dados**

**Abra NOVO terminal no seu PC local:**

```bash
cd /workspaces/ODOO_Modules

# 1. Arquivo .env (EDITADO!)
scp deploy/config/.env.production root@123.456.789.10:/opt/odoo/.env

# 2. Módulos customizados
scp -r gz_finance_core \
       gz_finance_crm \
       gz_finance_docs \
       root@123.456.789.10:/opt/odoo/addons/

# 3. Backup do banco
scp deploy/backups/gzcon_*.dump \
    root@123.456.789.10:/opt/odoo/backups/database/

# 4. Configurações
scp deploy/config/docker-compose.production.yml \
    root@123.456.789.10:/opt/odoo/docker-compose.yml
    
scp deploy/config/odoo.conf \
    root@123.456.789.10:/opt/odoo/
    
scp deploy/config/nginx.conf \
    root@123.456.789.10:/opt/odoo/
    
scp deploy/config/backup.sh \
    root@123.456.789.10:/opt/odoo/scripts/

# Dar permissão ao script de backup
ssh root@123.456.789.10 "chmod +x /opt/odoo/scripts/backup.sh"
```

**Depois volte ao terminal SSH e pressione ENTER para continuar**

---

### **PASSO 9: Aguardar Inicialização**

O script irá:

1. ✅ Restaurar banco de dados (gzcon)
2. ✅ Iniciar containers Docker
3. ✅ Configurar SSL
4. ✅ Mostrar status

**Aguarde ~60 segundos**

---

### **PASSO 10: TESTAR ACESSO** 🎉

Abra navegador:

```
https://odoo.gzconsultoria.com.br
```

**Login:**
- **Database:** gzcon
- **Email:** admin@gzconsultoria.com.br
- **Senha:** (a que você definiu no .env como ODOO_ADMIN_PASSWORD)

**Verificar:**
1. ✅ HTTPS ativo (cadeado verde)
2. ✅ Menu "Consultoria" → "Clientes Financeiros"
3. ✅ Menu "Consultoria" → "Documentos Financeiros"
4. ✅ Apps → Módulos instalados: gz_finance_core, gz_finance_crm

---

## 🔧 PASSO 11: Configurar Backup Automático

**No servidor:**

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup às 2:00 AM todos os dias):
0 2 * * * /opt/odoo/scripts/backup.sh >> /opt/odoo/logs/backup.log 2>&1

# Salvar e sair
```

**Testar backup manual:**

```bash
bash /opt/odoo/scripts/backup.sh

# Ver backups criados
ls -lh /opt/odoo/backups/database/
ls -lh /opt/odoo/backups/filestore/
```

---

## 🎯 RESUMO FINAL

### ✅ O que você tem AGORA:

- ✅ Backup do banco (5.4MB)
- ✅ Módulos prontos (gz_finance_core, crm, docs)
- ✅ Script de deploy automatizado
- ✅ Configurações de produção (Docker, Nginx, SSL)
- ✅ .gitignore seguro (sem senhas no Git)
- ✅ Guia completo passo a passo

### 🚀 Próximos Passos:

1. ⏳ Contratar VPS no Contabo
2. ⏳ Configurar DNS do domínio
3. ⏳ Executar deploy (30-40 minutos)
4. ⏳ Testar sistema em produção
5. ⏳ Configurar backups automáticos

---

## 📞 Suporte

**Dúvidas?** Consulte:

- **Guia Completo:** `/workspaces/ODOO_Modules/deploy/GUIA_DEPLOY_CONTABO.md`
- **README:** `/workspaces/ODOO_Modules/deploy/README.md`

**Comandos úteis:**

```bash
# Ver logs do Odoo
docker-compose logs -f web

# Reiniciar Odoo
docker-compose restart web

# Status dos containers
docker-compose ps

# Backup manual
bash /opt/odoo/scripts/backup.sh
```

---

**🎉 Pronto! Tudo está preparado para o deploy em produção!**

**Tempo estimado total:** 1-2 horas (incluindo propagação DNS)
