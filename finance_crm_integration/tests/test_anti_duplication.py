# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'finance_crm_integration')
class TestAntiDuplication(TransactionCase):
    """
    Testa sistema de anti-duplicação de Finance Profiles.
    
    Garante que:
    - Múltiplos Leads para MESMO partner NÃO criam profiles duplicados
    - Constraint SQL bloqueia duplicatas a nível de banco
    - Método helper get_or_create_for_partner funciona corretamente
    """
    
    def setUp(self):
        super(TestAntiDuplication, self).setUp()
        
        # Criar Partner único para testes
        self.partner = self.env['res.partner'].create({
            'name': 'Cliente Teste Anti-Duplicação',
            'email': 'teste@antidup.com',
            'company_type': 'person',
        })
        
        # Criar estágio "Ganho" (is_won=True)
        self.stage_won = self.env['crm.stage'].create({
            'name': 'Teste - Ganho',
            'sequence': 60,
            'is_won': True,
        })
    
    def test_01_single_lead_creates_profile(self):
        """Teste 1: Lead único cria profile normalmente"""
        
        # Criar Lead
        lead = self.env['crm.lead'].create({
            'name': 'Lead A - Teste 1',
            'partner_id': self.partner.id,
            'stage_id': self.stage_won.id,  # Trigger automático
        })
        
        # Verificar que profile foi criado
        self.assertTrue(lead.finance_profile_id, "Profile deveria ter sido criado")
        self.assertEqual(
            lead.finance_profile_id.partner_id.id,
            self.partner.id,
            "Profile deve estar vinculado ao partner correto"
        )
    
    def test_02_multiple_leads_same_partner_share_profile(self):
        """Teste 2: Dois Leads para MESMO partner compartilham profile (anti-duplicação)"""
        
        # Criar Lead A
        lead_a = self.env['crm.lead'].create({
            'name': 'Lead A - Teste 2',
            'partner_id': self.partner.id,
            'stage_id': self.stage_won.id,
        })
        
        profile_a = lead_a.finance_profile_id
        self.assertTrue(profile_a, "Lead A deveria criar profile")
        
        # Criar Lead B para MESMO partner
        lead_b = self.env['crm.lead'].create({
            'name': 'Lead B - Teste 2 (mesmo partner)',
            'partner_id': self.partner.id,
            'stage_id': self.stage_won.id,
        })
        
        profile_b = lead_b.finance_profile_id
        self.assertTrue(profile_b, "Lead B deveria ter profile vinculado")
        
        # ✅ VALIDAÇÃO CRÍTICA: Ambos Leads apontam para MESMO profile
        self.assertEqual(
            profile_a.id,
            profile_b.id,
            "❌ FALHOU: Lead B criou profile duplicado! Deveria vincular ao existente."
        )
        
        # Verificar que existe APENAS 1 profile para este partner
        profiles_count = self.env['finance.profile'].search_count([
            ('partner_id', '=', self.partner.id)
        ])
        self.assertEqual(
            profiles_count,
            1,
            f"❌ FALHOU: Encontrados {profiles_count} profiles. Deveria ter apenas 1."
        )
    
    def test_03_sql_constraint_blocks_duplicate(self):
        """Teste 3: Constraint SQL bloqueia criação manual de duplicata"""
        
        # Criar primeiro profile
        profile_1 = self.env['finance.profile'].create({
            'partner_id': self.partner.id,
            'investor_type': 'pf',
        })
        
        # Tentar criar segundo profile para MESMO partner
        with self.assertRaises(
            ValidationError,
            msg="❌ FALHOU: Constraint SQL deveria bloquear duplicata!"
        ):
            self.env['finance.profile'].create({
                'partner_id': self.partner.id,
                'investor_type': 'pj',
            })
    
    def test_04_helper_method_prevents_duplicate(self):
        """Teste 4: Método get_or_create_for_partner previne duplicatas"""
        
        # Primeira chamada: cria profile
        profile_1 = self.env['finance.profile'].get_or_create_for_partner(
            partner_id=self.partner.id,
            vals={'investor_type': 'pf'}
        )
        
        self.assertTrue(profile_1, "Primeira chamada deveria criar profile")
        
        # Segunda chamada: retorna MESMO profile (não cria duplicata)
        profile_2 = self.env['finance.profile'].get_or_create_for_partner(
            partner_id=self.partner.id,
            vals={'investor_type': 'pj'}  # Valor diferente
        )
        
        # ✅ VALIDAÇÃO: Ambas chamadas retornam MESMO profile
        self.assertEqual(
            profile_1.id,
            profile_2.id,
            "❌ FALHOU: get_or_create_for_partner criou duplicata!"
        )
        
        # Verificar que investor_type NÃO foi sobrescrito (permanece 'pf')
        self.assertEqual(
            profile_2.investor_type,
            'pf',
            "Helper method não deveria sobrescrever campos existentes"
        )
    
    def test_05_concurrent_leads_merge_data(self):
        """Teste 5: Dados de múltiplos Leads são mesclados no profile único"""
        
        # Lead A: preenche dados pessoais
        lead_a = self.env['crm.lead'].create({
            'name': 'Lead A - Dados Pessoais',
            'partner_id': self.partner.id,
        })
        
        # Simular campos do CRM Wealth
        if hasattr(lead_a, 'cliente_nascimento'):
            lead_a.cliente_nascimento = '1985-03-15'
        
        lead_a.stage_id = self.stage_won.id  # Trigger
        profile = lead_a.finance_profile_id
        
        # Lead B: preenche objetivos (mesmo partner)
        lead_b = self.env['crm.lead'].create({
            'name': 'Lead B - Objetivos',
            'partner_id': self.partner.id,
        })
        
        if hasattr(lead_b, 'objetivo_principal'):
            lead_b.objetivo_principal = 'Aposentadoria tranquila'
        
        lead_b.stage_id = self.stage_won.id  # Trigger
        
        # ✅ VALIDAÇÃO: Profile mesclou dados de ambos Leads
        self.assertEqual(
            lead_b.finance_profile_id.id,
            profile.id,
            "Lead B deveria vincular ao profile de Lead A"
        )
        
        # Verificar que dados foram mesclados
        if hasattr(profile, 'client_birthdate'):
            self.assertTrue(
                profile.client_birthdate,
                "Dados pessoais de Lead A deveriam estar no profile"
            )
        
        if hasattr(profile, 'main_goal'):
            self.assertTrue(
                profile.main_goal,
                "Objetivos de Lead B deveriam estar no profile"
            )
