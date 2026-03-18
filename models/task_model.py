# models/task_model.py

from database import db
from datetime import date

class TaskModel(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    due_date = db.Column(db.Date, nullable=True)
    domain = db.Column(db.String(50), default='General')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'domain': self.domain,
            'completed': self.completed
        }