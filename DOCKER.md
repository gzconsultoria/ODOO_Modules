# Ambiente Docker - Odoo 19

Este diretório contém a configuração Docker para executar o Odoo 19 com o módulo CRM Wealth Management.

## 🚀 Quick Start

### 1. Iniciar Odoo

```bash
./start-odoo.sh
```

Ou manualmente:

```bash
docker compose up -d
```

### 2. Acessar

- **URL:** http://localhost:8069
- **Senha Master:** admin

### 3. Criar Banco de Dados

1. Acesse http://localhost:8069
2. Clique em "Create Database"
3. Preencha:
   - Database Name: `crm_wealth_db`
   - Email: `admin@example.com`
   - Password: `admin` (ou sua preferência)
   - Language: Portuguese (BR) / pt_BR
   - Country: Brazil
   - Demo Data: ☐ (desmarque para banco limpo)

### 4. Instalar Módulo

1. Ative o modo desenvolvedor: Settings → Developer Tools → Activate Developer Mode
2. Apps → Update Apps List
3. Remover filtro "Apps"
4. Buscar "Wealth"
5. Instalar "CRM Wealth Management"

## 📁 Estrutura

```
.
├── docker-compose.yml      # Configuração dos containers
├── config/
│   └── odoo.conf          # Configuração do Odoo
├── crm_wealth/            # Módulo (montado automaticamente)
├── start-odoo.sh          # Script para iniciar
└── stop-odoo.sh           # Script para parar
```

## 🐳 Containers

### odoo_app
- **Imagem:** odoo:19.0
- **Porta:** 8069 (HTTP), 8072 (Longpolling)
- **Volume:** `./crm_wealth` → `/mnt/extra-addons/crm_wealth`

### odoo_postgres
- **Imagem:** postgres:15
- **Porta:** 5432 (interna)
- **Dados:** Volume persistente `odoo_db_data`

## 🛠️ Comandos Úteis

### Logs

```bash
# Todos os logs
docker compose logs -f

# Apenas Odoo
docker compose logs -f odoo

# Apenas PostgreSQL
docker compose logs -f db
```

### Gerenciamento

```bash
# Parar
docker compose stop

# Iniciar
docker compose start

# Reiniciar apenas Odoo
docker compose restart odoo

# Parar e remover containers
docker compose down

# Parar e remover tudo (incluindo dados!)
docker compose down -v
```

### Desenvolvimento

```bash
# Acessar shell do container Odoo
docker exec -it odoo_app bash

# Dentro do container, você pode:
# - Ver logs: tail -f /var/log/odoo/odoo-server.log
# - Listar addons: ls /mnt/extra-addons
# - Executar odoo shell: odoo shell -d crm_wealth_db

# Reiniciar após mudanças no código
docker compose restart odoo
# Depois: Apps → CRM Wealth Management → Upgrade
```

### PostgreSQL

```bash
# Conectar ao PostgreSQL
docker exec -it odoo_postgres psql -U odoo

# Comandos úteis dentro do psql:
\l                          # Listar databases
\c crm_wealth_db           # Conectar ao banco
\dt                        # Listar tabelas
\d crm_lead                # Descrever tabela
```

## 🔧 Troubleshooting

### Porta 8069 já em uso

```bash
# Descobrir processo
lsof -i :8069

# Parar container antigo
docker stop odoo_app

# Ou matar processo
kill -9 $(lsof -t -i:8069)
```

### Módulo não aparece

1. Verificar se está montado:
   ```bash
   docker exec -it odoo_app ls -la /mnt/extra-addons/crm_wealth
   ```

2. Reiniciar Odoo:
   ```bash
   docker compose restart odoo
   ```

3. Update Apps List no Odoo

### Erro de permissão

```bash
# Ajustar permissões do módulo
chmod -R 755 crm_wealth
```

### Limpar tudo e recomeçar

```bash
# ATENÇÃO: Isso remove TODOS os dados!
docker compose down -v
docker volume prune -f
docker compose up -d
```

## 🔐 Segurança

**⚠️ IMPORTANTE:** Esta configuração é para **desenvolvimento apenas**!

Para produção:
- Mude as senhas padrão
- Use variáveis de ambiente
- Configure proxy reverso (nginx)
- Habilite SSL/HTTPS
- Ajuste workers e limites de memória

## 📝 Configuração Customizada

Edite `config/odoo.conf` para personalizar:

```ini
# Exemplo: aumentar workers para produção
workers = 4

# Exemplo: mudar porta
http_port = 8080

# Exemplo: configurar email
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_user = seu@email.com
smtp_password = suasenha
```

Após mudar configuração:

```bash
docker compose restart odoo
```

## 🎯 Desenvolvimento do Módulo

### Editar código

1. Edite arquivos em `crm_wealth/`
2. Reinicie Odoo: `docker compose restart odoo`
3. Atualize módulo no Odoo: Apps → CRM Wealth → Upgrade

### Adicionar dependências Python

Crie `Dockerfile` customizado:

```dockerfile
FROM odoo:19.0

USER root
RUN pip3 install sua-dependencia
USER odoo
```

Modifique `docker-compose.yml`:

```yaml
odoo:
  build: .
  # image: odoo:19.0  # Comente esta linha
```

Reconstrua:

```bash
docker compose up -d --build
```

## 📊 Monitoramento

### Verificar saúde dos containers

```bash
docker compose ps
```

### Recursos utilizados

```bash
docker stats odoo_app odoo_postgres
```

### Espaço em disco

```bash
docker system df
```

## 🔄 Backup e Restore

### Backup

```bash
# Backup do banco
docker exec odoo_postgres pg_dump -U odoo crm_wealth_db > backup.sql

# Backup dos filestore
docker cp odoo_app:/var/lib/odoo/filestore ./backup_filestore/
```

### Restore

```bash
# Restore do banco
docker exec -i odoo_postgres psql -U odoo crm_wealth_db < backup.sql

# Restore dos filestore
docker cp ./backup_filestore/ odoo_app:/var/lib/odoo/filestore/
```

## 🌐 Acessar de Outra Máquina

Se quiser acessar de outro computador na rede:

1. Descubra seu IP:
   ```bash
   ip addr show | grep "inet "
   # ou
   hostname -I
   ```

2. Acesse: http://SEU_IP:8069

3. Se necessário, configure firewall:
   ```bash
   sudo ufw allow 8069/tcp
   ```

## 📚 Recursos

- [Odoo Docker Hub](https://hub.docker.com/_/odoo)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
