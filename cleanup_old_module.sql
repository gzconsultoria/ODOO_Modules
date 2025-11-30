-- Limpeza completa do módulo document_hub_main
-- Execute este script no banco de dados gzcon

-- 1. Remover todos os dados XML/registros do módulo antigo
DELETE FROM ir_model_data WHERE module = 'document_hub_main';

-- 2. Remover o módulo da lista de módulos
DELETE FROM ir_module_module WHERE name = 'document_hub_main';

-- 3. Remover dependências
DELETE FROM ir_module_module_dependency WHERE name = 'document_hub_main';

-- 4. Limpar cache
-- Nota: O Odoo irá recriar automaticamente após restart
