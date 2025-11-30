#!/usr/bin/env python3
"""
Script para desinstalar módulos antigos do Odoo
Execute via: Apps → Technical → Automated Actions
Ou copie e cole no shell do Odoo
"""

# Copie e cole este código no Odoo Shell (Settings → Technical → Database Structure → Shell)

# Desinstalar document_hub
module_hub = env['ir.module.module'].search([('name', '=', 'document_hub')])
if module_hub:
    print(f"Desinstalando document_hub (estado: {module_hub.state})")
    if module_hub.state == 'installed':
        module_hub.button_immediate_uninstall()
    else:
        module_hub.unlink()
    print("✓ document_hub removido")

# Desinstalar gz_finance_dochub  
module_dochub = env['ir.module.module'].search([('name', '=', 'gz_finance_dochub')])
if module_dochub:
    print(f"Desinstalando gz_finance_dochub (estado: {module_dochub.state})")
    if module_dochub.state == 'installed':
        module_dochub.button_immediate_uninstall()
    else:
        module_dochub.unlink()
    print("✓ gz_finance_dochub removido")

# Commit
env.cr.commit()
print("\n✅ Limpeza concluída!")
