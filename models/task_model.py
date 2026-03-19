# models/task_model.py

from database import db
from datetime import date
from dateutil.relativedelta import relativedelta

class TaskModel(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    due_date = db.Column(db.Date, nullable=True)
    domain = db.Column(db.String(50), default='General')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # New fields for recurring tasks and archiving
    repeat = db.Column(db.String(20), nullable=True)  # daily, weekly, monthly, yearly
    archived = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f'<Task {self.id}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'domain': self.domain,
            'completed': self.completed,
            'repeat': self.repeat,
            'archived': self.archived,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_next_due_date(self):
        """Calculate the next due date based on repeat pattern"""
        if not self.due_date or not self.repeat:
            return None
        
        if self.repeat == 'daily':
            return self.due_date + relativedelta(days=1)
        elif self.repeat == 'weekly':
            return self.due_date + relativedelta(weeks=1)
        elif self.repeat == 'monthly':
            return self.due_date + relativedelta(months=1)
        elif self.repeat == 'yearly':
            return self.due_date + relativedelta(years=1)
        else:
            return None
        