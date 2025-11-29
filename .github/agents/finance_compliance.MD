# 🛡️ Finance Compliance & Suitability - Arquitetura Completa

## 📘 Visão Geral

O módulo **Finance Compliance & Suitability** é o segundo módulo da suíte de investimentos, responsável por garantir conformidade regulatória com CVM (Comissão de Valores Mobiliários) e ANBIMA (Associação Brasileira das Entidades dos Mercados Financeiro e de Capitais).

### Por que este módulo é prioritário?

✅ **Mandatório Regulatório**: Instrução CVM 539/2013 e Código ANBIMA exigem suitability antes de qualquer recomendação de investimento  
✅ **Bloqueia Operações**: Sistema não permite aplicações sem suitability válido  
✅ **Independente**: Funciona standalone, não depende do módulo de investimentos  
✅ **Complementa o Core**: Expande o KYC básico com análise de perfil detalhada  
✅ **Alta Prioridade de Compliance**: Evita multas e problemas legais (multas podem chegar a R$ 500 mil por infração)

---

## 📊 Regulamentação Base

### Instrução CVM 539/2013
- **Art. 2º**: Obrigação de verificar adequação dos produtos ao perfil do cliente
- **Art. 3º**: Coleta de informações sobre:
  - Objetivos de investimento
  - Situação financeira
  - Conhecimento em investimentos
  - Experiência no mercado
- **Art. 4º**: Validade de 24 meses (renovação obrigatória)
- **Art. 5º**: Classificação de produtos por risco

### Código ANBIMA de Regulação e Melhores Práticas
- **Capítulo IV**: Suitability obrigatório antes da primeira aplicação
- **Atualização**: A cada 24 meses ou mudança relevante na situação do cliente
- **Disclosure**: Cliente deve declarar ciência dos riscos
- **Documentação**: Manter histórico completo por 5 anos

---

## 🏗️ Estrutura do Módulo

```
finance_compliance/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── res_partner.py                      # Extend partner com compliance
│   ├── compliance_suitability.py           # Registro principal de suitability
│   ├── compliance_questionnaire.py         # Template de questionário
│   ├── compliance_question.py              # Perguntas do questionário
│   ├── compliance_answer.py                # Respostas do cliente
│   ├── compliance_risk_profile.py          # Definição de perfis de risco
│   ├── compliance_product_classification.py # Classificação de produtos
│   ├── compliance_approval.py              # Aprovações de compliance
│   ├── compliance_declaration.py           # Declarações assinadas
│   └── documents_folder.py                 # Integração com documents
├── security/
│   ├── compliance_security.xml
│   └── ir.model.access.csv
├── views/
│   ├── res_partner_views.xml               # Aba Suitability no cliente
│   ├── compliance_suitability_views.xml
│   ├── compliance_questionnaire_views.xml
│   ├── compliance_approval_views.xml
│   ├── compliance_dashboard.xml            # Dashboard de compliance
│   └── compliance_menu.xml
├── data/
│   ├── compliance_data.xml                 # Dados iniciais
│   ├── compliance_questionnaire_anbima.xml # Questionário ANBIMA padrão
│   ├── compliance_risk_profiles.xml        # Perfis de risco
│   ├── compliance_cron.xml                 # Tarefas agendadas
│   └── documents_workspace.xml             # Workspace padrão
├── wizard/
│   ├── __init__.py
│   ├── compliance_questionnaire_wizard.py  # Aplicar suitability
│   ├── compliance_approval_wizard.py       # Aprovar/rejeitar
│   └── compliance_renew_wizard.py          # Renovação em massa
├── reports/
│   ├── __init__.py
│   ├── compliance_suitability_report.xml   # Relatório de adequação
│   └── compliance_declaration_report.xml   # Termo de ciência
└── static/
    ├── description/
    │   ├── icon.png
    │   └── index.html
    └── src/
        ├── css/
        │   └── compliance.css
        └── js/
            └── compliance_questionnaire.js
```

---

## 🎯 Funcionalidades Principais

### 1. Questionário de Suitability Dinâmico

**Categorias de Perguntas (ANBIMA):**

#### A. Situação Financeira (Peso: 25%)
- Renda mensal
- Patrimônio líquido
- Percentual do patrimônio a investir
- Necessidade de liquidez
- Fonte de recursos
- Capacidade de suportar perdas

#### B. Objetivos de Investimento (Peso: 25%)
- Prazo de investimento
- Objetivo principal (preservação, crescimento, especulação)
- Tolerância a volatilidade
- Necessidade de renda regular
- Momento de vida (acumulação, preservação, usufruto)

#### C. Conhecimento e Experiência (Peso: 30%)
- Escolaridade
- Formação em área financeira
- Experiência profissional no mercado
- Conhecimento de produtos (renda fixa, ações, derivativos, etc.)
- Tempo de experiência em investimentos
- Frequência de operações

#### D. Perfil Psicológico (Peso: 20%)
- Reação a perdas
- Preferência risco x retorno
- Horizonte temporal
- Disciplina em manter estratégia
- Conforto com volatilidade

### 2. Scoring e Classificação

**Sistema de Pontuação:**
```
0-33 pontos   → CONSERVADOR
34-66 pontos  → MODERADO
67-100 pontos → AGRESSIVO
```

**Subcategorias:**
- **Conservador Defensivo**: 0-16 pontos
- **Conservador Clássico**: 17-33 pontos
- **Moderado Equilibrado**: 34-50 pontos
- **Moderado Dinâmico**: 51-66 pontos
- **Agressivo Arrojado**: 67-83 pontos
- **Agressivo Sofisticado**: 84-100 pontos

### 3. Classificação de Produtos por Risco

**Escala de Risco (1-7):**

| Nível | Classificação | Produtos Típicos | Perfis Compatíveis |
|-------|---------------|------------------|-------------------|
| 1 | Risco Baixíssimo | Tesouro Selic, Fundos DI | Todos |
| 2 | Risco Baixo | CDB 100% CDI, LCI/LCA | Conservador+ |
| 3 | Risco Médio-Baixo | Títulos Públicos Prefixados, Fundos Renda Fixa | Conservador+ |
| 4 | Risco Médio | Debêntures, Fundos Multimercado | Moderado+ |
| 5 | Risco Médio-Alto | Ações Blue Chips, Fundos de Ações | Moderado+ |
| 6 | Risco Alto | Ações Small Caps, COE, Fundos Alavancados | Agressivo |
| 7 | Risco Altíssimo | Derivativos, Day Trade, Forex, Criptomoedas | Agressivo Sofisticado |

### 4. Motor de Adequação

**Regras de Compatibilidade:**

```python
COMPATIBILITY_MATRIX = {
    'conservador_defensivo': [1, 2],           # Só produtos nível 1-2
    'conservador_classico': [1, 2, 3],         # Até nível 3
    'moderado_equilibrado': [1, 2, 3, 4],      # Até nível 4
    'moderado_dinamico': [1, 2, 3, 4, 5],      # Até nível 5
    'agressivo_arrojado': [1, 2, 3, 4, 5, 6],  # Até nível 6
    'agressivo_sofisticado': [1, 2, 3, 4, 5, 6, 7],  # Todos
}
```

**Exceções (Override):**
- Compliance Manager pode aprovar investimentos fora do perfil
- Requer justificativa por escrito
- Cliente deve assinar termo de ciência específico
- Auditoria completa do processo

### 5. Integração com Documents (Nativo Odoo)

**Estrutura de Pastas Automática:**

```
Documents/
└── Clientes/
    └── [CPF/CNPJ] - [Nome do Cliente]/
        ├── 01. Cadastro/
        │   ├── RG ou CNH (frente e verso)
        │   ├── Comprovante de Residência
        │   ├── Comprovante de Renda
        │   └── Procuração (se aplicável)
        ├── 02. Compliance/
        │   ├── Questionário de Suitability
        │   ├── Termo de Ciência de Riscos
        │   ├── Declaração de PEP
        │   ├── Termo de Adequação
        │   └── Histórico de Suitability
        ├── 03. Contratos/
        │   ├── Termo de Adesão
        │   ├── Política de Investimentos
        │   ├── Contrato de Gestão
        │   └── Aditivos
        ├── 04. Operações/
        │   ├── Boletins de Aplicação
        │   ├── Notas de Negociação
        │   └── Comprovantes de TED/DOC
        └── 05. Relatórios/
            ├── Extratos Mensais
            ├── Relatórios de Performance
            └── IR - Informe de Rendimentos
```

**Automações:**
- ✅ Criação automática da estrutura ao marcar cliente como Finance Client
- ✅ Tags automáticas por tipo de documento
- ✅ OCR automático para extração de dados (CPF, endereço, etc.)
- ✅ Workflow de aprovação para documentos críticos
- ✅ Versionamento automático
- ✅ Alertas de documentos faltantes
- ✅ Expiração automática (ex: comprovante de residência > 3 meses)

---

## 💾 Models Detalhados

### 1. `res_partner.py` (Extend)

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # ================================
    # COMPLIANCE FIELDS
    # ================================
    
    # Suitability
    active_suitability_id = fields.Many2one(
        'compliance.suitability',
        string='Active Suitability',
        compute='_compute_active_suitability',
        store=True,
        help='Most recent valid suitability'
    )
    
    suitability_ids = fields.One2many(
        'compliance.suitability',
        'partner_id',
        string='Suitability History'
    )
    
    suitability_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ], compute='_compute_suitability_status', store=True)
    
    suitability_expiry_date = fields.Date(
        compute='_compute_suitability_expiry',
        store=True,
        string='Suitability Expiry'
    )
    
    days_to_suitability_expiry = fields.Integer(
        compute='_compute_days_to_expiry',
        string='Days to Expiry'
    )
    
    risk_profile = fields.Selection([
        ('conservador_defensivo', 'Conservador Defensivo'),
        ('conservador_classico', 'Conservador Clássico'),
        ('moderado_equilibrado', 'Moderado Equilibrado'),
        ('moderado_dinamico', 'Moderado Dinâmico'),
        ('agressivo_arrojado', 'Agressivo Arrojado'),
        ('agressivo_sofisticado', 'Agressivo Sofisticado'),
    ], compute='_compute_risk_profile', store=True)
    
    risk_score = fields.Integer(
        compute='_compute_risk_score',
        store=True,
        string='Risk Score (0-100)'
    )
    
    # Documents Integration
    document_folder_id = fields.Many2one(
        'documents.folder',
        string='Client Document Folder',
        readonly=True,
        help='Main folder for this client in Documents app'
    )
    
    document_count = fields.Integer(
        compute='_compute_document_count',
        string='Documents'
    )
    
    missing_documents = fields.Text(
        compute='_compute_missing_documents',
        string='Missing Documents'
    )
    
    # Compliance Approvals
    compliance_approval_ids = fields.One2many(
        'compliance.approval',
        'partner_id',
        string='Compliance Approvals'
    )
    
    pending_compliance_approvals = fields.Integer(
        compute='_compute_pending_approvals',
        string='Pending Approvals'
    )
    
    # Investment Restrictions
    can_invest = fields.Boolean(
        compute='_compute_can_invest',
        string='Can Invest',
        help='Has valid suitability and approved KYC'
    )
    
    investment_restrictions = fields.Text(
        compute='_compute_investment_restrictions',
        string='Investment Restrictions'
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('suitability_ids', 'suitability_ids.state', 'suitability_ids.expiry_date')
    def _compute_active_suitability(self):
        """Get most recent valid suitability"""
        for partner in self:
            active = self.env['compliance.suitability'].search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'approved'),
                ('expiry_date', '>=', fields.Date.today()),
            ], limit=1, order='application_date desc')
            partner.active_suitability_id = active
    
    @api.depends('active_suitability_id', 'active_suitability_id.state')
    def _compute_suitability_status(self):
        """Compute current suitability status"""
        for partner in self:
            if not partner.is_finance_client:
                partner.suitability_status = False
                continue
                
            if not partner.active_suitability_id:
                # Check if has any in progress
                in_progress = self.env['compliance.suitability'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'in', ['draft', 'submitted']),
                ], limit=1)
                
                if in_progress:
                    partner.suitability_status = 'in_progress'
                else:
                    partner.suitability_status = 'pending'
            else:
                suitability = partner.active_suitability_id
                if suitability.expiry_date < fields.Date.today():
                    partner.suitability_status = 'expired'
                else:
                    partner.suitability_status = 'valid'
    
    @api.depends('active_suitability_id', 'active_suitability_id.expiry_date')
    def _compute_suitability_expiry(self):
        """Get suitability expiry date"""
        for partner in self:
            if partner.active_suitability_id:
                partner.suitability_expiry_date = partner.active_suitability_id.expiry_date
            else:
                partner.suitability_expiry_date = False
    
    @api.depends('suitability_expiry_date')
    def _compute_days_to_expiry(self):
        """Calculate days until suitability expires"""
        today = fields.Date.today()
        for partner in self:
            if partner.suitability_expiry_date:
                delta = partner.suitability_expiry_date - today
                partner.days_to_suitability_expiry = delta.days
            else:
                partner.days_to_suitability_expiry = 0
    
    @api.depends('active_suitability_id', 'active_suitability_id.risk_profile')
    def _compute_risk_profile(self):
        """Get risk profile from active suitability"""
        for partner in self:
            if partner.active_suitability_id:
                partner.risk_profile = partner.active_suitability_id.risk_profile
            else:
                partner.risk_profile = False
    
    @api.depends('active_suitability_id', 'active_suitability_id.total_score')
    def _compute_risk_score(self):
        """Get risk score from active suitability"""
        for partner in self:
            if partner.active_suitability_id:
                partner.risk_score = partner.active_suitability_id.total_score
            else:
                partner.risk_score = 0
    
    def _compute_document_count(self):
        """Count documents in client folder"""
        Document = self.env['documents.document']
        for partner in self:
            if partner.document_folder_id:
                partner.document_count = Document.search_count([
                    ('folder_id', 'child_of', partner.document_folder_id.id)
                ])
            else:
                partner.document_count = 0
    
    def _compute_missing_documents(self):
        """List missing mandatory documents"""
        for partner in self:
            missing = []
            
            if not partner.document_folder_id:
                partner.missing_documents = 'Document folder not created'
                continue
            
            # Check mandatory documents
            required_tags = [
                'doc_rg_cnh',
                'doc_comprovante_residencia',
                'doc_suitability',
                'doc_termo_ciencia',
            ]
            
            Document = self.env['documents.document']
            for tag_name in required_tags:
                tag = self.env.ref(f'finance_compliance.tag_{tag_name}', raise_if_not_found=False)
                if tag:
                    exists = Document.search([
                        ('folder_id', 'child_of', partner.document_folder_id.id),
                        ('tag_ids', 'in', tag.id)
                    ], limit=1)
                    
                    if not exists:
                        missing.append(tag.name)
            
            if missing:
                partner.missing_documents = ', '.join(missing)
            else:
                partner.missing_documents = False
    
    def _compute_pending_approvals(self):
        """Count pending compliance approvals"""
        for partner in self:
            partner.pending_compliance_approvals = self.env['compliance.approval'].search_count([
                ('partner_id', '=', partner.id),
                ('state', '=', 'pending')
            ])
    
    @api.depends('suitability_status', 'kyc_status')
    def _compute_can_invest(self):
        """Check if client can make investments"""
        for partner in self:
            partner.can_invest = (
                partner.suitability_status == 'valid' and
                partner.kyc_status == 'completed'
            )
    
    @api.depends('risk_profile', 'suitability_status', 'kyc_status')
    def _compute_investment_restrictions(self):
        """List investment restrictions"""
        for partner in self:
            restrictions = []
            
            if partner.suitability_status != 'valid':
                restrictions.append('⚠️ Suitability inválido ou expirado')
            
            if partner.kyc_status != 'completed':
                restrictions.append('⚠️ KYC não completado')
            
            if partner.is_pep:
                restrictions.append('⚠️ Cliente PEP - requer aprovação adicional')
            
            if partner.risk_profile:
                risk_levels = {
                    'conservador_defensivo': [1, 2],
                    'conservador_classico': [1, 2, 3],
                    'moderado_equilibrado': [1, 2, 3, 4],
                    'moderado_dinamico': [1, 2, 3, 4, 5],
                    'agressivo_arrojado': [1, 2, 3, 4, 5, 6],
                    'agressivo_sofisticado': [1, 2, 3, 4, 5, 6, 7],
                }
                
                allowed = risk_levels.get(partner.risk_profile, [])
                restrictions.append(f'✅ Produtos permitidos: níveis de risco {", ".join(map(str, allowed))}')
            
            partner.investment_restrictions = '\n'.join(restrictions) if restrictions else False
    
    # ================================
    # CRUD OVERRIDES
    # ================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Create document folder when finance client is created"""
        partners = super().create(vals_list)
        
        for partner in partners.filtered('is_finance_client'):
            if not partner.document_folder_id:
                partner._create_document_folder()
        
        return partners
    
    def write(self, vals):
        """Create document folder when partner becomes finance client"""
        result = super().write(vals)
        
        if vals.get('is_finance_client'):
            for partner in self.filtered(lambda p: p.is_finance_client and not p.document_folder_id):
                partner._create_document_folder()
        
        return result
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_start_suitability(self):
        """Open wizard to start suitability questionnaire"""
        self.ensure_one()
        
        if self.suitability_status == 'valid':
            raise UserError(_(
                'Client already has a valid suitability. '
                'Use "Renew Suitability" action instead.'
            ))
        
        return {
            'name': _('Suitability Questionnaire'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.questionnaire.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
            }
        }
    
    def action_renew_suitability(self):
        """Renew existing suitability"""
        self.ensure_one()
        
        return {
            'name': _('Renew Suitability'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.questionnaire.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'is_renewal': True,
            }
        }
    
    def action_view_documents(self):
        """Open client document folder"""
        self.ensure_one()
        
        if not self.document_folder_id:
            self._create_document_folder()
        
        return {
            'name': _('Client Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban,tree,form',
            'domain': [('folder_id', 'child_of', self.document_folder_id.id)],
            'context': {
                'default_folder_id': self.document_folder_id.id,
                'default_partner_id': self.id,
            }
        }
    
    def action_view_compliance_approvals(self):
        """View compliance approvals for this client"""
        self.ensure_one()
        
        return {
            'name': _('Compliance Approvals'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.approval',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
            }
        }
    
    # ================================
    # HELPER METHODS
    # ================================
    
    def _create_document_folder(self):
        """Create document folder structure for client"""
        self.ensure_one()
        
        if self.document_folder_id:
            return self.document_folder_id
        
        Folder = self.env['documents.folder']
        
        # Get or create main Clientes workspace
        workspace = self.env.ref('finance_compliance.documents_workspace_clientes', raise_if_not_found=False)
        if not workspace:
            workspace = self.env['documents.folder'].create({
                'name': 'Clientes',
                'description': 'Documentos de clientes',
                'parent_folder_id': False,
            })
        
        # Create client main folder
        folder_name = f"{self.finance_profile_id or self.id} - {self.name}"
        main_folder = Folder.create({
            'name': folder_name,
            'parent_folder_id': workspace.id,
            'description': f'Documentos do cliente {self.name}',
        })
        
        # Create subfolders
        subfolders = [
            ('01. Cadastro', 'Documentos cadastrais'),
            ('02. Compliance', 'Documentos de compliance e suitability'),
            ('03. Contratos', 'Contratos e termos'),
            ('04. Operações', 'Boletins e comprovantes de operações'),
            ('05. Relatórios', 'Extratos e relatórios'),
        ]
        
        for subfolder_name, description in subfolders:
            Folder.create({
                'name': subfolder_name,
                'parent_folder_id': main_folder.id,
                'description': description,
            })
        
        self.document_folder_id = main_folder
        
        return main_folder
    
    @api.model
    def _cron_check_suitability_expiry(self):
        """Scheduled action to check suitability expiry"""
        today = fields.Date.today()
        
        # Partners with suitability expiring in 180 days
        expiring_180 = self.search([
            ('is_finance_client', '=', True),
            ('suitability_status', '=', 'valid'),
            ('days_to_suitability_expiry', '<=', 180),
            ('days_to_suitability_expiry', '>', 90),
        ])
        
        for partner in expiring_180:
            partner._notify_suitability_expiry(180)
        
        # Partners with suitability expiring in 90 days
        expiring_90 = self.search([
            ('is_finance_client', '=', True),
            ('suitability_status', '=', 'valid'),
            ('days_to_suitability_expiry', '<=', 90),
            ('days_to_suitability_expiry', '>', 30),
        ])
        
        for partner in expiring_90:
            partner._notify_suitability_expiry(90)
        
        # Partners with suitability expiring in 30 days
        expiring_30 = self.search([
            ('is_finance_client', '=', True),
            ('suitability_status', '=', 'valid'),
            ('days_to_suitability_expiry', '<=', 30),
            ('days_to_suitability_expiry', '>', 0),
        ])
        
        for partner in expiring_30:
            partner._notify_suitability_expiry(30)
        
        # Mark expired suitability
        expired = self.search([
            ('is_finance_client', '=', True),
            ('suitability_status', '=', 'valid'),
            ('days_to_suitability_expiry', '<=', 0),
        ])
        
        for partner in expired:
            partner.active_suitability_id.write({'state': 'expired'})
            partner._notify_suitability_expired()
    
    def _notify_suitability_expiry(self, days):
        """Notify about upcoming suitability expiry"""
        self.ensure_one()
        
        if not self.advisor_id:
            return
        
        message = _(
            '<p><strong>⚠️ Suitability Expiring Soon</strong></p>'
            '<p>Client <strong>%s</strong> suitability will expire in <strong>%d days</strong>.</p>'
            '<p>Expiry date: <strong>%s</strong></p>'
            '<p>Please schedule renewal process.</p>'
        ) % (
            self.name,
            days,
            self.suitability_expiry_date.strftime('%d/%m/%Y')
        )
        
        self.message_post(
            body=message,
            subject=f'Suitability Expiring in {days} Days',
            partner_ids=[self.advisor_id.partner_id.id],
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
    
    def _notify_suitability_expired(self):
        """Notify that suitability has expired"""
        self.ensure_one()
        
        message = _(
            '<p><strong>🚫 Suitability Expired</strong></p>'
            '<p>Client <strong>%s</strong> suitability has <strong>EXPIRED</strong>.</p>'
            '<p>Expired on: <strong>%s</strong></p>'
            '<p><strong>Client cannot make new investments until suitability is renewed.</strong></p>'
        ) % (
            self.name,
            self.suitability_expiry_date.strftime('%d/%m/%Y')
        )
        
        recipients = [self.advisor_id.partner_id.id] if self.advisor_id else []
        
        # Add compliance managers
        compliance_managers = self.env.ref('finance_compliance.group_compliance_manager').users
        recipients.extend([u.partner_id.id for u in compliance_managers])
        
        self.message_post(
            body=message,
            subject='🚫 Suitability EXPIRED',
            partner_ids=recipients,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
```

---

### 2. `compliance_suitability.py`

```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class ComplianceSuitability(models.Model):
    _name = 'compliance.suitability'
    _description = 'Client Suitability Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'application_date desc'
    _rec_name = 'reference'
    
    # ================================
    # FIELDS - Identification
    # ================================
    reference = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Unique suitability reference number'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        ondelete='restrict',
        tracking=True,
        domain=[('is_finance_client', '=', True)]
    )
    
    questionnaire_id = fields.Many2one(
        'compliance.questionnaire',
        string='Questionnaire Template',
        required=True,
        ondelete='restrict'
    )
    
    # ================================
    # FIELDS - Dates
    # ================================
    application_date = fields.Date(
        string='Application Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    
    approval_date = fields.Date(
        string='Approval Date',
        readonly=True,
        tracking=True
    )
    
    expiry_date = fields.Date(
        string='Expiry Date',
        compute='_compute_expiry_date',
        store=True,
        help='Suitability valid for 24 months'
    )
    
    # ================================
    # FIELDS - Answers
    # ================================
    answer_ids = fields.One2many(
        'compliance.answer',
        'suitability_id',
        string='Answers'
    )
    
    # ================================
    # FIELDS - Scoring
    # ================================
    financial_score = fields.Integer(
        compute='_compute_scores',
        store=True,
        string='Financial Score'
    )
    
    objective_score = fields.Integer(
        compute='_compute_scores',
        store=True,
        string='Objective Score'
    )
    
    knowledge_score = fields.Integer(
        compute='_compute_scores',
        store=True,
        string='Knowledge Score'
    )
    
    psychological_score = fields.Integer(
        compute='_compute_scores',
        store=True,
        string='Psychological Score'
    )
    
    total_score = fields.Integer(
        compute='_compute_total_score',
        store=True,
        string='Total Score (0-100)'
    )
    
    risk_profile = fields.Selection([
        ('conservador_defensivo', 'Conservador Defensivo'),
        ('conservador_classico', 'Conservador Clássico'),
        ('moderado_equilibrado', 'Moderado Equilibrado'),
        ('moderado_dinamico', 'Moderado Dinâmico'),
        ('agressivo_arrojado', 'Agressivo Arrojado'),
        ('agressivo_sofisticado', 'Agressivo Sofisticado'),
    ], compute='_compute_risk_profile', store=True, tracking=True)
    
    # ================================
    # FIELDS - Approval
    # ================================
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], default='draft', required=True, tracking=True)
    
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By',
        readonly=True,
        tracking=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        tracking=True
    )
    
    # ================================
    # FIELDS - Client Declaration
    # ================================
    client_signature = fields.Binary(
        string='Client Signature',
        attachment=True
    )
    
    client_signature_date = fields.Datetime(
        string='Signed At'
    )
    
    client_ip_address = fields.Char(
        string='IP Address'
    )
    
    declaration_text = fields.Html(
        string='Declaration',
        default=lambda self: self._default_declaration()
    )
    
    # ================================
    # FIELDS - Technical
    # ================================
    is_renewal = fields.Boolean(
        string='Is Renewal',
        default=False,
        help='Indicates if this is a renewal of previous suitability'
    )
    
    previous_suitability_id = fields.Many2one(
        'compliance.suitability',
        string='Previous Suitability',
        ondelete='set null'
    )
    
    notes = fields.Text('Internal Notes')
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('answer_ids', 'answer_ids.score')
    def _compute_scores(self):
        """Calculate scores by category"""
        for suitability in self:
            # Get answers grouped by category
            financial = sum(suitability.answer_ids.filtered(
                lambda a: a.question_id.category == 'financial'
            ).mapped('score'))
            
            objective = sum(suitability.answer_ids.filtered(
                lambda a: a.question_id.category == 'objective'
            ).mapped('score'))
            
            knowledge = sum(suitability.answer_ids.filtered(
                lambda a: a.question_id.category == 'knowledge'
            ).mapped('score'))
            
            psychological = sum(suitability.answer_ids.filtered(
                lambda a: a.question_id.category == 'psychological'
            ).mapped('score'))
            
            suitability.financial_score = financial
            suitability.objective_score = objective
            suitability.knowledge_score = knowledge
            suitability.psychological_score = psychological
    
    @api.depends('financial_score', 'objective_score', 'knowledge_score', 'psychological_score')
    def _compute_total_score(self):
        """Calculate weighted total score"""
        for suitability in self:
            # Weights: Financial 25%, Objective 25%, Knowledge 30%, Psychological 20%
            total = (
                (suitability.financial_score * 0.25) +
                (suitability.objective_score * 0.25) +
                (suitability.knowledge_score * 0.30) +
                (suitability.psychological_score * 0.20)
            )
            suitability.total_score = int(total)
    
    @api.depends('total_score')
    def _compute_risk_profile(self):
        """Classify risk profile based on score"""
        for suitability in self:
            score = suitability.total_score
            
            if score <= 16:
                suitability.risk_profile = 'conservador_defensivo'
            elif score <= 33:
                suitability.risk_profile = 'conservador_classico'
            elif score <= 50:
                suitability.risk_profile = 'moderado_equilibrado'
            elif score <= 66:
                suitability.risk_profile = 'moderado_dinamico'
            elif score <= 83:
                suitability.risk_profile = 'agressivo_arrojado'
            else:
                suitability.risk_profile = 'agressivo_sofisticado'
    
    @api.depends('approval_date')
    def _compute_expiry_date(self):
        """Calculate expiry date (24 months after approval)"""
        for suitability in self:
            if suitability.approval_date:
                suitability.expiry_date = suitability.approval_date + timedelta(days=730)  # 24 months
            else:
                suitability.expiry_date = False
    
    # ================================
    # CRUD METHODS
    # ================================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate reference number"""
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('compliance.suitability') or _('New')
        
        return super().create(vals_list)
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_submit(self):
        """Submit suitability for review"""
        self.ensure_one()
        
        if not self.answer_ids:
            raise ValidationError(_('Please answer all questions before submitting.'))
        
        # Check if all questions answered
        total_questions = len(self.questionnaire_id.question_ids)
        answered = len(self.answer_ids)
        
        if answered < total_questions:
            raise ValidationError(_(
                'Please answer all questions. '
                'Answered: %d/%d'
            ) % (answered, total_questions))
        
        self.write({
            'state': 'submitted',
        })
        
        # Notify compliance team
        self._notify_submission()
    
    def action_approve(self):
        """Approve suitability"""
        self.ensure_one()
        
        self.write({
            'state': 'approved',
            'approval_date': fields.Date.today(),
            'reviewed_by': self.env.user.id,
        })
        
        # Notify client and advisor
        self._notify_approval()
        
        # Create compliance approval record
        self.env['compliance.approval'].create({
            'partner_id': self.partner_id.id,
            'suitability_id': self.id,
            'approval_type': 'suitability',
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Date.today(),
        })
    
    def action_reject(self):
        """Open wizard to reject with reason"""
        self.ensure_one()
        
        return {
            'name': _('Reject Suitability'),
            'type': 'ir.actions.act_window',
            'res_model': 'compliance.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_suitability_id': self.id,
                'default_action': 'reject',
            }
        }
    
    def action_print_report(self):
        """Print suitability report"""
        self.ensure_one()
        return self.env.ref('finance_compliance.action_report_suitability').report_action(self)
    
    # ================================
    # HELPER METHODS
    # ================================
    
    def _default_declaration(self):
        """Default declaration text"""
        return """
        <h3>Declaração de Ciência de Riscos</h3>
        <p>Declaro para todos os fins de direito que:</p>
        <ol>
            <li>Respondi o questionário de suitability de forma verdadeira e completa;</li>
            <li>Estou ciente que a classificação do meu perfil de investidor é baseada nas informações prestadas;</li>
            <li>Entendo que operações incompatíveis com meu perfil podem resultar em perdas financeiras;</li>
            <li>Comprometo-me a atualizar minhas informações sempre que houver alterações relevantes;</li>
            <li>Recebi e li a Política de Investimentos e os documentos de risco dos produtos recomendados;</li>
            <li>Autorizo a gravação desta declaração e seu armazenamento pelo prazo legal.</li>
        </ol>
        <p><strong>Estou ciente dos riscos envolvidos nas operações de investimento.</strong></p>
        """
    
    def _notify_submission(self):
        """Notify compliance team about submission"""
        compliance_managers = self.env.ref('finance_compliance.group_compliance_manager').users
        
        message = _(
            '<p><strong>📋 New Suitability Submitted</strong></p>'
            '<p>Client: <strong>%s</strong></p>'
            '<p>Reference: <strong>%s</strong></p>'
            '<p>Score: <strong>%d/100</strong></p>'
            '<p>Profile: <strong>%s</strong></p>'
        ) % (
            self.partner_id.name,
            self.reference,
            self.total_score,
            dict(self._fields['risk_profile'].selection).get(self.risk_profile)
        )
        
        self.message_post(
            body=message,
            subject='New Suitability for Review',
            partner_ids=[u.partner_id.id for u in compliance_managers],
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
    
    def _notify_approval(self):
        """Notify about approval"""
        recipients = []
        
        if self.partner_id.advisor_id:
            recipients.append(self.partner_id.advisor_id.partner_id.id)
        
        message = _(
            '<p><strong>✅ Suitability Approved</strong></p>'
            '<p>Client: <strong>%s</strong></p>'
            '<p>Reference: <strong>%s</strong></p>'
            '<p>Profile: <strong>%s</strong></p>'
            '<p>Valid until: <strong>%s</strong></p>'
        ) % (
            self.partner_id.name,
            self.reference,
            dict(self._fields['risk_profile'].selection).get(self.risk_profile),
            self.expiry_date.strftime('%d/%m/%Y')
        )
        
        self.message_post(
            body=message,
            subject='Suitability Approved',
            partner_ids=recipients,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
```

---

## 🔄 Fluxos de Trabalho

### Fluxo 1: Aplicação Inicial de Suitability

```
1. Advisor abre cliente Finance
   ↓
2. Clica "Start Suitability" (aba Compliance)
   ↓
3. Wizard abre com questionário ANBIMA
   ↓
4. Advisor/Cliente responde perguntas
   - Situação Financeira (8 perguntas)
   - Objetivos de Investimento (6 perguntas)
   - Conhecimento e Experiência (10 perguntas)
   - Perfil Psicológico (6 perguntas)
   ↓
5. Scoring automático por categoria
   - Financial: 0-25 pts
   - Objective: 0-25 pts
   - Knowledge: 0-30 pts
   - Psychological: 0-20 pts
   ↓
6. Cálculo do Total Score (0-100)
   ↓
7. Classificação automática do perfil
   ↓
8. Cliente assina declaração de ciência
   ↓
9. State: Draft → Submitted
   ↓
10. Notificação para Compliance Team
   ↓
11. Compliance Manager revisa
   ↓
12. Aprovação ou Rejeição
   ↓ APROVADO
13. State: Approved
    - Expiry Date = hoje + 24 meses
    - Cria registro em Compliance Approvals
    - Notifica Advisor e Cliente
   ↓
14. Cliente pode investir!
```

---

### Fluxo 2: Criação Automática de Pasta de Documentos

```
Cliente marcado como Finance Client
   ↓
Trigger: create() ou write() de res.partner
   ↓
_create_document_folder() é chamado
   ↓
Busca/cria Workspace "Clientes"
   ↓
Cria pasta principal
Nome: [Profile ID] - [Nome do Cliente]
   ↓
Cria 5 subpastas:
   ├── 01. Cadastro
   ├── 02. Compliance
   ├── 03. Contratos
   ├── 04. Operações
   └── 05. Relatórios
   ↓
Define document_folder_id no partner
   ↓
Cliente pode fazer upload de documentos
```

---

### Fluxo 3: Verificação de Adequação de Produto

```
Advisor tenta aplicar R$ 100k em COE (nível 6)
   ↓
Sistema verifica:
   1. Cliente tem suitability válido?
   2. Qual o perfil de risco?
   3. Produto é compatível?
   ↓
Cliente: Moderado Equilibrado (produtos até nível 4)
Produto: COE (nível 6)
   ↓
❌ BLOQUEIO AUTOMÁTICO
   ↓
Mensagem: "Produto incompatível com perfil do cliente"
   ↓
Opção: "Solicitar Override de Compliance"
   ↓ SOLICITA
Cria Compliance Approval (type: product_override)
   - Produto: COE
   - Motivo: [texto do advisor]
   ↓
Notifica Compliance Manager
   ↓
Manager revisa e decide:
   ├→ APROVAR: Cliente pode investir neste produto
   └→ REJEITAR: Operação permanece bloqueada
```

---

## 📊 Questionário ANBIMA Padrão

### Categoria A: Situação Financeira (25%)

**A1. Qual sua faixa de renda mensal?**
- [ ] Até R$ 3.000 (0 pts)
- [ ] R$ 3.001 a R$ 10.000 (3 pts)
- [ ] R$ 10.001 a R$ 30.000 (5 pts)
- [ ] R$ 30.001 a R$ 100.000 (7 pts)
- [ ] Acima de R$ 100.000 (10 pts)

**A2. Qual seu patrimônio líquido estimado?**
- [ ] Até R$ 50.000 (0 pts)
- [ ] R$ 50.001 a R$ 200.000 (3 pts)
- [ ] R$ 200.001 a R$ 1.000.000 (5 pts)
- [ ] R$ 1.000.001 a R$ 5.000.000 (7 pts)
- [ ] Acima de R$ 5.000.000 (10 pts)

**A3. Que percentual do seu patrimônio pretende investir?**
- [ ] Até 10% (10 pts)
- [ ] 11% a 30% (7 pts)
- [ ] 31% a 50% (5 pts)
- [ ] 51% a 75% (3 pts)
- [ ] Acima de 75% (0 pts)

**A4. Você possui reserva de emergência?**
- [ ] Sim, equivalente a 6+ meses de despesas (5 pts)
- [ ] Sim, equivalente a 3-6 meses (3 pts)
- [ ] Sim, menos de 3 meses (1 pt)
- [ ] Não possuo (0 pts)

**A5. Suas despesas mensais representam que % da sua renda?**
- [ ] Até 30% (5 pts)
- [ ] 31% a 50% (4 pts)
- [ ] 51% a 70% (3 pts)
- [ ] 71% a 90% (1 pt)
- [ ] Acima de 90% (0 pts)

**A6. Você possui dívidas?**
- [ ] Não (5 pts)
- [ ] Sim, mas controladas (parcelamentos planejados) (3 pts)
- [ ] Sim, algumas dívidas (1 pt)
- [ ] Sim, muitas dívidas (0 pts)

**A7. Qual sua capacidade de suportar perdas financeiras?**
- [ ] Não posso ter nenhuma perda (0 pts)
- [ ] Até 5% do valor investido (3 pts)
- [ ] Até 15% do valor investido (5 pts)
- [ ] Até 30% do valor investido (7 pts)
- [ ] Acima de 30% do valor investido (10 pts)

**A8. Em quanto tempo você precisará resgatar o dinheiro investido?**
- [ ] Em menos de 1 ano (0 pts)
- [ ] Entre 1 e 2 anos (3 pts)
- [ ] Entre 2 e 5 anos (5 pts)
- [ ] Entre 5 e 10 anos (7 pts)
- [ ] Acima de 10 anos ou não tenho prazo (10 pts)

---

### Categoria B: Objetivos de Investimento (25%)

**B1. Qual seu principal objetivo com os investimentos?**
- [ ] Preservar capital (segurança) (0 pts)
- [ ] Crescimento moderado (5 pts)
- [ ] Crescimento agressivo (rentabilidade) (10 pts)

**B2. Qual sua expectativa de retorno anual?**
- [ ] Apenas preservar da inflação (0 pts)
- [ ] Inflação + 2% a 5% (3 pts)
- [ ] Inflação + 5% a 10% (6 pts)
- [ ] Acima da inflação + 10% (10 pts)

**B3. Como você se sente em relação a volatilidade?**
- [ ] Não aceito volatilidade (0 pts)
- [ ] Aceito volatilidade muito baixa (3 pts)
- [ ] Aceito volatilidade moderada (6 pts)
- [ ] Aceito alta volatilidade (10 pts)

**B4. Você precisa de renda regular dos investimentos?**
- [ ] Sim, mensalmente (0 pts)
- [ ] Sim, semestralmente (2 pts)
- [ ] Sim, anualmente (4 pts)
- [ ] Não preciso de renda regular (10 pts)

**B5. Em que momento da vida você está?**
- [ ] Início de carreira (acumulação) (10 pts)
- [ ] Meio de carreira (crescimento) (7 pts)
- [ ] Próximo da aposentadoria (preservação) (4 pts)
- [ ] Aposentado (usufruto) (0 pts)

**B6. Você pretende fazer aportes regulares?**
- [ ] Sim, mensalmente (5 pts)
- [ ] Sim, esporadicamente (3 pts)
- [ ] Não, apenas investimento inicial (0 pts)

---

### Categoria C: Conhecimento e Experiência (30%)

**C1. Qual seu nível de escolaridade?**
- [ ] Fundamental (0 pts)
- [ ] Médio (2 pts)
- [ ] Superior (4 pts)
- [ ] Pós-graduação (6 pts)

**C2. Você tem formação em finanças/economia?**
- [ ] Sim, sou profissional da área (10 pts)
- [ ] Sim, estudei na graduação (6 pts)
- [ ] Não, mas fiz cursos (3 pts)
- [ ] Não tenho formação (0 pts)

**C3. Há quanto tempo você investe?**
- [ ] Nunca investi (0 pts)
- [ ] Menos de 1 ano (2 pts)
- [ ] 1 a 3 anos (4 pts)
- [ ] 3 a 10 anos (7 pts)
- [ ] Mais de 10 anos (10 pts)

**C4. Com que frequência você faz operações?**
- [ ] Nunca fiz (0 pts)
- [ ] Raramente (1-2x por ano) (2 pts)
- [ ] Ocasionalmente (mensalmente) (5 pts)
- [ ] Frequentemente (semanalmente) (8 pts)
- [ ] Diariamente (day trade) (10 pts)

**C5. Marque os produtos que você conhece:**
- [ ] Poupança, CDB (1 pt)
- [ ] Tesouro Direto, LCI/LCA (2 pts)
- [ ] Fundos de Investimento (3 pts)
- [ ] Ações, ETFs (4 pts)
- [ ] Debêntures, CRI/CRA (5 pts)
- [ ] Derivativos (opções, futuros) (7 pts)
- [ ] Mercado Internacional (10 pts)

**C6. Em quais produtos você já investiu?**
- [ ] Nenhum (0 pts)
- [ ] Poupança, CDB (2 pts)
- [ ] Tesouro, Fundos (4 pts)
- [ ] Ações (6 pts)
- [ ] Derivativos (10 pts)

**C7. Você acompanha o mercado financeiro?**
- [ ] Nunca (0 pts)
- [ ] Raramente (2 pts)
- [ ] Semanalmente (5 pts)
- [ ] Diariamente (10 pts)

**C8. Você sabe o que é alavancagem?**
- [ ] Não sei (0 pts)
- [ ] Já ouvi falar (3 pts)
- [ ] Entendo o conceito (6 pts)
- [ ] Já utilizei (10 pts)

**C9. Você entende os riscos de cada classe de ativo?**
- [ ] Não entendo (0 pts)
- [ ] Entendo parcialmente (4 pts)
- [ ] Entendo bem (8 pts)
- [ ] Domino completamente (10 pts)

**C10. Você já teve perdas em investimentos?**
- [ ] Nunca investi (0 pts)
- [ ] Não, nunca tive perdas (3 pts)
- [ ] Sim, pequenas perdas (<10%) (6 pts)
- [ ] Sim, perdas significativas (>10%) (10 pts - experiência)

---

### Categoria D: Perfil Psicológico (20%)

**D1. Se seu investimento cair 20% em um mês, você:**
- [ ] Venderia tudo imediatamente (0 pts)
- [ ] Ficaria muito preocupado (2 pts)
- [ ] Ficaria um pouco preocupado (5 pts)
- [ ] Manteria a estratégia (8 pts)
- [ ] Aproveitaria para comprar mais (10 pts)

**D2. Sua preferência entre risco e retorno:**
- [ ] Segurança total, mesmo com retorno baixo (0 pts)
- [ ] Segurança moderada, retorno razoável (3 pts)
- [ ] Equilíbrio entre risco e retorno (5 pts)
- [ ] Aceito mais risco por retorno maior (8 pts)
- [ ] Alto risco, alta rentabilidade (10 pts)

**D3. Qual prazo você consegue manter investido?**
- [ ] Menos de 1 ano (0 pts)
- [ ] 1 a 3 anos (3 pts)
- [ ] 3 a 5 anos (6 pts)
- [ ] 5 a 10 anos (8 pts)
- [ ] Acima de 10 anos (10 pts)

**D4. Você costuma seguir sua estratégia mesmo com volatilidade?**
- [ ] Não, sempre mudo (0 pts)
- [ ] Raramente mantenho (3 pts)
- [ ] Às vezes mantenho (5 pts)
- [ ] Geralmente mantenho (8 pts)
- [ ] Sempre mantenho (10 pts)

**D5. Como você se sente com volatilidade diária?**
- [ ] Muito desconfortável (0 pts)
- [ ] Desconfortável (3 pts)
- [ ] Indiferente (5 pts)
- [ ] Confortável (8 pts)
- [ ] Muito confortável (10 pts)

**D6. Você prefere:**
- [ ] Rentabilidade previsível e estável (0 pts)
- [ ] Rentabilidade razoável com pouca oscilação (4 pts)
- [ ] Rentabilidade variável mas potencialmente maior (7 pts)
- [ ] Máxima rentabilidade independente da oscilação (10 pts)

---

## 🎓 Próximos Passos

Após a criação deste documento, o próximo passo é:

1. **Criar todos os arquivos Python do módulo**
2. **Criar as views XML**
3. **Criar os dados iniciais (questionário ANBIMA)**
4. **Criar os relatórios**
5. **Testar integração com Finance Core**
6. **Testar integração com Documents**

---

**Documento criado em:** 2024-11-24  
**Versão Odoo:** 19.0  
**Compliance:** CVM 539/2013 + ANBIMA  
**Status:** Arquitetura Completa - Pronto para Implementação
