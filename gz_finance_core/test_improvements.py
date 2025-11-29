#!/usr/bin/env python3
"""
Script de teste para validar correções implementadas
"""

print("="*60)
print("TESTE DE VALIDAÇÃO - GZ_FINANCE_CORE")
print("="*60)

# Teste 1: AUM Calculation Fix
print("\n✅ TESTE 1: Correção de Cálculo de AUM")
print("Verificando se AUM usa apenas snapshot mais recente...")

partner = env['res.partner'].search([('is_finance_client', '=', True)], limit=1)
if partner:
    print(f"Cliente: {partner.name}")
    print(f"Snapshots: {len(partner.finance_patrimony_ids)}")
    
    if partner.finance_patrimony_ids:
        latest = partner.finance_patrimony_ids.sorted('date', reverse=True)[0]
        print(f"Snapshot mais recente: {latest.date} - R$ {latest.total_value:,.2f}")
        print(f"AUM calculado: R$ {partner.aum:,.2f}")
        
        if partner.aum == latest.total_value:
            print("✅ PASSOU: AUM correto (usa apenas último snapshot)")
        else:
            print(f"❌ FALHOU: AUM deveria ser {latest.total_value}, mas é {partner.aum}")
    else:
        print("⚠️ Sem snapshots para testar")
else:
    print("⚠️ Nenhum cliente financeiro encontrado")

# Teste 2: Profile ID Batch Generation
print("\n✅ TESTE 2: Geração de Profile ID em Batch")
print("Criando 3 clientes de uma vez...")

partners = env['res.partner'].create([
    {'name': f'Teste Batch {i}', 'is_finance_client': True}
    for i in range(1, 4)
])

ids_gerados = [p.finance_profile_id for p in partners if p.finance_profile_id]
print(f"Profile IDs gerados: {len(ids_gerados)}/3")

for p in partners:
    print(f"  - {p.name}: {p.finance_profile_id or '❌ SEM ID'}")

if len(ids_gerados) == 3:
    print("✅ PASSOU: Todos receberam Profile ID")
else:
    print(f"❌ FALHOU: Apenas {len(ids_gerados)}/3 receberam ID")

# Limpar dados de teste
partners.unlink()

# Teste 3: Validações
print("\n✅ TESTE 3: Validações de Campos")

test_partner = env['res.partner'].create({
    'name': 'Teste Validação',
    'is_finance_client': True,
})

# Teste 3.1: Management Fee
print("  3.1 Validação de Management Fee...")
try:
    test_partner.management_fee = 150
    print("  ❌ FALHOU: Deveria rejeitar fee > 100%")
except Exception as e:
    if 'entre 0% e 100%' in str(e):
        print("  ✅ PASSOU: Rejeita fee > 100%")
    else:
        print(f"  ⚠️ Erro inesperado: {e}")

# Teste 3.2: Goal Deadline
print("  3.2 Validação de Prazo Negativo...")
try:
    test_partner.goal_deadline_years = -5
    print("  ❌ FALHOU: Deveria rejeitar prazo negativo")
except Exception as e:
    if 'positivo' in str(e):
        print("  ✅ PASSOU: Rejeita prazo negativo")
    else:
        print(f"  ⚠️ Erro inesperado: {e}")

# Limpar
test_partner.unlink()

# Teste 4: Smart Button
print("\n✅ TESTE 4: Smart Button de Patrimônio")
partner = env['res.partner'].search([('is_finance_client', '=', True)], limit=1)
if partner:
    count = partner.patrimony_count
    real_count = len(partner.finance_patrimony_ids)
    print(f"patrimony_count: {count}")
    print(f"finance_patrimony_ids: {real_count}")
    
    if count == real_count:
        print("✅ PASSOU: Count correto")
    else:
        print(f"❌ FALHOU: Count deveria ser {real_count}")

print("\n" + "="*60)
print("TESTES CONCLUÍDOS")
print("="*60)
