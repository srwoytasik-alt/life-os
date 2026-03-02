from datetime import datetime, timedelta
from database import db
from models.task_model import TaskModel


def check_due_tasks():
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    overdue = TaskModel.query.filter(
        TaskModel.completed == False,
        TaskModel.due_date < today
    ).all()

    due_soon = TaskModel.query.filter(
        TaskModel.completed == False,
        TaskModel.due_date == tomorrow
    ).all()

    if overdue:
        print("\n⚠️ OVERDUE TASKS:")
        for task in overdue:
            print(f"- {task.title} (Due {task.due_date})")

    if due_soon:
        print("\n⏳ TASKS DUE TOMORROW:")
        for task in due_soon:
            print(f"- {task.title} (Due {task.due_date})")

    if not overdue and not due_soon:
        print("\n✅ No urgent tasks at this time.")
        