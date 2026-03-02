# models/task_model.py

from database import db
from datetime import date


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    domain = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def is_overdue(self):
        if not self.due_date or self.completed:
            return False
        return self.due_date < date.today()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "domain": self.domain,
            "completed": self.completed
        }   
        
         