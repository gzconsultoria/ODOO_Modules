#!/usr/bin/env python3
"""
Script para DELETAR todas as views do módulo gz_finance_core
Necessário para permitir upgrade limpo quando novos campos são adicionados
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configurações do PostgreSQL
DB_HOST = 'db'
DB_PORT = '5432'
DB_NAME = 'gzcon'
DB_USER = 'odoo'
DB_PASSWORD = 'odoo'

print("🔌 Conectando ao PostgreSQL...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    print("✅ Conectado ao banco gzcon")
    
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    exit(1)

# ========================================
# PASSO 1: Listar views do módulo
# ========================================
print("\n📋 Buscando views do módulo gz_finance_core...")
query_list = """
    SELECT 
        v.id, 
        v.name, 
        v.model,
        v.type,
        m.name as module_name
    FROM ir_ui_view v
    LEFT JOIN ir_model_data d ON d.model = 'ir.ui.view' AND d.res_id = v.id
    LEFT JOIN ir_module_module m ON m.id = d.module
    WHERE d.module = (SELECT id FROM ir_module_module WHERE name = 'gz_finance_core')
    ORDER BY v.id;
"""

cursor.execute(query_list)
views = cursor.fetchall()

if not views:
    print("ℹ️  Nenhuma view encontrada para deletar")
    print("   (Isso é esperado se for primeira instalação)")
else:
    print(f"📊 Encontradas {len(views)} views:")
    for view_id, name, model, view_type, module in views:
        print(f"   - ID {view_id}: {name} ({model}.{view_type})")

# ========================================
# PASSO 2: Deletar views
# ========================================
if views:
    print(f"\n🗑️  Deletando {len(views)} views...")
    
    view_ids = [str(v[0]) for v in views]
    view_ids_str = ','.join(view_ids)
    
    # Deletar ir_model_data primeiro (foreign key)
    query_delete_data = f"""
        DELETE FROM ir_model_data 
        WHERE model = 'ir.ui.view' 
        AND res_id IN ({view_ids_str});
    """
    cursor.execute(query_delete_data)
    print(f"   ✅ Deletados {cursor.rowcount} registros de ir_model_data")
    
    # Deletar views
    query_delete_views = f"""
        DELETE FROM ir_ui_view 
        WHERE id IN ({view_ids_str});
    """
    cursor.execute(query_delete_views)
    print(f"   ✅ Deletadas {cursor.rowcount} views de ir_ui_view")

# ========================================
# PASSO 3: Verificar res.partner columns
# ========================================
print("\n🔍 Verificando campos no modelo res.partner...")
query_columns = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'res_partner' 
    AND column_name IN (
        'annual_income', 
        'monthly_expenses',
        'saving_capacity',
        'suitability_score',
        'marital_status',
        'spouse_name',
        'children_count',
        'main_goal',
        'goal_amount',
        'diagnosis_date',
        'proposal_date',
        'management_fee'
    )
    ORDER BY column_name;
"""
cursor.execute(query_columns)
existing_columns = cursor.fetchall()

if existing_columns:
    print(f"✅ Campos já existentes no banco ({len(existing_columns)}):")
    for col in existing_columns:
        print(f"   - {col[0]}")
else:
    print("ℹ️  Nenhum campo novo encontrado ainda")
    print("   (Serão criados no próximo upgrade)")

# ========================================
# FECHAR CONEXÃO
# ========================================
cursor.close()
conn.close()

print("\n" + "="*60)
print("✅ LIMPEZA CONCLUÍDA!")
print("="*60)
print("\n🚀 PRÓXIMO PASSO:")
print("   1. Aguarde 5 segundos para cache limpar")
print("   2. Acesse a interface do Odoo")
print("   3. Vá em Apps → gz_finance_core")
print("   4. Clique em UPGRADE")
print("   5. O upgrade vai criar os campos sem erros de view")
print("\n")
