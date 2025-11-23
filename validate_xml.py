#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador XML avançado com cores para identificar problemas em views do Odoo
"""
import sys
from lxml import etree
from colorama import Fore, Style, init

init(autoreset=True)

def validate_xml_file(filepath):
    print(f"{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Validando: {filepath}")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    try:
        # Parse XML
        tree = etree.parse(filepath)
        root = tree.getroot()
        
        print(f"{Fore.GREEN}✅ XML bem formado (sintaxe válida)\n")
        
        # Estatísticas
        records = root.findall(".//record")
        print(f"{Fore.YELLOW}📊 Estatísticas:")
        print(f"   Total de <record>: {len(records)}")
        
        # Análise de cada record
        for idx, record in enumerate(records, 1):
            rec_id = record.get('id', 'SEM ID')
            model = record.get('model', 'SEM MODEL')
            
            # Verifica se é uma view
            if model == 'ir.ui.view':
                name_field = record.find(".//field[@name='name']")
                view_model_field = record.find(".//field[@name='model']")
                arch_field = record.find(".//field[@name='arch']")
                
                view_name = name_field.text if name_field is not None else 'N/A'
                view_model = view_model_field.text if view_model_field is not None else 'N/A'
                
                print(f"\n{Fore.MAGENTA}[{idx}] View ID: {rec_id}")
                print(f"    Nome: {view_name}")
                print(f"    Model: {view_model}")
                
                if arch_field is not None:
                    arch_type = arch_field.get('type', 'xml')
                    print(f"    Arch type: {arch_type}")
                    
                    # Verifica conteúdo do arch
                    arch_children = list(arch_field)
                    if arch_children:
                        root_tag = arch_children[0].tag
                        print(f"    View type: <{root_tag}>")
                        
                        # Análise específica por tipo de view
                        if root_tag == 'search':
                            analyze_search_view(arch_children[0], rec_id)
                        elif root_tag == 'form':
                            analyze_form_view(arch_children[0], rec_id)
                        elif root_tag == 'list':
                            analyze_list_view(arch_children[0], rec_id)
                    else:
                        print(f"{Fore.RED}    ⚠️  Arch vazio!")
                else:
                    print(f"{Fore.RED}    ⚠️  Sem campo arch!")
            elif model == 'ir.actions.act_window':
                name_field = record.find(".//field[@name='name']")
                res_model_field = record.find(".//field[@name='res_model']")
                action_name = name_field.text if name_field is not None else 'N/A'
                res_model = res_model_field.text if res_model_field is not None else 'N/A'
                print(f"\n{Fore.CYAN}[{idx}] Action ID: {rec_id}")
                print(f"    Nome: {action_name}")
                print(f"    Model: {res_model}")
        
        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"{Fore.GREEN}✅ Validação concluída com sucesso!")
        print(f"{Fore.GREEN}{'='*80}\n")
        return True
        
    except etree.XMLSyntaxError as e:
        print(f"{Fore.RED}❌ Erro de sintaxe XML:")
        print(f"{Fore.RED}   Linha {e.lineno}: {e.msg}")
        print(f"{Fore.RED}{'='*80}\n")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_search_view(search_elem, view_id):
    """Analisa search view em detalhes"""
    fields = search_elem.findall('.//field')
    filters = search_elem.findall('.//filter')
    groups = search_elem.findall('.//group')
    
    print(f"{Fore.YELLOW}    📋 Campos de busca: {len(fields)}")
    for field in fields:
        field_name = field.get('name', 'SEM NOME')
        print(f"       - {field_name}")
    
    print(f"{Fore.YELLOW}    🔍 Filtros: {len(filters)}")
    for filt in filters:
        filt_name = filt.get('name', 'SEM NAME ATTR')
        filt_string = filt.get('string', 'SEM STRING')
        filt_domain = filt.get('domain', '')
        filt_context = filt.get('context', '')
        
        print(f"       - [{filt_name}] {filt_string}")
        if filt_domain:
            print(f"         domain={filt_domain}")
        if filt_context:
            # Verifica group_by
            if 'group_by' in filt_context:
                print(f"         {Fore.CYAN}context={filt_context}")
                if '[' in filt_context and ']' in filt_context:
                    print(f"         {Fore.RED}⚠️  group_by como LISTA (pode ser problema no Odoo 19!)")
                else:
                    print(f"         {Fore.GREEN}✓ group_by como STRING (correto Odoo 19)")
    
    print(f"{Fore.YELLOW}    👥 Grupos: {len(groups)}")
    for group in groups:
        group_string = group.get('string', 'SEM STRING')
        expand = group.get('expand', 'N/A')
        print(f"       - {group_string} (expand={expand})")

def analyze_form_view(form_elem, view_id):
    """Analisa form view em detalhes"""
    buttons = form_elem.findall('.//button')
    modifiers_buttons = [b for b in buttons if b.get('modifiers')]
    
    if modifiers_buttons:
        print(f"{Fore.RED}    ⚠️  PROBLEMA: {len(modifiers_buttons)} botões com atributo 'modifiers'")
        for btn in modifiers_buttons:
            btn_name = btn.get('name', 'SEM NOME')
            print(f"{Fore.RED}       - Botão: {btn_name}")
            print(f"{Fore.RED}         {btn.get('modifiers')}")
            print(f"{Fore.YELLOW}         Deve usar: invisible=\"expressão\" ao invés de modifiers")

def analyze_list_view(list_elem, view_id):
    """Analisa list view em detalhes"""
    fields = list_elem.findall('.//field')
    print(f"{Fore.YELLOW}    📊 Campos: {len(fields)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Uso: python validate_xml.py <arquivo.xml>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    success = validate_xml_file(filepath)
    sys.exit(0 if success else 1)
