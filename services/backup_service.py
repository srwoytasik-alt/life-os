# services/backup_service.py

import csv
import os
import json
from datetime import datetime
from models.task_model import TaskModel
from database import db

BACKUP_DIR = 'backups'

def backup_tasks_to_csv():
    """Create a CSV backup of all tasks"""
    tasks = TaskModel.query.all()

    # Create backups directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backups/tasks_backup_{timestamp}.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "id",
            "title",
            "priority",
            "due_date",
            "domain",
            "completed",
            "repeat",
            "archived",
            "created_at"
        ])

        for t in tasks:
            writer.writerow([
                t.id,
                t.title,
                t.priority,
                t.due_date,
                t.domain,
                t.completed,
                t.repeat,
                t.archived,
                t.created_at
            ])

    print(f"✅ Backup created: {filename}")
    return filename


def get_last_backup_time():
    """Get the most recent backup timestamp from file system"""
    if not os.path.exists(BACKUP_DIR):
        return None
    
    # Look for backup files
    files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('tasks_backup_') and f.endswith('.csv')]
    if not files:
        return None
    
    # Get the most recent file by modification time
    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)))
    file_path = os.path.join(BACKUP_DIR, latest)
    
    # Try to extract timestamp from filename (tasks_backup_20260318_143022.csv)
    try:
        # Format: tasks_backup_20260318_143022.csv
        ts_str = latest.replace('tasks_backup_', '').replace('.csv', '')
        return datetime.strptime(ts_str, '%Y%m%d_%H%M%S')
    except:
        # Fall back to file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))