# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CrmAuditLog(models.Model):
    _name = 'crm.audit.log'
    _description = 'Log de Auditoria CRM'
    _order = 'timestamp desc, id desc'
    _rec_name = 'action_type'
    
    # ================================
    # CAMPOS PRINCIPAIS
    # ================================
    
    timestamp = fields.Datetime(
        string='Data/Hora',
        required=True,
        default=fields.Datetime.now,
        index=True
    )
    
    model_name = fields.Char(
        string='Modelo',
        required=True,
        index=True,
        help='Nome técnico do modelo (ex: crm.lead)'
    )
    
    res_id = fields.Integer(
        string='ID do Registro',
        required=True,
        index=True
    )
    
    record_name = fields.Char(
        string='Nome do Registro',
        help='Nome amigável do registro auditado'
    )
    
    # ================================
    # TIPO DE AÇÃO
    # ================================
    
    action_type = fields.Selection([
        ('create', 'Criação'),
        ('write', 'Modificação'),
        ('read', 'Leitura'),
        ('unlink', 'Exclusão'),
        ('stage_change', 'Mudança de Estágio'),
        ('profile_creation', 'Criação de Perfil'),
        ('data_export', 'Exportação de Dados'),
        ('lgpd_action', 'Ação LGPD'),
    ], string='Tipo de Ação', required=True, index=True)
    
    # ================================
    # DADOS DA ALTERAÇÃO
    # ================================
    
    field_name = fields.Char(
        string='Campo Alterado',
        help='Nome do campo que foi modificado'
    )
    
    old_value = fields.Text(
        string='Valor Anterior',
        help='Valor antes da modificação (JSON para campos relacionais)'
    )
    
    new_value = fields.Text(
        string='Novo Valor',
        help='Valor após a modificação (JSON para campos relacionais)'
    )
    
    changes_summary = fields.Text(
        string='Resumo das Mudanças',
        compute='_compute_changes_summary',
        store=True
    )
    
    # ================================
    # DADOS DO USUÁRIO
    # ================================
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuário',
        required=True,
        default=lambda self: self.env.user,
        index=True
    )
    
    ip_address = fields.Char(
        string='Endereço IP',
        help='IP de origem da ação'
    )
    
    user_agent = fields.Text(
        string='User Agent',
        help='Navegador/dispositivo usado'
    )
    
    # ================================
    # CONTEXTO ADICIONAL
    # ================================
    
    context_data = fields.Text(
        string='Contexto',
        help='Dados adicionais de contexto (JSON)'
    )
    
    notes = fields.Text(
        string='Observações'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.company,
        required=True,
        index=True
    )
    
    # ================================
    # CRITICIDADE
    # ================================
    
    severity = fields.Selection([
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ], string='Criticidade', default='low')
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    @api.depends('field_name', 'old_value', 'new_value')
    def _compute_changes_summary(self):
        """Gerar resumo legível das mudanças"""
        for record in self:
            if record.action_type == 'write' and record.field_name:
                record.changes_summary = f"{record.field_name}: '{record.old_value}' → '{record.new_value}'"
            elif record.action_type == 'create':
                record.changes_summary = 'Registro criado'
            elif record.action_type == 'unlink':
                record.changes_summary = 'Registro excluído'
            elif record.action_type == 'stage_change':
                record.changes_summary = f"Estágio: {record.old_value} → {record.new_value}"
            else:
                record.changes_summary = record.action_type or ''
    
    # ================================
    # HELPER METHODS
    # ================================
    
    @api.model
    def log_action(self, model_name, res_id, action_type, **kwargs):
        """
        Helper para criar log de auditoria
        
        Args:
            model_name: Nome do modelo (ex: 'crm.lead')
            res_id: ID do registro
            action_type: Tipo de ação ('create', 'write', etc)
            **kwargs: Campos adicionais (field_name, old_value, new_value, notes, etc)
        """
        try:
            # Buscar nome do registro
            record_name = None
            if model_name in self.env:
                record = self.env[model_name].browse(res_id)
                if record.exists():
                    record_name = record.display_name or record.name
            
            # Capturar IP (se disponível no contexto HTTP)
            ip_address = None
            try:
                request = self.env.context.get('request')
                if request:
                    ip_address = request.httprequest.remote_addr
            except:
                pass
            
            # Criar log
            log_data = {
                'model_name': model_name,
                'res_id': res_id,
                'record_name': record_name,
                'action_type': action_type,
                'ip_address': ip_address,
            }
            log_data.update(kwargs)
            
            return self.create(log_data)
        
        except Exception as e:
            _logger.error(f"Erro ao criar audit log: {str(e)}", exc_info=True)
            # Não falhar a operação principal se auditoria falhar
            return False
    
    @api.model
    def get_record_history(self, model_name, res_id, limit=50):
        """Buscar histórico completo de um registro"""
        return self.search([
            ('model_name', '=', model_name),
            ('res_id', '=', res_id)
        ], limit=limit, order='timestamp desc')
    
    @api.model
    def _cron_cleanup_old_logs(self):
        """
        Limpeza automática de logs antigos
        
        Política de Retenção:
        - Ações normais (read, write): 365 dias
        - Ações críticas (unlink, lgpd_action, data_export): mantém permanentemente
        - Criação de perfil: mantém permanentemente
        
        Executado via cron diário.
        """
        from datetime import datetime, timedelta
        
        # Calcular data limite (1 ano atrás)
        retention_date = datetime.now() - timedelta(days=365)
        
        _logger.info(f"🗑️ Iniciando cleanup de audit logs anteriores a {retention_date.date()}...")
        
        # Buscar logs elegíveis para exclusão (não-críticos + antigos)
        deletable_logs = self.search([
            ('timestamp', '<', retention_date),
            ('action_type', 'not in', ['unlink', 'lgpd_action', 'data_export', 'profile_creation'])
        ])
        
        count = len(deletable_logs)
        
        if count > 0:
            # Deletar em lotes de 1000 para evitar timeout
            batch_size = 1000
            deleted_total = 0
            
            while deletable_logs:
                batch = deletable_logs[:batch_size]
                batch.unlink()
                deleted_total += len(batch)
                deletable_logs = deletable_logs[batch_size:]
                
                _logger.info(f"  Lote deletado: {deleted_total}/{count} registros...")
            
            _logger.info(
                f"✅ Cleanup concluído: {deleted_total} audit logs deletados "
                f"(anteriores a {retention_date.date()})"
            )
        else:
            _logger.info("✅ Nenhum audit log elegível para exclusão encontrado.")
        
        return True
