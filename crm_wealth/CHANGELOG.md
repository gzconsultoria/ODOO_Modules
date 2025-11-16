# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-11-16

### Adicionado
- ✨ Sistema completo de CRM para Wealth Management
- 📊 6 estágios customizados do funil:
  - 🔵 Captação
  - 🟢 Qualificação
  - 🟣 Reunião Estratégica
  - 🟠 Proposta
  - 🟡 Onboarding
  - 🟤 Execução & Acompanhamento
- 🎯 Abas dinâmicas com visibilidade progressiva baseada no estágio
- 💼 Campos específicos para cada etapa do funil
- 📝 Sistema de acompanhamento mensal integrado
- 🏦 Gestão de corretoras e contas
- 📄 Controle de documentos do cliente
- 💡 Gerenciamento de estratégias de investimento
- 🎭 Sistema de objeções e tratativas
- 🎨 Tags de interesses do cliente
- 🔒 Controle de acesso (user/manager)
- 📚 Documentação completa:
  - README principal
  - README do módulo
  - Guia de boas práticas Odoo 19
  - Troubleshooting
- 🚀 Script de instalação automatizado
- 📦 Dados iniciais pré-configurados:
  - 10 tipos de interesses
  - 8 estratégias de investimento
  - 6 objeções comuns
  - 6 documentos padrão
  - 8 corretoras populares

### Características Técnicas
- Herança do modelo `crm.lead`
- Campos computados com `@api.depends`
- Relacionamentos Many2many e One2many
- Views XML com XPath inheritance
- Security rules com ir.model.access.csv
- Data files com noupdate para preservar customizações
- Tracking em campos importantes
- Campos monetários com currency_field
- Widgets especializados (many2many_tags, radio, etc.)

### Compatibilidade
- Odoo 19.0
- Python 3.10+
- PostgreSQL 12+

## [Unreleased]

### Planejado para v1.1.0
- [ ] Dashboard com métricas de conversão
- [ ] Integração com APIs de corretoras
- [ ] Relatórios de performance
- [ ] Automação de e-mails por estágio
- [ ] Portal do cliente
- [ ] Assinatura digital de documentos

### Planejado para v1.2.0
- [ ] Mobile app (Odoo Mobile)
- [ ] Chatbot para qualificação inicial
- [ ] IA para recomendação de estratégias
- [ ] Integração com WhatsApp Business

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correção de bugs
- `Segurança` para vulnerabilidades

## Versionamento

Formato: MAJOR.MINOR.PATCH

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis
