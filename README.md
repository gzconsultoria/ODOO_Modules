# 📊 ODOO Modules - Consultoria de Investimentos

![Odoo](https://img.shields.io/badge/Odoo-19.0-714B67?style=for-the-badge&logo=odoo)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=for-the-badge)

> **Desenvolvido por:** [Geovane Zomer](https://github.com/gzconsultoria)  
> **Empresa:** GZ Consultoria  
> **Especialização:** Módulos Odoo para Wealth Management e Consultoria Financeira

---

## 🎯 Sobre Este Repositório

Este repositório contém uma coleção de **módulos customizados para Odoo 19** voltados especificamente para **consultorias de investimentos, wealth management e assessorias financeiras**.

Os módulos foram desenvolvidos para otimizar o processo comercial de empresas que trabalham com gestão de patrimônio, planejamento financeiro e consultoria de investimentos, desde a captação até o acompanhamento contínuo de clientes.

---

## 📦 Módulos Disponíveis

### 🏆 **CRM Wealth Management** (Principal)

Sistema completo de CRM especializado em Wealth Management com funil de vendas customizado e gestão inteligente de leads.

**Características principais:**

#### 🔄 **Funil Customizado (6 Estágios)**
- 🔵 **Captação** - Primeiro contato e qualificação inicial
- 🟢 **Qualificação** - Análise de perfil e objetivos
- 🟣 **Reunião Estratégica** - Diagnóstico profundo
- 🟠 **Proposta** - Apresentação de soluções
- 🟡 **Onboarding** - Documentação e estruturação
- 🟤 **Execução & Acompanhamento** - Gestão ativa

#### ✨ **Funcionalidades Avançadas**
- ✅ **Abas Dinâmicas** - Aparecem conforme progressão do lead
- ✅ **Validações Inteligentes** - Bloqueio de avanço sem dados obrigatórios
- ✅ **Indicadores de Completude** - 0-100% por aba com alertas visuais
- ✅ **Cálculos Automáticos** - Aporte mensal necessário, receita estimada
- ✅ **Sistema de SLA** - Notificações automáticas de follow-up
- ✅ **Campos Pessoais** - Aniversários, família, hobbies (relacionamento)
- ✅ **Resumo Executivo** - Primeira aba com contexto completo do cliente
- ✅ **Score de Qualificação** - Temperatura do lead (hot/warm/cold)

#### 🎛️ **Configurações Flexíveis**
- Taxas de retorno ajustáveis (conservadora, moderada, agressiva)
- Prazos de SLA personalizáveis por estágio
- Cadastros auxiliares (interesses, estratégias, objeções, documentos)

#### 🤖 **Automações**
- Cron jobs diários para verificação de SLAs
- Criação automática de atividades e notificações
- Alertas de aniversário (cliente e cônjuge)
- Rastreamento de tempo por estágio

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Odoo 19.0
- Python 3.12+
- PostgreSQL 13+

### Passos

```bash
# Clone o repositório
git clone https://github.com/gzconsultoria/ODOO_Modules.git

# Copie o módulo para addons path do Odoo
cp -r ODOO_Modules/crm_wealth /path/to/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo

# Ative o modo desenvolvedor
# Apps → Atualizar Lista de Apps
# Procure por "CRM Wealth Management"
# Clique em "Instalar"
```

### Docker (Recomendado)

```bash
# Use o docker-compose incluído
cd ODOO_Modules
docker-compose up -d

# Acesse: http://localhost:8069
# Login: admin / admin
```

---

## 📖 Documentação

Cada módulo possui sua própria documentação detalhada:

- 📘 [CRM Wealth Management - README](./crm_wealth/README.md)
- 📗 [Guia de Boas Práticas Odoo 19](./crm_wealth/BOAS_PRATICAS_ODOO19.md)
- 📙 [Exemplos de Uso](./crm_wealth/EXEMPLOS_USO.md)
- 📕 [Changelog](./crm_wealth/CHANGELOG.md)

---

## 🎓 Para Quem é Este Projeto?

### ✅ Ideal para:
- 🏦 **Consultorias de Investimentos**
- 💼 **Wealth Management / Family Office**
- 📊 **Assessorias de Investimentos**
- 💰 **Gestoras de Patrimônio**
- 🎯 **Planejadores Financeiros Certificados (CFP)**
- 📈 **Agentes Autônomos de Investimento (AAI)**

### 💡 Casos de Uso:
- Gestão de pipeline de prospecção de clientes HNW (High Net Worth)
- Acompanhamento de onboarding de novos investidores
- Controle de SLA de atendimento e follow-up
- Cálculos de viabilidade e simulações financeiras
- Registro de perfil de risco e suitability
- Histórico de reuniões e estratégias recomendadas

---

## 🛠️ Stack Tecnológico

- **Framework:** Odoo 19.0
- **Backend:** Python 3.12
- **ORM:** Odoo ORM
- **Frontend:** Owl Framework (Odoo)
- **Database:** PostgreSQL 13+
- **Views:** XML (QWeb Templates)

---

## 📊 Roadmap

### ✅ Fase 1 - Concluída
- [x] Funil customizado com 6 estágios
- [x] Abas dinâmicas por estágio
- [x] Validações e completude
- [x] Cálculos financeiros automáticos

### ✅ Fase 2 - Concluída
- [x] Sistema de SLAs configurável
- [x] Campos pessoais e relacionamento
- [x] Aba Resumo executivo
- [x] Score e temperatura de leads

### 🚧 Fase 3 - Em Planejamento
- [ ] Dashboard gerencial com KPIs
- [ ] Relatórios de performance
- [ ] Templates de email
- [ ] Integração WhatsApp/Email
- [ ] Lead scoring avançado (ML)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você tem sugestões de melhorias:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Add: Nova funcionalidade X'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está licenciado sob **LGPL-3** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**Geovane Zomer**  
- 🌐 Website: [gzconsultoria.com.br](https://www.gzconsultoria.com.br)  
- 📧 Email: geovane.zomer@gmail.com  
- 💼 LinkedIn: [linkedin.com/in/geovanezomer](https://linkedin.com/in/geovanezomer)  
- 🐙 GitHub: [@gzconsultoria](https://github.com/gzconsultoria)

---

## 🙏 Agradecimentos

- Odoo SA pela plataforma incrível
- Comunidade Odoo Brasil
- Clientes que inspiraram estas funcionalidades

---

## ⭐ Apoie o Projeto

Se este projeto foi útil para você, considere:
- ⭐ Dar uma estrela no GitHub
- 🐛 Reportar bugs e sugerir melhorias
- 📢 Compartilhar com colegas do setor financeiro
- ☕ [Buy me a coffee](https://www.buymeacoffee.com/geovanezomer)

---

<p align="center">
  <strong>Feito com ❤️ para o mercado financeiro brasileiro</strong>
</p>

<p align="center">
  <sub>Transformando a gestão de clientes em consultorias de investimentos</sub>
</p>
