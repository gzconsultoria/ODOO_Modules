# 🚀 Quick Start - CRM Wealth Management

Comece a usar o CRM Wealth Management em 5 minutos!

## ⚡ Instalação Rápida

### Opção 1: Script Automático (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/gzconsultoria/crm_wealth_odoo.git
cd crm_wealth_odoo

# 2. Execute o instalador
./install.sh

# 3. Siga as instruções na tela
```

### Opção 2: Manual

```bash
# 1. Copie o módulo
sudo cp -r crm_wealth /opt/odoo/addons/

# 2. Ajuste permissões
sudo chown -R odoo:odoo /opt/odoo/addons/crm_wealth

# 3. Reinicie o Odoo
sudo systemctl restart odoo
```

## 📱 Configuração Inicial (2 minutos)

### 1. Ative o Modo Desenvolvedor

```
Settings → Developer Tools → Activate Developer Mode
```

### 2. Atualize Lista de Apps

```
Apps → Atualizar Lista de Aplicativos (ícone ⟳)
```

### 3. Instale o Módulo

```
Apps → Remover filtro "Apps" → Buscar "Wealth" → Install
```

✅ **Pronto!** O módulo está instalado.

## 🎯 Primeiro Lead (3 minutos)

### Passo 1: Criar Lead

```
CRM → Leads → Criar

Preencha:
- Nome: João Silva
- Email: joao@email.com
- Telefone: +55 11 98765-4321
```

### Passo 2: Preencher Aba Captação

```
Estágio: 🔵 Captação (já selecionado por padrão)

Aba Captação:
- Origem: Instagram
- Momento Financeiro: Iniciando investimentos
- Patrimônio: R$ 50.000 - R$ 200.000
- Renda: R$ 10.000 - R$ 20.000
- Interesses: Bolsa, FIIs, Planejamento

Salvar
```

### Passo 3: Avançar para Qualificação

```
Arrastar o card para → 🟢 Qualificação
(ou mudar Estágio no formulário)

Nova aba "Qualificação" aparece! ✨

Preencher:
- Perfil: Moderado
- Dor Principal: Estratégia
- Objetivo CP: Começar a investir estruturado
- Objetivo LP: Independência financeira em 15 anos

Salvar
```

### Passo 4: Explorar as Abas

Continue movendo entre estágios e veja as abas aparecerem progressivamente:

- 🟣 Reunião Estratégica (estágio 3)
- 🟠 Proposta (estágio 4)
- 🟡 Onboarding (estágio 5)
- 🟤 Execução (estágio 6)

## ⚙️ Personalizar (5 minutos)

### Adicionar Seus Próprios Dados

#### Interesses

```
CRM → Configuração → Wealth Management → Interesses → Criar

Exemplos:
- Stocks Internacionais
- Day Trade
- Swing Trade
```

#### Estratégias

```
CRM → Configuração → Wealth Management → Estratégias → Criar

Exemplos:
- Small Caps
- Dividendos (Dividend Yield)
- Growth Investing
```

#### Corretoras

```
CRM → Configuração → Wealth Management → Corretoras → Criar

Exemplos:
- Sua corretora preferida
- Bancos digitais
```

## 📊 Visualizar Funil

### View Kanban (Padrão)

```
CRM → Pipeline

Veja cards organizados por estágio:
┌─────────────┬──────────────┬──────────────┬─────────┐
│  Captação   │ Qualificação │   Reunião    │ Proposta│
│             │              │              │         │
│ ┌─────────┐ │ ┌─────────┐  │ ┌─────────┐  │         │
│ │ João S. │ │ │ Maria A.│  │ │ Pedro O.│  │         │
│ └─────────┘ │ └─────────┘  │ └─────────┘  │         │
└─────────────┴──────────────┴──────────────┴─────────┘
```

### View Lista

```
CRM → Leads/Opportunities → Trocar para List View

Veja tabela com todos os leads
```

### View Gráfico

```
CRM → Reporting

Gráficos e análises do funil
```

## 🎨 Dicas para Primeiros Dias

### 1. Crie Leads de Teste

Crie 5-10 leads em diferentes estágios para ver o sistema funcionando.

### 2. Configure Atividades

```
Em cada lead:
→ Agendar Atividade
→ Tipo: Reunião / Ligação / Email
→ Data e Responsável
```

### 3. Use Filtros

```
Filtros úteis:
- Meus Leads
- Leads Hot (score 4-5)
- Por Origem
- Por Estágio
```

### 4. Personalize o Pipeline

```
Settings → CRM → Stages

Pode reordenar, renomear ou adicionar estágios
(mas mantenha as sequências 10, 20, 30... para o módulo funcionar)
```

## 📱 Atalhos Úteis

| Ação | Atalho |
|------|--------|
| Criar Lead | CRM → + |
| Buscar | Alt + Q |
| Salvar | Ctrl + S |
| Descartar | Esc |
| Modo Dev | Alt + D |

## 🆘 Problemas Comuns

### Módulo não aparece

```
1. Verificar se está em /addons/crm_wealth
2. Apps → Update Apps List
3. Reiniciar Odoo
```

### Abas não aparecem

```
1. Verificar Estágio → deve ter sequence correta (10,20,30...)
2. Salvar o lead novamente
3. Atualizar página (F5)
```

### Dados vazios

```
CRM → Configuração → Wealth Management
Criar interesses, estratégias, etc.
```

## 📚 Próximos Passos

1. ✅ **Ler Documentação Completa:** [README.md](README.md)
2. 📖 **Ver Exemplos Detalhados:** [EXEMPLOS_USO.md](EXEMPLOS_USO.md)
3. 🛠️ **Aprender Boas Práticas:** [crm_wealth/BOAS_PRATICAS_ODOO19.md](crm_wealth/BOAS_PRATICAS_ODOO19.md)
4. 🐛 **Resolver Problemas:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 💡 Recursos

- [Documentação Odoo](https://www.odoo.com/documentation/19.0/)
- [Community](https://www.odoo.com/forum)
- [GitHub Issues](https://github.com/gzconsultoria/crm_wealth_odoo/issues)

## 🎉 Tudo Pronto!

Você está pronto para usar o CRM Wealth Management!

**Próximo:** Comece a importar seus leads reais e personalize conforme sua necessidade.

---

Tem dúvidas? Abra uma [Issue](https://github.com/gzconsultoria/crm_wealth_odoo/issues) ou [Discussion](https://github.com/gzconsultoria/crm_wealth_odoo/discussions)!
