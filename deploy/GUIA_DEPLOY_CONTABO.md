# 🚀 GUIA COMPLETO: Deploy Odoo 19 para Produção (Contabo VPS)

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Preparação do Ambiente Local](#preparação-do-ambiente-local)
3. [Provisionamento do VPS Contabo](#provisionamento-do-vps-contabo)
4. [Instalação e Configuração](#instalação-e-configuração)
5. [Transferência de Dados](#transferência-de-dados)
6. [Inicialização e Testes](#inicialização-e-testes)
7. [Manutenção e Backups](#manutenção-e-backups)
8. [Troubleshooting](#troubleshooting)

---

## 📦 Pré-requisitos

### No seu computador local:
- ✅ Git instalado
- ✅ SSH client configurado
- ✅ Backup do banco `gzcon` criado (5.4MB)
- ✅ Módulos `gz_finance_core` e `gz_finance_crm` atualizados

### No Contabo:
- 🖥️ **VPS Mínimo Recomendado:**
  - CPU: 4 vCPU
  - RAM: 8GB
  - Disco: 50GB SSD
  - OS: Ubuntu 24.04 LTS
- 🌐 **Domínio configurado** (ex: `odoo.gzconsultoria.com.br`)
- 📧 **Email válido** para certificado SSL

---

## 🛠️ PASSO 1: Preparação do Ambiente Local

### 1.1 Verificar Backup do Banco

```bash
cd /workspaces/ODOO_Modules
ls -lh deploy/backups/

# Deve mostrar:
# gzcon_20251206_134009.dump (5.4M)
```

### 1.2 Empacotar Módulos Customizados

```bash
# Criar tarball dos módulos gz_finance
tar czf deploy/backups/gz_finance_modules.tar.gz \
    gz_finance_core/ \
    gz_finance_crm/ \
    gz_finance_docs/

# Verificar tamanho
ls -lh deploy/backups/gz_finance_modules.tar.gz
```

### 1.3 Preparar Arquivo .env (IMPORTANTE!)

```bash
# Copiar template
cp deploy/config/.env.production.template deploy/config/.env.production

# EDITAR COM SUAS SENHAS (NUNCA COMMITAR!)
nano deploy/config/.env.production
```

**Exemplo de .env configurado:**

```env
POSTGRES_PASSWORD=Sua_Senha_Super_Forte_123!ABC
ODOO_ADMIN_PASSWORD=Outra_Senha_Muito_Segura_456!XYZ
DOMAIN=odoo.gzconsultoria.com.br
EMAIL_ADMIN=admin@gzconsultoria.com.br
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app-gmail
SMTP_SSL=True
```

---

## 🌐 PASSO 2: Provisionamento do VPS Contabo

### 2.1 Criar VPS no Painel Contabo

1. Acesse: https://my.contabo.com
2. Vá em **Cloud VPS** → **Create VPS**
3. Configuração:
   - **Location:** Europa (baixa latência Brasil)
   - **OS:** Ubuntu 24.04 LTS
   - **RAM:** 8GB (mínimo)
   - **CPU:** 4 vCPU
   - **Storage:** 50GB SSD
   - **Backup:** Ative backup automático diário

4. Anote as credenciais enviadas por email:
   ```
   IP: 123.456.789.10
   User: root
   Password: senha_temporaria
   ```

### 2.2 Configurar DNS do Domínio

No seu provedor de DNS (ex: Cloudflare, Registro.br):

```
Tipo: A
Nome: odoo (ou @)
Valor: 123.456.789.10
TTL: 3600
```

Aguardar propagação DNS (5-30 minutos):

```bash
# Testar no seu PC local
nslookup odoo.gzconsultoria.com.br
```

### 2.3 Primeira Conexão SSH

```bash
# Conectar via SSH
ssh root@123.456.789.10

# Na primeira conexão, trocar senha
passwd

# Atualizar sistema
apt update && apt upgrade -y
```

### 2.4 Criar Usuário Admin (Opcional mas Recomendado)

```bash
# Criar usuário
adduser odoo-admin
usermod -aG sudo odoo-admin

# Copiar chave SSH (do seu PC local)
ssh-copy-id odoo-admin@123.456.789.10

# Testar conexão
ssh odoo-admin@123.456.789.10
```

---

## 🐳 PASSO 3: Instalação Automatizada

### 3.1 Transferir Script de Deploy

**No seu PC local:**

```bash
cd /workspaces/ODOO_Modules/deploy/config

# Copiar script para servidor
scp deploy_to_contabo.sh root@123.456.789.10:/root/

# Dar permissão de execução
ssh root@123.456.789.10 "chmod +x /root/deploy_to_contabo.sh"
```

### 3.2 Executar Deploy Automatizado

**No servidor (via SSH):**

```bash
ssh root@123.456.789.10

# ANTES DE EXECUTAR: Editar variáveis no script
nano /root/deploy_to_contabo.sh

# Mudar estas linhas:
# DOMAIN="odoo.gzconsultoria.com.br"  # SEU DOMÍNIO
# EMAIL="admin@gzconsultoria.com.br"  # SEU EMAIL

# Executar deploy
bash /root/deploy_to_contabo.sh
```

O script irá:
1. ✅ Atualizar sistema
2. ✅ Configurar firewall (UFW)
3. ✅ Instalar Docker + Docker Compose
4. ✅ Criar estrutura de diretórios
5. ✅ Gerar senhas seguras (.env)
6. ✅ Obter certificado SSL (Let's Encrypt)
7. ⏸️ Aguardar upload dos módulos
8. ⏸️ Aguardar upload do backup
9. ✅ Restaurar banco de dados
10. ✅ Iniciar Odoo

---

## 📤 PASSO 4: Transferência de Dados

### 4.1 Copiar Arquivo .env

**No seu PC local:**

```bash
cd /workspaces/ODOO_Modules/deploy/config

# Transferir .env (EDITADO COM SUAS SENHAS!)
scp .env.production root@123.456.789.10:/opt/odoo/.env
```

### 4.2 Copiar Módulos Customizados

```bash
# Transferir módulos
scp -r /workspaces/ODOO_Modules/gz_finance_core \
       /workspaces/ODOO_Modules/gz_finance_crm \
       /workspaces/ODOO_Modules/gz_finance_docs \
       root@123.456.789.10:/opt/odoo/addons/

# Verificar no servidor
ssh root@123.456.789.10 "ls -la /opt/odoo/addons/"
```

### 4.3 Copiar Backup do Banco

```bash
cd /workspaces/ODOO_Modules/deploy/backups

# Transferir dump do banco
scp gzcon_20251206_134009.dump \
    root@123.456.789.10:/opt/odoo/backups/database/
```

### 4.4 Copiar Arquivos de Configuração

```bash
cd /workspaces/ODOO_Modules/deploy/config

# Transferir docker-compose
scp docker-compose.production.yml \
    root@123.456.789.10:/opt/odoo/docker-compose.yml

# Transferir odoo.conf
scp odoo.conf root@123.456.789.10:/opt/odoo/

# Transferir nginx.conf
scp nginx.conf root@123.456.789.10:/opt/odoo/

# Transferir script de backup
scp backup.sh root@123.456.789.10:/opt/odoo/scripts/
ssh root@123.456.789.10 "chmod +x /opt/odoo/scripts/backup.sh"
```

---

## 🚀 PASSO 5: Inicialização

### 5.1 Iniciar Containers

**No servidor (via SSH):**

```bash
ssh root@123.456.789.10
cd /opt/odoo

# Substituir variáveis de ambiente no nginx.conf
source .env
envsubst '${DOMAIN}' < nginx.conf > nginx.conf.tmp
mv nginx.conf.tmp nginx.conf

# Iniciar apenas PostgreSQL primeiro
docker-compose up -d db

# Aguardar 10 segundos
sleep 10

# Restaurar banco de dados
BACKUP_FILE=$(ls -t backups/database/*.dump | head -1)
docker exec -i postgres_production createdb -U odoo gzcon || true
cat $BACKUP_FILE | docker exec -i postgres_production pg_restore -U odoo -d gzcon

# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f web
```

### 5.2 Verificar Status

```bash
# Ver containers rodando
docker-compose ps

# Deve mostrar:
# odoo_production      running   8069/tcp
# postgres_production  running   5432/tcp
# nginx_production     running   80/tcp, 443/tcp
# certbot_production   running

# Verificar logs do Odoo
docker-compose logs --tail=100 web

# Verificar saúde dos containers
docker-compose exec web curl -f http://localhost:8069/web/health
```

---

## ✅ PASSO 6: Testes e Configuração

### 6.1 Acessar Odoo

Abra o navegador e acesse:

```
https://odoo.gzconsultoria.com.br
```

**Credenciais:**
- **Database:** gzcon
- **Email:** admin@gzconsultoria.com.br
- **Password:** (a que você definiu no .env como ODOO_ADMIN_PASSWORD)

### 6.2 Verificar Módulos Instalados

1. Vá em **Apps** → **Update Apps List**
2. Procure por `gz_finance`
3. Devem aparecer:
   - ✅ **GZ Finance Core** (instalado)
   - ✅ **GZ Finance CRM** (instalado)
   - ⏳ **GZ Finance Docs** (para instalar)

### 6.3 Instalar Módulos Pendentes

```bash
# Via interface web:
Apps → Search "gz_finance_docs" → Install

# OU via linha de comando:
docker-compose exec web odoo -c /etc/odoo/odoo.conf \
    -d gzcon -u gz_finance_docs --stop-after-init
docker-compose restart web
```

### 6.4 Testar Funcionalidades

1. **Menu Consultoria** → Deve aparecer no header
2. **Clientes Financeiros** → Criar cliente teste
3. **Documentos Financeiros** → Upload de arquivo teste
4. **Dados & Histórico** → Verificar registros

---

## 🔄 PASSO 7: Configurar Backups Automáticos

### 7.1 Configurar Cron Job

**No servidor:**

```bash
# Editar crontab do root
crontab -e

# Adicionar linha (backup diário às 2:00 AM):
0 2 * * * /opt/odoo/scripts/backup.sh >> /opt/odoo/logs/backup.log 2>&1

# Salvar e sair
```

### 7.2 Testar Backup Manual

```bash
# Executar backup manualmente
bash /opt/odoo/scripts/backup.sh

# Verificar arquivos criados
ls -lh /opt/odoo/backups/database/
ls -lh /opt/odoo/backups/filestore/
```

### 7.3 (Opcional) Backup para Google Drive

```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar Google Drive
rclone config

# Nome: gdrive
# Tipo: drive
# Seguir instruções de autenticação

# Adicionar ao script backup.sh (no final):
nano /opt/odoo/scripts/backup.sh

# Adicionar:
# rclone sync /opt/odoo/backups gdrive:odoo-backups/
```

---

## 🔐 PASSO 8: Segurança Adicional

### 8.1 Configurar Fail2Ban

```bash
apt install -y fail2ban

# Configurar para proteger SSH
cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
fail2ban-client status sshd
```

### 8.2 Habilitar 2FA no Odoo

1. Apps → Search "auth_totp" → Install
2. Settings → Users → Admin → Enable Two-Factor
3. Scan QR code com Google Authenticator

### 8.3 Alterar Porta SSH (Recomendado)

```bash
# Editar configuração SSH
nano /etc/ssh/sshd_config

# Mudar linha:
Port 2222  # Nova porta (ao invés de 22)

# Salvar e reiniciar
systemctl restart sshd

# Atualizar firewall
ufw allow 2222/tcp
ufw delete allow 22/tcp

# Testar NOVA conexão (NÃO FECHE A SESSÃO ATUAL!)
ssh -p 2222 root@123.456.789.10
```

---

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
# Logs do Odoo
docker-compose logs -f web

# Logs do PostgreSQL
docker-compose logs -f db

# Logs do Nginx
docker-compose logs -f nginx

# Todos os logs
docker-compose logs -f
```

### Estatísticas de Recursos

```bash
# Ver uso de CPU/RAM dos containers
docker stats

# Espaço em disco
df -h

# Tamanho do banco de dados
docker exec postgres_production psql -U odoo -d gzcon -c \
    "SELECT pg_database_size('gzcon') / 1024 / 1024 AS size_mb;"
```

---

## 🛠️ Troubleshooting

### Problema: Odoo não inicia

```bash
# Verificar logs
docker-compose logs web | grep -i error

# Reiniciar containers
docker-compose restart

# Rebuild completo
docker-compose down
docker-compose up -d --build
```

### Problema: SSL não funciona

```bash
# Verificar certificado
certbot certificates

# Renovar manualmente
certbot renew --force-renewal

# Reiniciar nginx
docker-compose restart nginx
```

### Problema: Banco de dados corrompido

```bash
# Restaurar último backup
BACKUP=$(ls -t /opt/odoo/backups/database/*.dump | head -1)
docker exec -i postgres_production dropdb -U odoo gzcon
docker exec -i postgres_production createdb -U odoo gzcon
cat $BACKUP | docker exec -i postgres_production pg_restore -U odoo -d gzcon
docker-compose restart web
```

### Problema: Falta de memória

```bash
# Ver uso de memória
free -h

# Adicionar swap (se necessário)
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 📞 Suporte

### Logs Importantes

- **Odoo:** `/var/log/odoo/odoo.log` (dentro do container)
- **Nginx:** `/var/log/nginx/odoo_access.log` e `odoo_error.log`
- **PostgreSQL:** `docker-compose logs db`

### Comandos Úteis

```bash
# Entrar no container Odoo
docker-compose exec web bash

# Entrar no PostgreSQL
docker-compose exec db psql -U odoo -d gzcon

# Ver configuração ativa do Odoo
docker-compose exec web cat /etc/odoo/odoo.conf

# Restart rápido
docker-compose restart web

# Parar tudo
docker-compose down

# Remover volumes (CUIDADO! Apaga dados)
docker-compose down -v
```

---

## ✅ Checklist Final

Antes de considerar o deploy concluído:

- [ ] Odoo acessível via HTTPS no domínio
- [ ] Certificado SSL válido (cadeado verde)
- [ ] Módulos `gz_finance_*` instalados e funcionando
- [ ] Menu "Consultoria" → "Documentos Financeiros" visível
- [ ] Backup automático configurado (cron)
- [ ] Firewall ativo (apenas portas 22/2222, 80, 443)
- [ ] Fail2Ban ativo para SSH
- [ ] 2FA habilitado no usuário admin
- [ ] Senhas fortes e armazenadas em local seguro
- [ ] DNS do domínio apontando corretamente
- [ ] Backup manual testado e funcionando
- [ ] Monitoramento de logs funcionando

---

## 🎉 Próximos Passos

1. **Configurar usuários e permissões** no Odoo
2. **Importar dados adicionais** (clientes, produtos, etc)
3. **Personalizar branding** (logo, cores)
4. **Configurar SMTP** para envio de emails
5. **Treinar equipe** no uso do sistema
6. **Agendar manutenções** mensais
7. **Monitorar performance** e otimizar conforme necessário

---

**🚀 Parabéns! Seu Odoo 19 está em produção no Contabo!**

*Para suporte adicional, consulte a documentação oficial do Odoo 19 em https://www.odoo.com/documentation/19.0*
