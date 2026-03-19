# repositories/sql_repository.py

from models.task_model import TaskModel
from database import db
from datetime import datetime


class SQLTaskRepository:

    def get_all(self):
        return TaskModel.query.all()
    
    def get_by_id(self, task_id):
        return TaskModel.query.get(task_id)

    def add(self, title, priority, due_date, domain, repeat=None):
        parsed_date = None
        if due_date:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()

        task = TaskModel(
            title=title,
            priority=priority,
            due_date=parsed_date,
            domain=domain,
            completed=False,
            repeat=repeat,
            archived=False  # Explicitly set archived to False
        )

        db.session.add(task)
        db.session.commit()
        return task

    def toggle(self, task_id):
        task = TaskModel.query.get(task_id)
        if task:
            task.completed = not task.completed
            db.session.commit()
        return task

    def delete(self, task_id):
        task = TaskModel.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()