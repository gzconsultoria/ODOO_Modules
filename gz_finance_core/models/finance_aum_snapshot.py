# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class FinanceAumSnapshot(models.Model):
    _name = 'finance.aum.snapshot'
    _description = 'Snapshot Mensal de AUM'
    _order = 'snapshot_date desc, partner_id'
    _rec_name = 'display_name'
    
    # ================================
    # SQL CONSTRAINTS
    # ================================
    _sql_constraints = [
        ('partner_date_unique',
         'UNIQUE(partner_id, snapshot_date)',
         'Já existe snapshot para este cliente nesta data!')
    ]
    
    # ================================
    # CAMPOS PRINCIPAIS
    # ================================
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade',
        index=True,
        domain=[('is_finance_client', '=', True)],
        help='Cliente de consultoria financeira'
    )
    
    snapshot_date = fields.Date(
        string='Data do Snapshot',
        required=True,
        default=fields.Date.today,
        index=True,
        help='Data em que o snapshot foi capturado (geralmente dia 1 do mês)'
    )
    
    aum_value = fields.Monetary(
        string='AUM (Patrimônio sob Gestão)',
        required=True,
        currency_field='currency_id',
        help='Valor do AUM nesta data'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moeda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    # ================================
    # METADADOS
    # ================================
    
    source = fields.Selection([
        ('auto', 'Automático (Cron)'),
        ('manual', 'Manual'),
        ('crm_conversion', 'Conversão CRM'),
        ('api', 'API Externa'),
    ], string='Origem', default='auto', required=True, index=True)
    
    notes = fields.Text(
        string='Observações',
        help='Anotações sobre este snapshot (ex: "Entrada grande de R$500k")'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        default=lambda self: self.env.company,
        required=True,
        index=True
    )
    
    # ================================
    # CAMPOS COMPUTADOS
    # ================================
    
    display_name = fields.Char(
        string='Nome',
        compute='_compute_display_name',
        store=True
    )
    
    previous_snapshot_id = fields.Many2one(
        'finance.aum.snapshot',
        string='Snapshot Anterior',
        compute='_compute_previous_snapshot',
        store=False,
        help='Snapshot do mês anterior para este cliente'
    )
    
    aum_variation = fields.Monetary(
        string='Variação AUM (R$)',
        compute='_compute_aum_variation',
        store=False,
        currency_field='currency_id',
        help='Diferença em reais vs mês anterior'
    )
    
    aum_variation_percent = fields.Float(
        string='Variação AUM (%)',
        compute='_compute_aum_variation',
        store=False,
        digits=(5, 2),
        help='Variação percentual vs mês anterior'
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('partner_id', 'snapshot_date', 'aum_value')
    def _compute_display_name(self):
        """Gerar nome amigável para o snapshot"""
        for snapshot in self:
            if snapshot.partner_id and snapshot.snapshot_date:
                snapshot.display_name = f"{snapshot.partner_id.name} - {snapshot.snapshot_date.strftime('%m/%Y')}"
            else:
                snapshot.display_name = 'Novo Snapshot'
    
    @api.depends('partner_id', 'snapshot_date')
    def _compute_previous_snapshot(self):
        """Buscar snapshot do mês anterior"""
        for snapshot in self:
            if snapshot.partner_id and snapshot.snapshot_date:
                # Buscar snapshot anterior (mais recente antes desta data)
                previous = self.search([
                    ('partner_id', '=', snapshot.partner_id.id),
                    ('snapshot_date', '<', snapshot.snapshot_date)
                ], order='snapshot_date desc', limit=1)
                
                snapshot.previous_snapshot_id = previous.id if previous else False
            else:
                snapshot.previous_snapshot_id = False
    
    @api.depends('aum_value', 'previous_snapshot_id', 'previous_snapshot_id.aum_value')
    def _compute_aum_variation(self):
        """Calcular variação vs mês anterior"""
        for snapshot in self:
            if snapshot.previous_snapshot_id:
                previous_aum = snapshot.previous_snapshot_id.aum_value
                
                # Variação em reais
                snapshot.aum_variation = snapshot.aum_value - previous_aum
                
                # Variação percentual
                if previous_aum > 0:
                    snapshot.aum_variation_percent = ((snapshot.aum_value - previous_aum) / previous_aum) * 100
                else:
                    snapshot.aum_variation_percent = 0.0
            else:
                snapshot.aum_variation = 0.0
                snapshot.aum_variation_percent = 0.0
    
    # ================================
    # MÉTODOS DE NEGÓCIO
    # ================================
    
    @api.model
    def create_snapshot_for_partner(self, partner, snapshot_date=None, source='manual', notes=None):
        """
        Criar snapshot para um cliente específico
        
        Args:
            partner: res.partner record
            snapshot_date: date (default: hoje)
            source: 'auto', 'manual', 'crm_conversion', 'api'
            notes: str (opcional)
        
        Returns:
            finance.aum.snapshot record
        """
        if not snapshot_date:
            snapshot_date = fields.Date.today()
        
        # Verificar se já existe snapshot para esta data
        existing = self.search([
            ('partner_id', '=', partner.id),
            ('snapshot_date', '=', snapshot_date)
        ], limit=1)
        
        if existing:
            _logger.warning(
                f"Snapshot já existe para {partner.name} em {snapshot_date}. "
                f"Atualizando valor existente."
            )
            existing.write({
                'aum_value': partner.aum,
                'source': source,
                'notes': notes or existing.notes
            })
            return existing
        
        # Criar novo snapshot
        snapshot_data = {
            'partner_id': partner.id,
            'snapshot_date': snapshot_date,
            'aum_value': partner.aum,
            'source': source,
        }
        
        if notes:
            snapshot_data['notes'] = notes
        
        snapshot = self.create(snapshot_data)
        
        _logger.info(
            f"Snapshot criado: {partner.name} | {snapshot_date} | "
            f"R$ {partner.aum:,.2f} | Origem: {source}"
        )
        
        return snapshot
    
    @api.model
    def _cron_create_monthly_snapshots(self):
        """
        CRON MENSAL: Criar snapshots de AUM para todos os clientes ativos
        
        Execução: Dia 1 de cada mês às 2:00 AM
        
        Lógica:
        1. Busca todos os clientes finance ativos
        2. Cria snapshot com AUM atual
        3. Registra logs de sucesso/erro
        """
        snapshot_date = fields.Date.today()
        
        _logger.info(f"📸 === INICIANDO CRIAÇÃO DE SNAPSHOTS MENSAIS ({snapshot_date}) ===")
        
        # Buscar todos os clientes financeiros ativos
        finance_clients = self.env['res.partner'].search([
            ('is_finance_client', '=', True),
            ('active', '=', True)
        ])
        
        _logger.info(f"Encontrados {len(finance_clients)} clientes financeiros ativos")
        
        snapshots_created = 0
        snapshots_updated = 0
        snapshots_skipped = 0
        errors = []
        
        for partner in finance_clients:
            try:
                # Verificar se já existe snapshot para hoje
                existing = self.search([
                    ('partner_id', '=', partner.id),
                    ('snapshot_date', '=', snapshot_date)
                ], limit=1)
                
                if existing:
                    # Atualizar se AUM mudou
                    if existing.aum_value != partner.aum:
                        existing.write({
                            'aum_value': partner.aum,
                            'source': 'auto',
                            'notes': f'Atualizado automaticamente via cron em {datetime.now()}'
                        })
                        snapshots_updated += 1
                        _logger.info(f"  ✓ Atualizado: {partner.name} - R$ {partner.aum:,.2f}")
                    else:
                        snapshots_skipped += 1
                else:
                    # Criar novo snapshot
                    self.create({
                        'partner_id': partner.id,
                        'snapshot_date': snapshot_date,
                        'aum_value': partner.aum,
                        'source': 'auto',
                        'notes': f'Snapshot mensal automático - {snapshot_date.strftime("%B/%Y")}'
                    })
                    snapshots_created += 1
                    _logger.info(f"  ✓ Criado: {partner.name} - R$ {partner.aum:,.2f}")
                
            except Exception as e:
                error_msg = f"Erro ao processar {partner.name}: {str(e)}"
                errors.append(error_msg)
                _logger.error(f"  ✗ {error_msg}", exc_info=True)
        
        # Log final
        _logger.info(
            f"=== SNAPSHOTS CONCLUÍDOS ===\n"
            f"  📸 Criados: {snapshots_created}\n"
            f"  🔄 Atualizados: {snapshots_updated}\n"
            f"  ⏭️  Ignorados: {snapshots_skipped}\n"
            f"  ❌ Erros: {len(errors)}"
        )
        
        if errors:
            _logger.error(f"Erros encontrados:\n" + "\n".join(errors))
        
        return True
    
    def action_view_partner(self):
        """Ação para visualizar o cliente"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.partner_id.name,
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
