partner = env['res.partner'].browse(28)
print(f"Nome: {partner.name}")
print(f"Profile ID no banco: {partner.finance_profile_id}")
