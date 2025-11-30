#!/usr/bin/env python3
"""
Test Script - Churn Detection Infrastructure
Valida criação de snapshots e cálculo de métricas
"""
import xmlrpc.client

# Configuração
URL = 'http://localhost:8069'
DB = 'gzcon'
USERNAME = 'admin'
PASSWORD = 'admin'

def test_snapshot_infrastructure():
    """Testa infraestrutura de snapshots AUM"""
    
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    
    print("=" * 80)
    print("🧪 TESTE: Infraestrutura Churn Detection")
    print("=" * 80)
    
    # 1. Verificar modelo finance.aum.snapshot
    print("\n1️⃣ Verificando modelo finance.aum.snapshot...")
    try:
        snapshot_model = models.execute_kw(DB, uid, PASSWORD,
            'ir.model', 'search_read',
            [[('model', '=', 'finance.aum.snapshot')]],
            {'fields': ['name', 'model'], 'limit': 1}
        )
        if snapshot_model:
            print(f"   ✅ Modelo encontrado: {snapshot_model[0]['name']}")
        else:
            print("   ❌ Modelo NÃO encontrado")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 2. Buscar cliente finance para teste
    print("\n2️⃣ Buscando cliente finance para teste...")
    finance_clients = models.execute_kw(DB, uid, PASSWORD,
        'res.partner', 'search_read',
        [[('is_finance_client', '=', True), ('aum', '>', 0)]],
        {'fields': ['name', 'aum', 'aum_3months_ago'], 'limit': 1}
    )
    
    if not finance_clients:
        print("   ⚠️ Nenhum cliente finance encontrado com AUM > 0")
        return
    
    client = finance_clients[0]
    print(f"   ✅ Cliente: {client['name']}")
    print(f"   💰 AUM Atual: R$ {client['aum']:,.2f}")
    print(f"   📊 AUM 3 meses atrás: R$ {client['aum_3months_ago']:,.2f}")
    
    # 3. Criar snapshot manual
    print(f"\n3️⃣ Criando snapshot manual para cliente {client['name']}...")
    try:
        snapshot_id = models.execute_kw(DB, uid, PASSWORD,
            'finance.aum.snapshot', 'create_snapshot_for_partner',
            [client['id'], False, 'manual', 'Teste infraestrutura churn']
        )
        print(f"   ✅ Snapshot criado: ID {snapshot_id}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Buscar snapshots existentes
    print("\n4️⃣ Buscando snapshots existentes...")
    snapshots = models.execute_kw(DB, uid, PASSWORD,
        'finance.aum.snapshot', 'search_read',
        [[('partner_id', '=', client['id'])]],
        {'fields': ['snapshot_date', 'aum_value', 'aum_variation_percent', 'source'], 
         'order': 'snapshot_date desc', 'limit': 5}
    )
    
    if snapshots:
        print(f"   ✅ {len(snapshots)} snapshot(s) encontrado(s):")
        for snap in snapshots:
            variation = snap['aum_variation_percent']
            icon = "📈" if variation > 0 else "📉" if variation < 0 else "➡️"
            print(f"      {icon} {snap['snapshot_date']}: R$ {snap['aum_value']:,.2f} ({variation:+.2f}%) [{snap['source']}]")
    else:
        print("   ⚠️ Nenhum snapshot encontrado")
    
    # 5. Verificar computed fields do partner
    print(f"\n5️⃣ Verificando computed fields do partner...")
    partner_data = models.execute_kw(DB, uid, PASSWORD,
        'res.partner', 'read',
        [client['id']],
        {'fields': ['meetings_last_6months', 'response_rate']}
    )[0]
    
    print(f"   📅 Reuniões (últimos 6 meses): {partner_data['meetings_last_6months']}")
    print(f"   📧 Taxa de resposta: {partner_data['response_rate']:.2f}%")
    
    # 6. Verificar churn indicator (se existir)
    print("\n6️⃣ Verificando churn indicator...")
    churn_indicators = models.execute_kw(DB, uid, PASSWORD,
        'crm.churn.indicator', 'search_read',
        [[('partner_id', '=', client['id'])]],
        {'fields': ['churn_risk_score', 'risk_level', 'aum_decline_percent', 
                   'meetings_last_6months', 'response_rate'], 'limit': 1}
    )
    
    if churn_indicators:
        indicator = churn_indicators[0]
        print(f"   ✅ Churn Indicator encontrado:")
        print(f"      🎯 Risk Score: {indicator['churn_risk_score']:.1f}/100")
        print(f"      ⚠️ Risk Level: {indicator['risk_level']}")
        print(f"      📉 AUM Decline: {indicator['aum_decline_percent']:.2f}%")
        print(f"      📅 Meetings: {indicator['meetings_last_6months']}")
        print(f"      📧 Response Rate: {indicator['response_rate']:.2f}%")
    else:
        print("   ⚠️ Nenhum churn indicator encontrado para este cliente")
    
    # 7. Testar cron (dry-run)
    print("\n7️⃣ Testando método do cron (sem executar)...")
    try:
        # Apenas buscar o cron para validar que existe
        cron = models.execute_kw(DB, uid, PASSWORD,
            'ir.cron', 'search_read',
            [[('name', 'ilike', 'Monthly AUM Snapshots')]],
            {'fields': ['name', 'interval_type', 'nextcall'], 'limit': 1}
        )
        if cron:
            print(f"   ✅ Cron configurado: {cron[0]['name']}")
            print(f"      ⏰ Próxima execução: {cron[0]['nextcall']}")
            print(f"      🔁 Intervalo: {cron[0]['interval_type']}")
        else:
            print("   ⚠️ Cron não encontrado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == '__main__':
    test_snapshot_infrastructure()
