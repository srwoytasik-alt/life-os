# backup_db.py

import shutil
from datetime import datetime
import os

def backup_sqlite():
    source = 'instance/lifeos.db'
    if os.path.exists(source):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backups/lifeos_backup_{timestamp}.db'
        
        # Create backups directory if it doesn't exist
        os.makedirs('backups', exist_ok=True)
        
        shutil.copy2(source, backup_file)
        print(f"✅ Database backed up to {backup_file}")
    else:
        print("❌ Database file not found")

if __name__ == "__main__":
    backup_sqlite()