#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração gz_finance_dochub para Odoo 19
Aplica todas as correções conhecidas de compatibilidade
"""
import re
import os
from pathlib import Path

MODULE_PATH = Path("/workspaces/ODOO_Modules/gz_finance_dochub")

def fix_tree_to_list(content):
    """Substitui <tree> por <list>"""
    content = re.sub(r'<tree\s', '<list ', content)
    content = re.sub(r'</tree>', '</list>', content)
    return content

def fix_view_mode_tree(content):
    """Substitui view_mode='tree' por 'list'"""
    content = re.sub(r"view_mode=['\"]([^'\"]*?)tree([^'\"]*?)['\"]", 
                    lambda m: f"view_mode='{m.group(1)}list{m.group(2)}'", content)
    return content

def fix_target_inline(content):
    """Substitui target='inline' por 'current'"""
    content = re.sub(r"target=['\"]inline['\"]", "target='current'", content)
    return content

def fix_nolabel_colspan(content):
    """Remove atributos nolabel e colspan deprecated"""
    content = re.sub(r'\s+nolabel=["\']1["\']', '', content)
    content = re.sub(r'\s+colspan=["\']\d+["\']', '', content)
    return content

def fix_search_view_structure(content):
    """Corrige estrutura de search views para Odoo 19"""
    # Remove <group> inválidos em search views (mantém apenas os válidos)
    lines = content.split('\n')
    in_search = False
    fixed_lines = []
    
    for line in lines:
        if '<search' in line:
            in_search = True
        elif '</search>' in line:
            in_search = False
            
        # Remove <group> sem expand/string em search views
        if in_search and '<group>' in line and 'expand' not in line and 'string' not in line:
            continue
        elif in_search and '</group>' in line and fixed_lines and '<group>' not in ''.join(fixed_lines[-5:]):
            continue
            
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_chatter_structure(content):
    """Substitui <div class="oe_chatter"> por <chatter>"""
    content = re.sub(r'<div class="oe_chatter">', '<chatter>', content)
    content = re.sub(r'</div>\s*</form>', '</chatter>\n                </form>', content, count=1)
    return content

def fix_groups_security(content):
    """Remove category_id e users de res.groups (Odoo 19)"""
    # Remove linhas com category_id
    content = re.sub(r'\s*<field name="category_id"[^/]*/>',  '', content)
    # Remove linhas com users
    content = re.sub(r'\s*<field name="users"[^/]*/>',  '', content)
    return content

def process_xml_file(filepath):
    """Processa um arquivo XML aplicando todas as correções"""
    print(f"📝 Processando: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Aplicar correções
    content = fix_tree_to_list(content)
    content = fix_view_mode_tree(content)
    content = fix_target_inline(content)
    content = fix_nolabel_colspan(content)
    content = fix_search_view_structure(content)
    content = fix_chatter_structure(content)
    
    if 'security' in str(filepath):
        content = fix_groups_security(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Modificado")
        return True
    else:
        print(f"  ⏭️  Sem alterações")
        return False

def main():
    print("🚀 Migração gz_finance_dochub para Odoo 19")
    print("=" * 60)
    
    # Processar todos os XMLs
    xml_files = list(MODULE_PATH.rglob("*.xml"))
    modified_count = 0
    
    for xml_file in sorted(xml_files):
        if process_xml_file(xml_file):
            modified_count += 1
    
    print("=" * 60)
    print(f"✅ Concluído! {modified_count}/{len(xml_files)} arquivos modificados")

if __name__ == '__main__':
    main()
