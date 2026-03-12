"""
Audit MCP Server - Comprehensive audit logging

Provides tools for:
- Logging actions
- Querying audit trail
- Generating reports
- Error tracking
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AuditMCP')


class AuditMCPServer:
    """Audit MCP Server for logging and compliance."""
    
    def __init__(self):
        self.vault_path = Path('AI_Employee_Vault')
        self.audit_dir = self.vault_path / 'Audit'
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.audit_file = self.audit_dir / f'{self.today}.jsonl'
    
    def log(self, event_type: str, actor: str, action: str, **kwargs) -> dict:
        """Log an audit event."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'actor': actor,
            'action': action,
            **kwargs
        }
        
        # Write to audit file
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        
        logger.info(f"[{event_type}] {actor} -> {action}")
        
        return {'success': True, 'entry_id': entry['timestamp']}
    
    def query(self, filters: dict = None) -> dict:
        """Query audit trail."""
        if not self.audit_file.exists():
            return {'success': True, 'entries': []}
        
        entries = []
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    
                    # Apply filters
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if entry.get(key) != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    entries.append(entry)
                except:
                    pass
        
        return {'success': True, 'entries': entries, 'count': len(entries)}
    
    def generate_report(self, date: str = None) -> dict:
        """Generate audit report."""
        if not date:
            date = self.today
        
        result = self.query({'date': date})
        entries = result.get('entries', [])
        
        # Aggregate stats
        stats = {
            'total': len(entries),
            'by_type': {},
            'by_actor': {},
            'errors': []
        }
        
        for entry in entries:
            event_type = entry.get('event_type', 'unknown')
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1
            
            actor = entry.get('actor', 'unknown')
            stats['by_actor'][actor] = stats['by_actor'].get(actor, 0) + 1
            
            if entry.get('result') == 'failed':
                stats['errors'].append(entry)
        
        return {'success': True, 'report': {'date': date, 'stats': stats}}


def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get('method', '')
    params = request.get('params', {})
    
    server = AuditMCPServer()
    
    if method == 'audit/log':
        result = server.log(
            event_type=params.get('event_type', 'action'),
            actor=params.get('actor', 'unknown'),
            action=params.get('action', ''),
            **params.get('extra', {})
        )
    elif method == 'audit/query':
        result = server.query(params.get('filters'))
    elif method == 'audit/generate_report':
        result = server.generate_report(params.get('date'))
    else:
        result = {'success': False, 'error': f'Unknown method: {method}'}
    
    return {'jsonrpc': '2.0', 'id': request.get('id'), 'result': result}


def main():
    """Run MCP server."""
    logger.info('Audit MCP Server started')
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({'jsonrpc': '2.0', 'id': None, 'error': {'message': str(e)}}), flush=True)


if __name__ == '__main__':
    main()
