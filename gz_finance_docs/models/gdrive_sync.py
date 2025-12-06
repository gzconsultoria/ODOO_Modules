# -*- coding: utf-8 -*-
"""
Módulo de Sincronização Google Drive
Permite controlar backup/sincronização via interface Odoo
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import subprocess
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class GDriveSyncConfig(models.TransientModel):
    _name = 'gdrive.sync.config'
    _description = 'Configuração de Sincronização Google Drive'
    
    auto_sync_enabled = fields.Boolean(
        string='Sincronização Automática',
        default=True,
        help='Sincronizar automaticamente a cada 6 horas'
    )
    
    sync_frequency = fields.Selection([
        ('hourly', 'A cada hora'),
        ('6hours', 'A cada 6 horas'),
        ('daily', 'Diariamente'),
        ('weekly', 'Semanalmente'),
    ], string='Frequência', default='6hours')
    
    last_sync_date = fields.Datetime(
        string='Última Sincronização',
        readonly=True
    )
    
    last_sync_status = fields.Selection([
        ('success', 'Sucesso'),
        ('failed', 'Falhou'),
        ('running', 'Em Execução'),
    ], string='Status', readonly=True)
    
    last_sync_files_count = fields.Integer(
        string='Arquivos Sincronizados',
        readonly=True
    )
    
    gdrive_folder_url = fields.Char(
        string='URL da Pasta Google Drive',
        help='Link para acessar os documentos no Google Drive'
    )
    
    
    def action_sync_now(self):
        """Executar sincronização manual"""
        self.ensure_one()
        
        _logger.info("🚀 Sincronização manual iniciada pelo usuário %s", self.env.user.name)
        
        try:
            # Atualizar status
            self.write({
                'last_sync_status': 'running',
            })
            self.env.cr.commit()
            
            # Executar script de sincronização
            result = subprocess.run(
                ['python3', '/opt/odoo/scripts/sync_to_gdrive.py'],
                capture_output=True,
                text=True,
                timeout=3600  # Timeout de 1 hora
            )
            
            if result.returncode == 0:
                self.write({
                    'last_sync_date': fields.Datetime.now(),
                    'last_sync_status': 'success',
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Sincronização Concluída'),
                        'message': _('Documentos sincronizados com sucesso no Google Drive'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_(
                    "Erro na sincronização:\n\n%s"
                ) % result.stderr)
                
        except subprocess.TimeoutExpired:
            self.write({'last_sync_status': 'failed'})
            raise UserError(_("Sincronização excedeu o tempo limite de 1 hora"))
            
        except Exception as e:
            self.write({'last_sync_status': 'failed'})
            _logger.exception("Erro na sincronização: %s", e)
            raise UserError(_("Erro na sincronização: %s") % str(e))
    
    
    def action_view_gdrive_folder(self):
        """Abrir pasta no Google Drive"""
        self.ensure_one()
        
        if not self.gdrive_folder_url:
            raise UserError(_("URL do Google Drive não configurada"))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.gdrive_folder_url,
            'target': 'new',
        }
    
    
    def action_test_connection(self):
        """Testar conexão com Google Drive"""
        self.ensure_one()
        
        try:
            result = subprocess.run(
                ['rclone', 'lsd', 'gzdrive:'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Conexão OK'),
                        'message': _('Conexão com Google Drive funcionando corretamente'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_(
                    "Erro na conexão:\n\n%s"
                ) % result.stderr)
                
        except Exception as e:
            raise UserError(_("Erro ao testar conexão: %s") % str(e))


class GDriveSyncLog(models.Model):
    _name = 'gdrive.sync.log'
    _description = 'Histórico de Sincronizações'
    _order = 'sync_date desc'
    
    sync_date = fields.Datetime(
        string='Data/Hora',
        default=fields.Datetime.now,
        required=True
    )
    
    status = fields.Selection([
        ('success', 'Sucesso'),
        ('failed', 'Falhou'),
        ('partial', 'Parcial'),
    ], string='Status', required=True)
    
    files_synced = fields.Integer(string='Arquivos Sincronizados')
    files_failed = fields.Integer(string='Arquivos com Erro')
    
    duration_seconds = fields.Float(string='Duração (s)')
    
    error_message = fields.Text(string='Mensagem de Erro')
    
    triggered_by = fields.Many2one(
        'res.users',
        string='Executado por',
        help='Usuário que iniciou (vazio se cron automático)'
    )
    
    log_file_path = fields.Char(
        string='Arquivo de Log',
        help='Caminho do arquivo de log detalhado'
    )
