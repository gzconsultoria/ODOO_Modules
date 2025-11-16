# CRM Wealth Management - Odoo 19

Módulo personalizado para Consultoria e Gestão de Investimentos (Wealth Management) no Odoo 19.

## 📋 Descrição

Este módulo estende o CRM padrão do Odoo para atender às necessidades específicas de consultorias financeiras, gestoras de patrimônio e assessorias de investimento.

### ✨ Principais Funcionalidades

- **6 Estágios Customizados do Funil:**
  1. 🔵 Captação
  2. 🟢 Qualificação
  3. 🟣 Reunião Estratégica
  4. 🟠 Proposta
  5. 🟡 Onboarding
  6. 🟤 Execução & Acompanhamento

- **Abas Dinâmicas:** As abas aparecem progressivamente conforme o lead avança no funil
- **Campos Específicos:** Cada etapa possui campos relevantes para aquele momento
- **Acompanhamento Mensal:** Registro de reuniões e evolução do portfólio
- **Dados Pré-configurados:** Interesses, estratégias, objeções, documentos e corretoras

## 🎯 Visibilidade Progressiva das Abas

O sistema controla automaticamente quais abas são exibidas baseado no estágio atual do lead:

- **Estágio Captação (seq 10):** Mostra apenas aba Captação
- **Estágio Qualificação (seq 20):** Mostra Captação + Qualificação
- **Estágio Reunião (seq 30):** Mostra Captação + Qualificação + Reunião
- **Estágio Proposta (seq 40):** Mostra até Proposta
- **Estágio Onboarding (seq 50):** Mostra até Onboarding
- **Estágio Execução (seq 60):** Mostra todas as abas

## 📦 Instalação

### Requisitos

- Odoo 19.0
- Módulo `crm` (padrão do Odoo)
- Módulo `sale_crm` (padrão do Odoo)

### Passos

1. Copie o diretório `crm_wealth` para o diretório de addons do Odoo:
   ```bash
   cp -r crm_wealth /caminho/para/odoo/addons/
   ```

2. Atualize a lista de módulos no Odoo:
   - Modo desenvolvedor ativado
   - Apps → Atualizar Lista de Aplicativos

3. Instale o módulo:
   - Apps → Buscar "CRM Wealth Management"
   - Clique em "Instalar"

## 🚀 Configuração Inicial

Após a instalação, o módulo cria automaticamente:

- 6 estágios do funil de Wealth Management
- Dados exemplo de:
  - Interesses (Bolsa, FIIs, Previdência, etc.)
  - Estratégias (Renda Fixa, Tesouro, ETFs, etc.)
  - Objeções comuns e tratativas
  - Documentos necessários
  - Corretoras principais

### Configurar Dados Adicionais

Acesse: **CRM → Configuração → Wealth Management**

Onde você pode gerenciar:
- Interesses
- Estratégias
- Objeções
- Documentos
- Corretoras

## 📊 Estrutura de Dados

### Aba 1: Captação
- Origem do Lead
- Momento Financeiro Atual
- Patrimônio Aproximado
- Renda Mensal
- Interesses Iniciais

### Aba 2: Qualificação
- Perfil do Investidor (Suitability Preliminar)
- Dor Principal
- Objetivo de Curto Prazo
- Objetivo de Longo Prazo

### Aba 3: Reunião Estratégica
- Diagnóstico (Situação Atual, Pontos Fortes, Pontos a Melhorar, Oportunidades)
- Estratégias Recomendadas
- Score de Potencial (0-5 estrelas)

### Aba 4: Proposta
- Plano Sugerido
- Valor da Proposta
- Justificativa de Valor
- Objeções Apresentadas

### Aba 5: Onboarding
- Suitability Oficial Preenchido
- Documentos Entregues
- Perfil de Risco Final
- Estrutura Inicial Montada
- Contas de Corretoras

### Aba 6: Execução & Acompanhamento
- Valor Investido Atual
- Distribuição de Portfólio
- Acompanhamento Mensal (One2many)
- Histórico de Mudanças

## 🛠️ Boas Práticas Implementadas (Odoo 19)

1. **Herança de Modelos:** Uso de `_inherit` para estender o CRM sem modificar o core
2. **Campos Computados:** Lógica de visibilidade usando `@api.depends`
3. **Relacionamentos Many2many:** Para seleções múltiplas (interesses, estratégias, etc.)
4. **One2many:** Para acompanhamento mensal recorrente
5. **Tracking:** Campos importantes com `tracking=True` para auditoria
6. **Security:** Permissões diferenciadas para usuários e managers
7. **Data Files:** Dados iniciais com `noupdate="1"`
8. **Views Inheritance:** Herança de views usando XPath
9. **Campos Monetários:** Uso correto de `Monetary` com `currency_field`
10. **Organização:** Código bem comentado e organizado por seções

## 🎨 Personalização

### Adicionar Novo Campo

1. Edite `models/crm_lead.py` e adicione o campo
2. Edite `views/crm_lead_views.xml` e adicione na view
3. Atualize o módulo

### Adicionar Nova Opção em Selection

Basta editar o arquivo de dados XML correspondente em `data/crm_stage_data.xml`

## 📝 Licença

LGPL-3

## 👥 Autor

**GZ Consultoria e Administração de Carteiras**
- Website: https://www.gzconsultoria.com.br

## 🆘 Suporte

Para questões e suporte, entre em contato através do website.

## 📚 Documentação Odoo 19

- [Documentação Oficial Odoo](https://www.odoo.com/documentation/19.0/)
- [ORM API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Views](https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html)
