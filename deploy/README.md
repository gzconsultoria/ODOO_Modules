# 🚀 Deploy Odoo 19 para Produção (Contabo)

Documentação completa de deploy para ambiente de produção.

## 📁 Estrutura de Arquivos

```
deploy/
├── GUIA_DEPLOY_CONTABO.md       # ⭐ GUIA COMPLETO PASSO A PASSO
├── config/
│   ├── docker-compose.production.yml  # Docker Compose para produção
│   ├── odoo.conf                      # Configuração Odoo otimizada
│   ├── nginx.conf                     # Reverse proxy + SSL
│   ├── backup.sh                      # Script de backup automático
│   ├── deploy_to_contabo.sh           # Script de deploy automatizado
│   └── .env.production.template       # Template de variáveis (EDITAR!)
└── backups/
    ├── gzcon_20251206_134009.dump     # Backup do banco (5.4MB)
    └── modules_installed.txt          # Lista de módulos ativos
```

## ⚡ Quick Start

### 1️⃣ **Preparação Local** (já feito!)

```bash
✅ Backup do banco criado: gzcon_20251206_134009.dump (5.4MB)
✅ Módulos instalados: gz_finance_core, gz_finance_crm
✅ Configurações de produção prontas
```

### 2️⃣ **Configurar Variáveis de Ambiente**

```bash
# Copiar template
cp config/.env.production.template config/.env.production

# EDITAR COM SUAS SENHAS (nunca commitar!)
nano config/.env.production
```

### 3️⃣ **Provisionar VPS no Contabo**

- Acessar: https://my.contabo.com
- Criar VPS: Ubuntu 24.04, 8GB RAM, 4 vCPU
- Anotar IP: `123.456.789.10`
- Configurar DNS: `odoo.gzconsultoria.com.br` → IP do VPS

### 4️⃣ **Executar Deploy Automatizado**

```bash
# Copiar script para servidor
scp config/deploy_to_contabo.sh root@IP_DO_SERVIDOR:/root/

# Conectar via SSH
ssh root@IP_DO_SERVIDOR

# EDITAR DOMÍNIO NO SCRIPT
nano /root/deploy_to_contabo.sh
# Mudar: DOMAIN="seu-dominio.com.br"

# Executar
bash /root/deploy_to_contabo.sh
```

### 5️⃣ **Transferir Dados**

**No seu PC local:**

```bash
# .env (com senhas editadas)
scp config/.env.production root@IP:/opt/odoo/.env

# Módulos customizados
scp -r ../gz_finance_* root@IP:/opt/odoo/addons/

# Backup do banco
scp backups/gzcon_*.dump root@IP:/opt/odoo/backups/database/

# Configurações
scp config/docker-compose.production.yml root@IP:/opt/odoo/docker-compose.yml
scp config/odoo.conf root@IP:/opt/odoo/
scp config/nginx.conf root@IP:/opt/odoo/
scp config/backup.sh root@IP:/opt/odoo/scripts/
```

### 6️⃣ **Iniciar Odoo**

**No servidor:**

```bash
cd /opt/odoo
docker-compose up -d
```

### 7️⃣ **Acessar Sistema**

Abrir navegador:

```
https://seu-dominio.com.br
```

---

## 📚 Documentação Completa

**👉 Leia o guia completo:** [`GUIA_DEPLOY_CONTABO.md`](GUIA_DEPLOY_CONTABO.md)

Inclui:
- ✅ Pré-requisitos detalhados
- ✅ Configuração de segurança (Firewall, SSL, 2FA)
- ✅ Backups automáticos
- ✅ Monitoramento e logs
- ✅ Troubleshooting
- ✅ Manutenção

---

## 🔐 Segurança

### ⚠️ Arquivos que NUNCA devem ser commitados:

- ❌ `.env.production` (senhas reais)
- ❌ `backups/*.dump` (dados do banco)
- ❌ `ssl/*.pem` (certificados privados)

### ✅ Arquivos seguros para commitar:

- ✅ `.env.production.template` (sem senhas)
- ✅ `*.sh` (scripts)
- ✅ `*.yml` (docker-compose)
- ✅ `*.md` (documentação)

---

## 🆘 Suporte Rápido

### Ver logs do Odoo

```bash
ssh root@IP
cd /opt/odoo
docker-compose logs -f web
```

### Reiniciar serviços

```bash
docker-compose restart web
```

### Backup manual

```bash
bash /opt/odoo/scripts/backup.sh
```

### Atualizar módulo

```bash
docker-compose exec web odoo -c /etc/odoo/odoo.conf \
    -d gzcon -u gz_finance_docs --stop-after-init
docker-compose restart web
```

---

## 📊 Status Atual

- ✅ Backup do banco criado (5.4MB)
- ✅ Módulos empacotados (gz_finance_core, gz_finance_crm, gz_finance_docs)
- ✅ Docker Compose configurado
- ✅ Nginx + SSL configurado
- ✅ Script de backup automático criado
- ✅ Script de deploy automatizado
- ⏳ Aguardando provisionamento do VPS Contabo

---

**Próximos passos:** Seguir o guia completo em `GUIA_DEPLOY_CONTABO.md`
