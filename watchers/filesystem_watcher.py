"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors a designated "Inbox" folder for new files. When a file
is created, it copies it to Needs_Action and creates a metadata file.

Perfect for Bronze tier - no external API dependencies required.
"""

import time
import logging
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the drop folder."""
    
    def __init__(self, vault_path: str, inbox_path: str):
        """
        Initialize the handler.
        
        Args:
            vault_path: Path to the Obsidian vault
            inbox_path: Path to the inbox/drop folder
        """
        self.vault_path = Path(vault_path)
        self.inbox_path = Path(inbox_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash to avoid duplicates
        self.processed_hashes = set()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip hidden files and temporary files
        if source.name.startswith('.') or source.suffix == '.tmp':
            return
        
        self.logger.info(f'New file detected: {source.name}')
        self.process_file(source)
    
    def process_file(self, source: Path):
        """
        Process a new file: copy to Needs_Action and create metadata.
        
        Args:
            source: Path to the source file
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest_name = f'FILE_{timestamp}_{source.name}'
            dest = self.needs_action / dest_name
            
            # Copy the file
            shutil.copy2(source, dest)
            self.logger.info(f'Copied to: {dest}')
            
            # Create metadata file
            self.create_metadata(source, dest)
            
        except Exception as e:
            self.logger.error(f'Error processing file {source.name}: {e}')
    
    def create_metadata(self, source: Path, dest: Path):
        """
        Create a metadata markdown file for the dropped file.
        
        Args:
            source: Path to the original file
            dest: Path to the copied file
        """
        meta_path = dest.with_suffix('.md')
        
        # Get file info
        file_size = source.stat().st_size
        file_hash = self.get_file_hash(source)
        
        content = f'''---
type: file_drop
original_name: {source.name}
size: {file_size}
size_human: {self.format_size(file_size)}
hash: {file_hash}
dropped: {datetime.now().isoformat()}
status: pending
---

# File Dropped for Processing

**Original File:** `{source.name}`

**Size:** {self.format_size(file_size)}

**Location:** `{dest.name}`

## Suggested Actions

- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to Done

## Notes

_Add notes here after reviewing the file._

'''
        meta_path.write_text(content)
        self.logger.info(f'Created metadata: {meta_path.name}')
    
    def get_file_hash(self, filepath: Path) -> str:
        """Get MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.2f} TB'


class FileSystemWatcher(BaseWatcher):
    """
    File system watcher using watchdog for efficient file monitoring.
    
    This watcher monitors an Inbox folder and creates action files when
    new files are dropped.
    """
    
    def __init__(self, vault_path: str, inbox_path: str = None):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            inbox_path: Path to the inbox folder (default: vault/Inbox)
        """
        # Initialize with a dummy check_interval since we use event-driven
        super().__init__(vault_path, check_interval=1)
        
        self.inbox_path = Path(inbox_path) if inbox_path else self.vault_path / 'Inbox'
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        self.handler = DropFolderHandler(str(self.vault_path), str(self.inbox_path))
        self.observer = None
    
    def check_for_updates(self) -> list:
        """
        This method is not used in event-driven mode.
        
        Returns:
            list: Empty list (we use event-driven notifications)
        """
        return []
    
    def create_action_file(self, item) -> Path:
        """
        This method is not used in event-driven mode.
        
        Returns:
            Path: None
        """
        return None
    
    def run(self):
        """
        Run the file system watcher using watchdog observer.
        
        This overrides the base class run method to use event-driven
        monitoring instead of polling.
        """
        self.logger.info(f'Starting FileSystemWatcher')
        self.logger.info(f'Watching folder: {self.inbox_path}')
        
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.inbox_path), recursive=False)
        self.observer.start()
        self.logger.info('File watcher started. Drop files in the Inbox folder.')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('File watcher stopped by user')
            self.observer.stop()
        
        self.observer.join()


if __name__ == '__main__':
    import sys
    
    # Default vault path
    vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
    # Allow custom vault path via command line
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    watcher = FileSystemWatcher(str(vault_path))
    watcher.run()
