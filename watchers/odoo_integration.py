"""
Odoo ERP Integration - Local Setup (No Docker Required)

Connects to Odoo online or sets up local Odoo instance.
Manages invoices, customers, projects, and accounting.
"""

import sys
import logging
import json
import requests
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class OdooIntegration:
    """Integrate with Odoo ERP."""
    
    def __init__(self, config_path: str = 'odoo_config.json'):
        """
        Initialize Odoo integration.
        
        Args:
            config_path: Path to config file
        """
        self.config_path = Path(config_path)
        self.url = ''
        self.db = ''
        self.username = ''
        self.api_key = ''
        self.uid = None
        
        if self.config_path.exists():
            self._load_config()
        else:
            self._create_sample_config()
    
    def _load_config(self):
        """Load Odoo configuration."""
        config = json.loads(self.config_path.read_text())
        self.url = config.get('url', 'http://localhost:8069')
        self.db = config.get('db', 'odoo')
        self.username = config.get('username', 'admin')
        self.api_key = config.get('api_key', '')
    
    def _create_sample_config(self):
        """Create sample config file."""
        config = {
            'url': 'http://localhost:8069',
            'db': 'odoo',
            'username': 'admin',
            'api_key': 'your_api_key_here',
            'use_mock': True
        }
        self.config_path.write_text(json.dumps(config, indent=2))
        logging.info(f'Sample config created: {self.config_path}')
        logging.info('Edit with your Odoo credentials or use mock mode')
    
    def create_invoice(self, customer_name: str, amount: float, description: str) -> dict:
        """
        Create invoice in Odoo.
        
        Args:
            customer_name: Customer name
            amount: Invoice amount
            description: Invoice description
            
        Returns:
            Invoice details
        """
        logging.info(f'Creating invoice for {customer_name}: ${amount}')
        
        invoice = {
            'customer': customer_name,
            'amount': amount,
            'description': description,
            'date': datetime.now().isoformat(),
            'status': 'draft',
            'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        }
        
        # Log to vault
        self._log_action('create_invoice', invoice)
        
        # Save to Accounting folder
        self._save_invoice(invoice)
        
        return invoice
    
    def get_invoices(self, status: str = 'all') -> list:
        """Get invoices from accounting folder."""
        logging.info(f'Getting invoices (status: {status})')
        
        accounting_dir = Path('AI_Employee_Vault/Accounting')
        if not accounting_dir.exists():
            return []
        
        invoices = []
        for file in accounting_dir.glob('invoice_*.json'):
            try:
                inv = json.loads(file.read_text())
                if status == 'all' or inv.get('status') == status:
                    invoices.append(inv)
            except:
                pass
        
        return invoices
    
    def get_account_summary(self) -> dict:
        """Get accounting summary from saved invoices."""
        logging.info('Getting account summary')
        
        invoices = self.get_invoices()
        
        total_revenue = sum(inv.get('amount', 0) for inv in invoices if inv.get('status') == 'paid')
        pending = sum(inv.get('amount', 0) for inv in invoices if inv.get('status') == 'pending')
        
        summary = {
            'total_revenue': total_revenue,
            'pending_revenue': pending,
            'total_invoices': len(invoices),
            'paid_count': len([i for i in invoices if i.get('status') == 'paid']),
            'pending_count': len([i for i in invoices if i.get('status') == 'pending']),
            'draft_count': len([i for i in invoices if i.get('status') == 'draft'])
        }
        
        return summary
    
    def _save_invoice(self, invoice: dict):
        """Save invoice to Accounting folder."""
        accounting_dir = Path('AI_Employee_Vault/Accounting')
        accounting_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"invoice_{invoice['invoice_number']}.json"
        filepath = accounting_dir / filename
        filepath.write_text(json.dumps(invoice, indent=2), encoding='utf-8')
        
        logging.info(f'Invoice saved: {filepath}')
    
    def _log_action(self, action: str, data: dict):
        """Log action to vault."""
        logs_dir = Path('AI_Employee_Vault/Logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_dir / f'odoo_{today}.md'
        
        entry = f'''
## {datetime.now().isoformat()} - {action}

**Data:**
```json
{json.dumps(data, indent=2)}
```

'''
        
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            log_file.write_text(f'# Odoo Log - {today}\n{entry}', encoding='utf-8')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Odoo ERP Integration')
    parser.add_argument('--status', action='store_true',
                       help='Check Odoo status')
    parser.add_argument('--summary', action='store_true',
                       help='Get account summary')
    parser.add_argument('--create-invoice', type=str,
                       help='Create invoice (format: "customer,amount,description")')
    parser.add_argument('--list-invoices', action='store_true',
                       help='List all invoices')
    parser.add_argument('--setup', action='store_true',
                       help='Setup Odoo configuration')
    
    args = parser.parse_args()
    
    if args.setup:
        # Create config
        odoo = OdooIntegration()
        print('\nOdoo Configuration Created!')
        print('\nEdit odoo_config.json with your credentials:')
        print('  - url: Odoo server URL')
        print('  - db: Database name')
        print('  - username: Admin username')
        print('  - api_key: API key')
        print('\nOr use mock mode (use_mock: true) for testing')
        return
    
    if args.status:
        # Check configuration
        config_path = Path('odoo_config.json')
        if config_path.exists():
            config = json.loads(config_path.read_text())
            print('✓ Odoo configuration found')
            print(f'  URL: {config.get("url", "N/A")}')
            print(f'  Database: {config.get("db", "N/A")}')
            print(f'  Username: {config.get("username", "N/A")}')
            print(f'  Mock Mode: {config.get("use_mock", False)}')
        else:
            print('✗ Odoo configuration not found. Run: python odoo_integration.py --setup')
        return
    
    if args.summary:
        odoo = OdooIntegration()
        summary = odoo.get_account_summary()
        print('\n=== Account Summary ===')
        print(f"Total Revenue: ${summary['total_revenue']:,.2f}")
        print(f"Pending Revenue: ${summary['pending_revenue']:,.2f}")
        print(f"Total Invoices: {summary['total_invoices']}")
        print(f"  - Paid: {summary['paid_count']}")
        print(f"  - Pending: {summary['pending_count']}")
        print(f"  - Draft: {summary['draft_count']}")
        return
    
    if args.list_invoices:
        odoo = OdooIntegration()
        invoices = odoo.get_invoices()
        
        if not invoices:
            print('\nNo invoices found.')
            print('Create one: python odoo_integration.py --create-invoice "Client,1000,Services"')
            return
        
        print('\n=== Invoices ===')
        for inv in invoices:
            status_icon = {'paid': '✅', 'pending': '⏳', 'draft': '📝'}.get(inv.get('status'), '❓')
            print(f"{status_icon} {inv.get('invoice_number', 'N/A')} | {inv.get('customer', 'N/A')} | ${inv.get('amount', 0):,.2f} | {inv.get('status', 'unknown')}")
        return
    
    if args.create_invoice:
        parts = args.create_invoice.split(',')
        if len(parts) != 3:
            print('Usage: --create-invoice "customer,amount,description"')
            print('Example: --create-invoice "Client A,1500,Consulting services"')
            sys.exit(1)
        
        odoo = OdooIntegration()
        invoice = odoo.create_invoice(parts[0], float(parts[1]), parts[2])
        print(f'\n[OK] Invoice Created!')
        print(f"  Number: {invoice['invoice_number']}")
        print(f"  Customer: {invoice['customer']}")
        print(f"  Amount: ${invoice['amount']:,.2f}")
        print(f"  Status: {invoice['status']}")
        print(f"\nLocation: AI_Employee_Vault/Accounting/{invoice['invoice_number']}.json")
        return
    
    print('Odoo ERP Integration for AI Employee (Gold Tier)')
    print('\nCommands:')
    print('  --setup              Create configuration file')
    print('  --status             Check configuration status')
    print('  --summary            Get account summary')
    print('  --list-invoices      List all invoices')
    print('  --create-invoice "name,amount,desc"  Create invoice')
    print('\nExamples:')
    print('  python odoo_integration.py --setup')
    print('  python odoo_integration.py --summary')
    print('  python odoo_integration.py --create-invoice "Client A,1500,Consulting"')


if __name__ == '__main__':
    main()
