#!/usr/bin/env python3
"""Script para limpar cache de views do Odoo via SQL direto"""
import psycopg2

# Configurações
db_config = {
    'dbname': 'gzcon',
    'user': 'odoo',
    'password': 'odoo',
    'host': 'localhost',
    'port': '5432'
}

try:
    # Conectar
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    print("✅ Conectado ao banco gzcon")
    
    # Buscar views do módulo gz_finance_core
    cur.execute("""
        SELECT iv.id, iv.name, iv.model
        FROM ir_ui_view iv
        JOIN ir_model_data imd ON imd.res_id = iv.id AND imd.model = 'ir.ui.view'
        WHERE imd.module = 'gz_finance_core'
        ORDER BY iv.model, iv.name
    """)
    
    views = cur.fetchall()
    print(f"\n📋 Encontradas {len(views)} views do módulo gz_finance_core:\n")
    
    for view_id, view_name, model in views:
        print(f"  - ID {view_id}: {view_name} ({model})")
    
    # Limpar cache de views_get (onde está o problema do tipo 'tree')
    print("\n🗑️  Limpando cache de views_get...")
    cur.execute("DELETE FROM ir_ui_view_custom WHERE user_id IS NULL")
    conn.commit()
    
    print("✅ Cache limpo com sucesso!")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ Erro de conexão: {e}")
    print("\n💡 Tente via Docker:")
    print("   docker exec odoo_modules-db-1 psql -U odoo -d gzcon -c \"SELECT * FROM ir_ui_view WHERE name LIKE '%gz.finance%'\"")
except Exception as e:
    print(f"❌ Erro: {e}")
