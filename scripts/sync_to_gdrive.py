#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronização Odoo Filestore → Google Drive
Cria estrutura de pastas navegável com nomes legíveis
"""

import os
import sys
import subprocess
import hashlib
import logging
from pathlib import Path
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/var/log/odoo/gdrive_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

DB_NAME = "gzcon"
FILESTORE_PATH = f"/var/lib/odoo/filestore/{DB_NAME}"
GDRIVE_REMOTE = "gzdrive:GZ Consultoria - Documentos"
TEMP_SYNC_DIR = f"/tmp/odoo_gdrive_sync_{DB_NAME}"

# Conexão com banco de dados Odoo
import psycopg2

DB_CONFIG = {
    'host': 'db',  # Nome do service no docker-compose
    'port': 5432,
    'database': DB_NAME,
    'user': 'odoo',
    'password': 'odoo'
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_folder_structure():
    """
    Busca estrutura de pastas do banco de dados
    Retorna dict: {folder_id: {'name': str, 'parent_id': int, 'path': str}}
    """
    logger.info("📂 Buscando estrutura de pastas do banco...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Buscar todas as pastas
    cursor.execute("""
        SELECT id, name, parent_folder_id, client_folder, partner_id
        FROM document_hub_folder
        WHERE active = TRUE
        ORDER BY parent_folder_id NULLS FIRST, id
    """)
    
    folders = {}
    for row in cursor.fetchall():
        folder_id, name, parent_id, is_client_folder, partner_id = row
        
        # Decodificar nome JSONB se necessário
        if isinstance(name, dict):
            name = name.get('pt_BR', name.get('en_US', 'Sem Nome'))
        
        folders[folder_id] = {
            'name': name,
            'parent_id': parent_id,
            'is_client_folder': is_client_folder,
            'partner_id': partner_id,
            'path': None  # Será calculado depois
        }
    
    cursor.close()
    conn.close()
    
    # Calcular caminhos completos
    for folder_id in folders:
        folders[folder_id]['path'] = _build_folder_path(folders, folder_id)
    
    logger.info(f"✅ Encontradas {len(folders)} pastas")
    return folders


def _build_folder_path(folders, folder_id):
    """Constrói caminho completo da pasta recursivamente"""
    folder = folders[folder_id]
    
    if folder['parent_id'] is None:
        # Raiz
        return folder['name']
    
    parent_path = _build_folder_path(folders, folder['parent_id'])
    return f"{parent_path}/{folder['name']}"


def get_documents_by_folder():
    """
    Busca documentos e seus anexos
    Retorna dict: {folder_id: [{'attachment_id': int, 'filename': str, 'store_fname': str}]}
    """
    logger.info("📄 Buscando documentos e anexos...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            d.folder_id,
            a.id AS attachment_id,
            a.name AS filename,
            a.store_fname,
            a.checksum
        FROM document_hub_document d
        INNER JOIN document_hub_document_ir_attachment_rel rel ON d.id = rel.document_hub_document_id
        INNER JOIN ir_attachment a ON rel.ir_attachment_id = a.id
        WHERE d.active = TRUE
          AND a.store_fname IS NOT NULL
        ORDER BY d.folder_id, a.id
    """)
    
    documents = {}
    for row in cursor.fetchall():
        folder_id, attachment_id, filename, store_fname, checksum = row
        
        if folder_id not in documents:
            documents[folder_id] = []
        
        documents[folder_id].append({
            'attachment_id': attachment_id,
            'filename': filename,
            'store_fname': store_fname,
            'checksum': checksum
        })
    
    cursor.close()
    conn.close()
    
    total_docs = sum(len(docs) for docs in documents.values())
    logger.info(f"✅ Encontrados {total_docs} documentos em {len(documents)} pastas")
    return documents


def prepare_sync_directory(folders, documents):
    """
    Cria diretório temporário com estrutura espelhada
    Copia arquivos do filestore para paths legíveis
    """
    logger.info(f"🔨 Preparando diretório de sincronização: {TEMP_SYNC_DIR}")
    
    # Limpar diretório anterior
    if os.path.exists(TEMP_SYNC_DIR):
        subprocess.run(['rm', '-rf', TEMP_SYNC_DIR], check=True)
    
    os.makedirs(TEMP_SYNC_DIR, exist_ok=True)
    
    copied_files = 0
    skipped_files = 0
    
    for folder_id, docs in documents.items():
        if folder_id not in folders:
            logger.warning(f"⚠️ Pasta ID {folder_id} não encontrada, pulando...")
            continue
        
        folder_path = folders[folder_id]['path']
        target_dir = os.path.join(TEMP_SYNC_DIR, folder_path)
        
        # Criar diretório
        os.makedirs(target_dir, exist_ok=True)
        
        for doc in docs:
            source_file = os.path.join(FILESTORE_PATH, doc['store_fname'])
            target_file = os.path.join(target_dir, doc['filename'])
            
            # Verificar se arquivo existe
            if not os.path.exists(source_file):
                logger.warning(f"⚠️ Arquivo não encontrado: {source_file}")
                skipped_files += 1
                continue
            
            # Copiar arquivo (hard link para economizar espaço)
            try:
                if os.path.exists(target_file):
                    os.remove(target_file)
                
                os.link(source_file, target_file)
                copied_files += 1
                
            except Exception as e:
                logger.error(f"❌ Erro ao copiar {source_file}: {e}")
                skipped_files += 1
    
    logger.info(f"✅ Preparação concluída: {copied_files} arquivos copiados, {skipped_files} ignorados")
    return copied_files


def sync_to_google_drive():
    """Sincroniza diretório temporário para Google Drive usando rclone"""
    logger.info(f"☁️ Sincronizando com Google Drive: {GDRIVE_REMOTE}")
    
    start_time = datetime.now()
    
    try:
        result = subprocess.run([
            'rclone', 'sync',
            TEMP_SYNC_DIR,
            GDRIVE_REMOTE,
            '--progress',
            '--transfers', '4',  # Transferências paralelas
            '--checkers', '8',   # Verificadores paralelos
            '--stats', '10s',    # Estatísticas a cada 10s
            '--log-level', 'INFO',
            '--exclude', '.DS_Store',
            '--exclude', 'Thumbs.db',
            '--drive-chunk-size', '64M',  # Chunks maiores para performance
        ], check=True, capture_output=True, text=True)
        
        logger.info(result.stdout)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Sincronização concluída em {elapsed:.2f}s")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro na sincronização: {e.stderr}")
        return False


def cleanup():
    """Remove diretório temporário"""
    logger.info("🧹 Limpando arquivos temporários...")
    
    if os.path.exists(TEMP_SYNC_DIR):
        subprocess.run(['rm', '-rf', TEMP_SYNC_DIR], check=True)
        logger.info("✅ Limpeza concluída")


# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO SINCRONIZAÇÃO ODOO → GOOGLE DRIVE")
    logger.info("=" * 80)
    
    try:
        # 1. Buscar estrutura de pastas
        folders = get_folder_structure()
        
        # 2. Buscar documentos
        documents = get_documents_by_folder()
        
        # 3. Preparar diretório de sincronização
        files_count = prepare_sync_directory(folders, documents)
        
        if files_count == 0:
            logger.warning("⚠️ Nenhum arquivo para sincronizar")
            cleanup()
            return
        
        # 4. Sincronizar com Google Drive
        success = sync_to_google_drive()
        
        # 5. Limpar temporários
        cleanup()
        
        if success:
            logger.info("=" * 80)
            logger.info("✅ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO")
            logger.info("=" * 80)
        else:
            logger.error("❌ Sincronização falhou")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"❌ Erro fatal: {e}")
        cleanup()
        sys.exit(1)


if __name__ == '__main__':
    main()
