import csv
from datetime import datetime
from models.task_model import TaskModel
from database import db


def backup_tasks_to_csv():
    tasks = TaskModel.query.all()

    filename = f"task_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "id",
            "title",
            "priority",
            "due_date",
            "domain",
            "completed"
        ])

        for t in tasks:
            writer.writerow([
                t.id,
                t.title,
                t.priority,
                t.due_date,
                t.domain,
                t.completed
            ])

    print(f"✅ Backup created: {filename}")
    