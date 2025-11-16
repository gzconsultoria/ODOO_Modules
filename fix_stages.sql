-- Script para limpar stages duplicados criados pelo módulo crm_wealth

-- Lista os stages atuais
SELECT id, name, sequence, is_won 
FROM crm_stage 
WHERE name LIKE '%Captação%' 
   OR name LIKE '%Qualificação%' 
   OR name LIKE '%Reunião%' 
   OR name LIKE '%Proposta%' 
   OR name LIKE '%Onboarding%' 
   OR name LIKE '%Execução%'
ORDER BY sequence;

-- Se houver duplicatas, você pode deletar os stages criados pelo módulo
-- (Os IDs específicos serão mostrados no SELECT acima)
-- DELETE FROM crm_stage WHERE id IN (lista_de_ids_duplicados);
