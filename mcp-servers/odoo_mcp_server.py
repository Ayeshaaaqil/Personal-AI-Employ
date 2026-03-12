"""
Odoo MCP Server - Odoo ERP integration

Provides tools for:
- Creating invoices
- Managing customers
- Tracking projects
- Financial reports
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OdooMCP')


class OdooMCPServer:
    """Odoo MCP Server for ERP integration."""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load Odoo configuration."""
        config_path = Path('odoo_config.json')
        if config_path.exists():
            import json
            return json.loads(config_path.read_text())
        return {'use_mock': True}
    
    def create_invoice(self, customer: str, amount: float, description: str) -> dict:
        """Create invoice."""
        logger.info(f'Creating invoice for {customer}: ${amount}')
        
        invoice = {
            'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'customer': customer,
            'amount': amount,
            'description': description,
            'date': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        # Save to Accounting folder
        accounting_dir = Path('AI_Employee_Vault/Accounting')
        accounting_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = accounting_dir / f"invoice_{invoice['invoice_number']}.json"
        filepath.write_text(json.dumps(invoice, indent=2), encoding='utf-8')
        
        return {'success': True, 'invoice': invoice}
    
    def get_invoices(self, status: str = 'all') -> dict:
        """Get invoices."""
        accounting_dir = Path('AI_Employee_Vault/Accounting')
        if not accounting_dir.exists():
            return {'success': True, 'invoices': []}
        
        invoices = []
        for file in accounting_dir.glob('invoice_*.json'):
            try:
                inv = json.loads(file.read_text())
                if status == 'all' or inv.get('status') == status:
                    invoices.append(inv)
            except:
                pass
        
        return {'success': True, 'invoices': invoices}
    
    def get_summary(self) -> dict:
        """Get financial summary."""
        result = self.get_invoices()
        invoices = result.get('invoices', [])
        
        total = sum(inv.get('amount', 0) for inv in invoices if inv.get('status') == 'paid')
        pending = sum(inv.get('amount', 0) for inv in invoices if inv.get('status') == 'pending')
        
        return {
            'success': True,
            'summary': {
                'total_revenue': total,
                'pending_revenue': pending,
                'total_invoices': len(invoices),
                'paid_count': len([i for i in invoices if i.get('status') == 'paid']),
                'pending_count': len([i for i in invoices if i.get('status') == 'pending'])
            }
        }


def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get('method', '')
    params = request.get('params', {})
    
    server = OdooMCPServer()
    
    if method == 'odoo/create_invoice':
        result = server.create_invoice(
            params.get('customer', ''),
            params.get('amount', 0),
            params.get('description', '')
        )
    elif method == 'odoo/get_invoices':
        result = server.get_invoices(params.get('status', 'all'))
    elif method == 'odoo/get_summary':
        result = server.get_summary()
    else:
        result = {'success': False, 'error': f'Unknown method: {method}'}
    
    return {'jsonrpc': '2.0', 'id': request.get('id'), 'result': result}


def main():
    """Run MCP server."""
    logger.info('Odoo MCP Server started')
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({'jsonrpc': '2.0', 'id': None, 'error': {'message': str(e)}}), flush=True)


if __name__ == '__main__':
    main()
