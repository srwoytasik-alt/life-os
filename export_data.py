import csv
from app import create_app
from models.task_model import TaskModel

app = create_app()

with app.app_context():
    tasks = TaskModel.query.all()

    print(f"Found {len(tasks)} tasks...")

    with open("tasks_backup.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "id",
            "title",
            "priority",
            "domain",
            "due_date",
            "completed"
        ])

        for t in tasks:
            writer.writerow([
                t.id,
                getattr(t, "title", None),
                getattr(t, "priority", None),
                getattr(t, "domain", None),
                getattr(t, "due_date", None),
                getattr(t, "completed", None)
            ])

print("✅ Export complete → tasks_backup.csv")