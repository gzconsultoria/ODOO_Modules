# CRM Wealth Management - Odoo 19

![Odoo Version](https://img.shields.io/badge/Odoo-19.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

Sistema de CRM personalizado para Consultoria e Gestão de Investimentos (Wealth Management) desenvolvido para Odoo 19.

## 🎯 Visão Geral

Este repositório contém um módulo completo para transformar o CRM padrão do Odoo em uma poderosa ferramenta de gestão de relacionamento para consultorias financeiras, gestoras de patrimônio e assessorias de investimento.

### ✨ Diferenciais

- **Abas Dinâmicas Progressivas:** As informações aparecem conforme o lead avança no funil
- **6 Estágios Especializados:** Captação → Qualificação → Reunião → Proposta → Onboarding → Execução
- **Campos Contextuais:** Cada etapa possui campos relevantes para aquele momento específico
- **Acompanhamento Contínuo:** Sistema de follow-up mensal integrado
- **Dados Pré-configurados:** Pronto para uso com estratégias, objeções e documentos padrão

## 📦 Estrutura do Projeto

```
crm_wealth_odoo/
├── crm_wealth/                    # Módulo principal
│   ├── models/                    # Modelos Python
│   │   ├── crm_lead.py           # Extensão do CRM Lead
│   │   └── acompanhamento_mensal.py
│   ├── views/                     # Views XML
│   │   └── crm_lead_views.xml
│   ├── data/                      # Dados iniciais
│   │   └── crm_stage_data.xml
│   ├── security/                  # Controle de acesso
│   │   └── ir.model.access.csv
│   ├── __manifest__.py            # Manifesto do módulo
│   ├── README.md                  # Documentação do módulo
│   └── BOAS_PRATICAS_ODOO19.md   # Guia de desenvolvimento
└── README.md                      # Este arquivo
```

## 🚀 Instalação Rápida

### Opção 1: Docker (Recomendado para Testes) 🐳

A maneira mais rápida de testar o módulo!

```bash
# 1. Clone o repositório
git clone https://github.com/gzconsultoria/crm_wealth_odoo.git
cd crm_wealth_odoo

# 2. Inicie o Odoo com Docker
./start-odoo.sh

# 3. Acesse http://localhost:8069
```

**Pronto!** O Odoo 19 está rodando com o módulo disponível para instalação.

👉 Veja [DOCKER.md](DOCKER.md) para instruções detalhadas

### Opção 2: Instalação Manual

#### Pré-requisitos

- Odoo 19.0 instalado
- Python 3.10+
- PostgreSQL 12+

#### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/gzconsultoria/crm_wealth_odoo.git
   cd crm_wealth_odoo
   ```

2. **Copie o módulo para o diretório de addons:**
   ```bash
   cp -r crm_wealth /caminho/para/odoo/addons/
   ```

3. **Atualize a lista de módulos no Odoo:**
   - Ative o modo desenvolvedor
   - Apps → Atualizar Lista de Aplicativos

4. **Instale o módulo:**
   - Apps → Buscar "CRM Wealth Management"
   - Clique em "Instalar"

## 📊 Funcionalidades Detalhadas

### 🔵 Estágio 1: Captação
- Origem do Lead (Instagram, Indicação, Site, WhatsApp, etc.)
- Momento Financeiro Atual
- Patrimônio Aproximado (faixas)
- Renda Mensal (faixas)
- Interesses Iniciais (multi-seleção)

### 🟢 Estágio 2: Qualificação
- Perfil do Investidor (Suitability Preliminar)
- Dor Principal (Tempo, Estratégia, Medo, etc.)
- Objetivo de Curto Prazo (12 meses)
- Objetivo de Longo Prazo (5+ anos)

### 🟣 Estágio 3: Reunião Estratégica
- Diagnóstico Completo (Situação Atual, Pontos Fortes, Pontos a Melhorar, Oportunidades)
- Estratégias Recomendadas (Renda Fixa, FIIs, ETFs, etc.)
- Score de Potencial (0 a 5 estrelas)

### 🟠 Estágio 4: Proposta
- Plano Sugerido (Consultoria Mensal, FIRE, Premium, Gestão Completa, Mentoria)
- Valor da Proposta
- Justificativa de Valor
- Objeções Apresentadas e Tratativas

### 🟡 Estágio 5: Onboarding
- Suitability Oficial
- Documentos Entregues (RG, CPF, Comprovantes, Extratos)
- Perfil de Risco Final
- Estrutura Inicial Montada
- Contas de Corretoras

### 🟤 Estágio 6: Execução & Acompanhamento
- Valor Investido Atual
- Distribuição de Portfólio
- Acompanhamento Mensal (histórico de reuniões)
- Histórico de Mudanças

## 🎨 Interface

A interface se adapta automaticamente ao estágio do funil:

- **Captação (seq 10):** Exibe apenas aba Captação
- **Qualificação (seq 20):** Exibe Captação + Qualificação
- **Reunião (seq 30):** Exibe até Reunião Estratégica
- E assim sucessivamente...

Isso garante que o usuário veja apenas as informações relevantes para o momento atual do lead.

## 🛠️ Tecnologias e Boas Práticas

- **Odoo Framework 19.0**
- **Python 3.10+**
- **PostgreSQL**
- **XML Views com XPath Inheritance**
- **ORM Odoo (models.Model)**
- **Campos Computados com @api.depends**
- **Many2many, One2many, Many2one relationships**
- **Security Rules (ir.model.access)**
- **Data Files com noupdate**

Veja o arquivo [BOAS_PRATICAS_ODOO19.md](crm_wealth/BOAS_PRATICAS_ODOO19.md) para detalhes completos.

## 📖 Documentação

- 🚀 [Quick Start](QUICKSTART.md) - Comece em 5 minutos
- 🐳 [Docker Setup](DOCKER.md) - Ambiente completo com Docker
- 📘 [README do Módulo](crm_wealth/README.md) - Instruções detalhadas
- 💡 [Exemplos de Uso](EXEMPLOS_USO.md) - Casos práticos e exemplos
- 🛠️ [Boas Práticas Odoo 19](crm_wealth/BOAS_PRATICAS_ODOO19.md) - Guia de desenvolvimento
- 🐛 [Troubleshooting](TROUBLESHOOTING.md) - Solução de problemas
- 🤝 [Contributing](CONTRIBUTING.md) - Como contribuir
- 📝 [Changelog](CHANGELOG.md) - Histórico de versões
- 📚 [Documentação Oficial Odoo](https://www.odoo.com/documentation/19.0/)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Roadmap

- [ ] Dashboard com métricas de conversão por estágio
- [ ] Integração com APIs de corretoras
- [ ] Relatórios de performance de carteira
- [ ] Automação de e-mails por estágio
- [ ] Assinatura digital de documentos
- [ ] Portal do cliente para acompanhamento

## 📄 Licença

Este projeto está licenciado sob LGPL-3 - veja o arquivo LICENSE para detalhes.

## 👥 Autor

**GZ Consultoria e Administração de Carteiras**
- Website: [https://www.gzconsultoria.com.br](https://www.gzconsultoria.com.br)
- Email: contato@geovanezomer.com.br

## 🆘 Suporte

Para questões, bugs ou sugestões:
- Abra uma [Issue](https://github.com/gzconsultoria/crm_wealth_odoo/issues)
- Entre em contato através do website

## 🙏 Agradecimentos

- Comunidade Odoo pela excelente plataforma
- Todos os contribuidores do projeto

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!