# Finance Core Module for Odoo 19

## Overview

Finance Core is the foundational module for investment advisory operations in Odoo 19. It serves as the Single Source of Truth (SSOT) for all financial client data, providing centralized management of client profiles, lifecycle stages, assets under management (AUM), and compliance tracking.

## Features

### Client Management
- **Finance Client Profiles**: Extended partner model with financial-specific fields
- **Unique Profile IDs**: Automatic generation of unique finance profile identifiers
- **Client Segmentation**: Automatic categorization (Retail, Affluent, HNW, UHNW)
- **Advisor Assignment**: Multi-advisor support with team management

### Lifecycle Management
- **8 Lifecycle Stages**: Lead, Prospect, Onboarding, Active, VIP, Churning, Churned, Blocked
- **Automatic Tracking**: Complete history of all stage changes
- **Change Reasons**: Categorized reasons for lifecycle transitions
- **Duration Analytics**: Days spent in each stage

### AUM (Assets Under Management)
- **Real-time Calculation**: Automatic AUM computation from patrimony snapshots
- **Asset Class Breakdown**: Fixed Income, Equities, Funds, Real Estate, Alternatives, Cash
- **Historical Tracking**: Complete patrimony history over time
- **Variation Analysis**: Automatic calculation of period-over-period changes

### Compliance
- **KYC Status Tracking**: Pending, In Progress, Completed, Expired, Rejected
- **Automatic Expiry**: Scheduled job to mark expired KYC
- **Expiry Notifications**: Advisor alerts 30 days before expiration
- **PEP Flagging**: Politically Exposed Person tracking

### Risk Profile
- Conservative
- Moderate
- Aggressive
- Not Defined

### Security & Permissions
- **4-Level Access Control**:
  - Finance User (Read-only)
  - Finance Advisor (Manage own clients)
  - Finance Manager (Full access)
  - Finance Admin (Configuration)
- **Record-Level Security**: Advisors only see their clients
- **Multi-company Support**: Full multi-company compliance

## Installation

### Requirements
- Odoo 19.0+
- Python 3.10+
- PostgreSQL 13+

### Dependencies
- `base` - Core Odoo functionality
- `contacts` - Partner management
- `mail` - Chatter and notifications
- `web` - Web interface

### Install Steps

1. Copy the `finance_core` folder to your Odoo addons directory:
```bash
cp -r finance_core /path/to/odoo/addons/
```

2. Update the addons list:
```bash
odoo-bin -c /path/to/odoo.conf -u all --stop-after-init
```

3. Restart Odoo server:
```bash
systemctl restart odoo
```

4. Install the module:
   - Navigate to Apps
   - Remove "Apps" filter
   - Search for "Finance Core"
   - Click Install

## Configuration

### Post-Installation Setup

1. **Assign User Groups**:
   - Go to Settings → Users & Companies → Users
   - Assign appropriate Finance groups to users

2. **Configure AUM Thresholds**:
   - Go to Settings → Technical → Parameters → System Parameters
   - Adjust these values:
     - `finance_core.retail_max`: 100000
     - `finance_core.affluent_max`: 1000000
     - `finance_core.hnw_max`: 10000000

3. **Set KYC Parameters**:
   - `finance_core.kyc_validity_months`: 12
   - `finance_core.kyc_expiry_notification_days`: 30

4. **Configure Scheduled Actions**:
   - Go to Settings → Technical → Automation → Scheduled Actions
   - Verify these crons are active:
     - "Finance: Update KYC Expiry Status" (daily at 3 AM)
     - "Finance: Update AUM for All Clients" (daily at 6 AM)

## Usage

### Creating a Finance Client

1. Navigate to Finance → Clients → All Clients
2. Click Create
3. Toggle "Finance Client" ON
4. Fill in client details
5. A Finance Profile ID will be auto-generated (FIN-YYYYMMDD-XXXX)
6. Assign an Advisor
7. Set initial Lifecycle Stage (defaults to "Lead")

### Managing Lifecycle

**Via Statusbar** (Quick Change):
1. Open client record
2. Click desired stage in statusbar

**Via Wizard** (With Reason):
1. Open client record
2. Go to Finance tab
3. Click "Change Stage" button
4. Select new stage and reason
5. Add notes
6. Confirm

### Tracking Patrimony

1. Open client record
2. Go to Finance tab → Patrimony History
3. Add new line with:
   - Date
   - Asset breakdown by class
   - Source (Manual, Custody, etc.)
4. Total and variation calculated automatically
5. AUM updated automatically

### Compliance Management

1. Set KYC Status
2. Record KYC Completed Date
3. Set Expiry Date (auto-calculated based on validity months)
4. System will:
   - Mark as expired automatically
   - Notify advisor 30 days before expiry
   - Track PEP status

## Data Model

### res.partner (Extended)
- `finance_profile_id`: Unique ID
- `is_finance_client`: Boolean flag
- `finance_lifecycle_state`: Selection
- `aum`: Monetary (computed)
- `client_segment`: Selection (computed)
- `kyc_status`: Selection
- `risk_profile`: Selection
- `advisor_id`: Many2one (res.users)

### finance.lifecycle
- `partner_id`: Many2one (res.partner)
- `stage`: Selection
- `previous_stage`: Selection
- `changed_date`: Datetime
- `changed_by`: Many2one (res.users)
- `reason`: Selection
- `days_in_stage`: Integer (computed)

### finance.patrimony
- `partner_id`: Many2one (res.partner)
- `date`: Date
- `fixed_income`: Monetary
- `equities`: Monetary
- `funds`: Monetary
- `real_estate`: Monetary
- `alternatives`: Monetary
- `cash`: Monetary
- `total_value`: Monetary (computed)
- `variation_percent`: Float (computed)

### finance.category
- `name`: Char
- `color`: Integer
- `partner_ids`: Many2many (res.partner)

## API Examples

### Python ORM

```python
# Create finance client
client = self.env['res.partner'].create({
    'name': 'John Doe',
    'email': 'john@example.com',
    'is_finance_client': True,
    'advisor_id': self.env.user.id,
})

# Update lifecycle
client.write({
    'finance_lifecycle_state': 'active'
})

# Add patrimony snapshot
self.env['finance.patrimony'].create({
    'partner_id': client.id,
    'date': fields.Date.today(),
    'fixed_income': 50000,
    'equities': 30000,
    'funds': 20000,
})

# Search high-value clients
hnw_clients = self.env['res.partner'].search([
    ('is_finance_client', '=', True),
    ('client_segment', '=', 'high_net_worth'),
])
```

### XML-RPC

```python
import xmlrpc.client

url = 'http://localhost:8069'
db = 'your_database'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search finance clients
clients = models.execute_kw(
    db, uid, password,
    'res.partner', 'search_read',
    [[('is_finance_client', '=', True)]],
    {'fields': ['name', 'aum', 'finance_lifecycle_state']}
)
```

## Troubleshooting

### Common Issues

**Profile ID not generating**:
- Check if sequence exists: `finance.profile`
- Verify sequence configuration in Technical menu

**AUM not updating**:
- Manually trigger: Open client → Finance tab → Refresh AUM
- Check cron job: Settings → Technical → Scheduled Actions

**Advisor can't see clients**:
- Verify user has `Finance Advisor` group
- Check `advisor_id` field on client record
- Review record rules in debug mode

**KYC expiry not working**:
- Check cron is active
- Verify dates are set correctly
- Check system logs for errors

## Development

### Extending Finance Core

To create satellite modules that extend Finance Core:

```python
# In your module's __manifest__.py
{
    'depends': ['finance_core'],
}

# In your models
class YourModel(models.Model):
    _name = 'your.model'
    
    partner_id = fields.Many2one(
        'res.partner',
        domain=[('is_finance_client', '=', True)]
    )
```

### Recommended Satellite Modules

1. **finance_compliance**: Extended suitability and compliance
2. **finance_investments**: Product catalog and positions
3. **finance_billing**: Fee calculation and invoicing
4. **finance_portal**: Client self-service portal
5. **finance_analytics**: BI dashboards and reports

## Support

For issues, questions, or feature requests:
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com/finance-core

## License

LGPL-3

## Credits

**Author**: Your Company  
**Version**: 19.0.1.0.0  
**Last Update**: 2024-11-24

---

**Important**: This is a foundational module. Always backup your database before major updates.
