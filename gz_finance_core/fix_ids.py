partners = env['res.partner'].search([('is_finance_client', '=', True), ('finance_profile_id', '=', False)])
print(f"Clientes encontrados: {len(partners)}")
for p in partners:
    print(f"Processando: {p.name}")
    p.write({'is_finance_client': True})
    env.cr.commit()
    print(f"  -> Profile ID: {p.finance_profile_id}")
