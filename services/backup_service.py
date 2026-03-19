# services/backup_service.py

import csv
import os
import json
from datetime import datetime
from models.task_model import TaskModel
from database import db


def backup_tasks_to_csv():
    tasks = TaskModel.query.all()

    # Create backups directory if it doesn't exist
    os.makedirs('backups', exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backups/lifeos_backup_{timestamp}.csv"

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
                t.created_at
            ])

    # Save last backup timestamp
    save_last_backup_time()
    
    print(f"✅ Backup created: {filename}")
    return filename


def save_last_backup_time():
    """Save the current time as the last backup timestamp"""
    backup_info = {
        'last_backup': datetime.now().isoformat(),
        'last_backup_readable': datetime.now().strftime('%B %d, %I:%M %p')
    }
    
    with open('backups/last_backup.json', 'w') as f:
        json.dump(backup_info, f)


def get_last_backup_time():
    """Get the last backup timestamp if it exists"""
    try:
        with open('backups/last_backup.json', 'r') as f:
            data = json.load(f)
            return data.get('last_backup_readable', 'Never')
    except FileNotFoundError:
        return 'Never'