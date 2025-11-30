#!/usr/bin/env python3
"""
Força criação de colunas faltantes no res.partner via SQL direto
USAR APENAS SE: módulos instalados mas colunas não criadas
"""
import psycopg2

DB_HOST = 'localhost'
DB_PORT = '5432'  
DB_NAME = 'gzcon'
DB_USER = 'odoo'
DB_PASSWORD = 'odoo'

def fix_missing_columns():
    """Adiciona colunas faltantes no res.partner"""
    
    print("=" * 80)
    print("🔧 CRIAÇÃO MANUAL DE COLUNAS FALTANTES")
    print("=" * 80)
    
    try:
        # Conectar direto no PostgreSQL do container
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False
        cur = conn.cursor()
        
        print("\n✅ Conectado ao banco de dados gzcon")
        
        # Verificar quais colunas existem
        print("\n📊 Verificando colunas existentes em res_partner...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'res_partner' 
            AND column_name IN ('origin_lead_id', 'aum_3months_ago', 'meetings_last_6months', 'response_rate', 'finance_aum_snapshot_ids')
            ORDER BY column_name;
        """)
        
        existing = cur.fetchall()
        existing_names = [col[0] for col in existing]
        
        if existing:
            print("   Colunas existentes:")
            for col_name, col_type in existing:
                print(f"      ✅ {col_name} ({col_type})")
        else:
            print("   ⚠️ Nenhuma das colunas esperadas foi encontrada")
        
        # Adicionar colunas faltantes
        columns_to_add = {
            'origin_lead_id': 'INTEGER',  # Many2one → INTEGER
            'aum_3months_ago': 'NUMERIC',  # Monetary → NUMERIC
            'meetings_last_6months': 'INTEGER',  # Integer → INTEGER
            'response_rate': 'NUMERIC',  # Float → NUMERIC
        }
        
        print("\n🔨 Adicionando colunas faltantes...")
        added_count = 0
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_names:
                try:
                    sql = f'ALTER TABLE res_partner ADD COLUMN IF NOT EXISTS {col_name} {col_type};'
                    print(f"   ➕ {col_name} ({col_type})...", end=' ')
                    cur.execute(sql)
                    print("✅")
                    added_count += 1
                except Exception as e:
                    print(f"❌ Erro: {e}")
                    conn.rollback()
                    continue
            else:
                print(f"   ⏭️  {col_name} já existe")
        
        if added_count > 0:
            conn.commit()
            print(f"\n✅ {added_count} coluna(s) adicionada(s) com sucesso!")
        else:
            print("\n✅ Todas as colunas já existem!")
        
        # Verificar constraints
        print("\n📋 Verificando constraints...")
        cur.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'res_partner'::regclass
            AND conname LIKE '%origin_lead%';
        """)
        
        constraints = cur.fetchall()
        if constraints:
            for con_name, con_type, con_def in constraints:
                print(f"   ✅ {con_name} ({con_type}): {con_def[:60]}...")
        else:
            print("   ℹ️  Nenhum constraint específico para origin_lead_id")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ PROCESSO CONCLUÍDO")
        print("=" * 80)
        print("\n⚠️ IMPORTANTE: Reinicie o Odoo para aplicar mudanças:")
        print("   docker-compose restart web")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("\nVerifique se:")
        print("1. Container do PostgreSQL está rodando: docker ps | grep postgres")
        print("2. Credenciais estão corretas (user=odoo, password=odoo)")
        print("3. Porta 5432 está mapeada corretamente")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n⚠️  ATENÇÃO: Este script modificará diretamente o banco de dados!")
    print("Certifique-se de ter backup antes de prosseguir.\n")
    
    response = input("Deseja continuar? (sim/não): ").lower()
    
    if response in ['sim', 's', 'yes', 'y']:
        fix_missing_columns()
    else:
        print("❌ Operação cancelada pelo usuário")
