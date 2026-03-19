# services/task_service.py

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from database import db
from models.task_model import TaskModel

class TaskService:
    def __init__(self, repo):
        self.repo = repo

    # -------------------------
    # Core CRUD
    # -------------------------

    def get_all(self, include_archived=False):
        if include_archived:
            return self.repo.get_all()
        return [t for t in self.repo.get_all() if not t.archived]

    def add_task(self, title, priority, due_date, domain, repeat=None):
        self.repo.add(title, priority, due_date, domain, repeat)

    def toggle(self, task_id):
        task = self.repo.get_by_id(task_id)
        if not task:
            return None
        
        # Toggle completion status
        task.completed = not task.completed
        
        # If completing a recurring task, create the next instance
        if task.completed and task.repeat:
            next_due = self.calculate_next_due_date(task)
            if next_due:
                # Check if next instance already exists (duplicate protection)
                existing = TaskModel.query.filter_by(
                    title=task.title,
                    due_date=next_due,
                    repeat=task.repeat,
                    archived=False
                ).first()
                
                if not existing:
                    new_task = TaskModel(
                        title=task.title,
                        priority=task.priority,
                        due_date=next_due,
                        domain=task.domain,
                        repeat=task.repeat,
                        completed=False,
                        archived=False
                    )
                    db.session.add(new_task)
                    print(f"✅ Created next recurring task: {task.title} for {next_due}")
        
        db.session.commit()
        return task

    def soft_delete(self, task_id):
        """Archive a task instead of deleting it"""
        task = self.repo.get_by_id(task_id)
        if task:
            task.archived = True
            db.session.commit()
            print(f"✅ Task {task_id} archived")

    def restore(self, task_id):
        """Restore an archived task"""
        task = self.repo.get_by_id(task_id)
        if task:
            task.archived = False
            db.session.commit()
            print(f"✅ Task {task_id} restored")

    def permanent_delete(self, task_id):
        """Permanently delete a task"""
        self.repo.delete(task_id)

    def get_archived_tasks(self):
        """Get all archived tasks"""
        return [t for t in self.repo.get_all() if t.archived]

    # -------------------------
    # Recurring Task Logic
    # -------------------------

    def calculate_next_due_date(self, task):
        """Calculate the next due date based on repeat pattern"""
        if not task.due_date or not task.repeat:
            return None
        
        if task.repeat == 'daily':
            return task.due_date + timedelta(days=1)
        elif task.repeat == 'weekly':
            return task.due_date + timedelta(weeks=1)
        elif task.repeat == 'monthly':
            # Handle month-end dates correctly
            try:
                # Try same day next month
                if task.due_date.month == 12:
                    return task.due_date.replace(year=task.due_date.year + 1, month=1)
                else:
                    return task.due_date.replace(month=task.due_date.month + 1)
            except ValueError:
                # Handle dates like Jan 31 -> Feb 28 (or 29 in leap year)
                # Get last day of next month
                if task.due_date.month == 12:
                    next_month = date(task.due_date.year + 1, 2, 1) - timedelta(days=1)
                else:
                    next_month = date(task.due_date.year, task.due_date.month + 2, 1) - timedelta(days=1)
                return next_month
        elif task.repeat == 'yearly':
            return task.due_date.replace(year=task.due_date.year + 1)
        else:
            return None

    def get_next_occurrence(self, task):
        """Get the next occurrence date for display"""
        if not task.repeat or task.completed:
            return None
        return self.calculate_next_due_date(task)

    # -------------------------
    # Task Categorization
    # -------------------------

    def get_tasks_due_today(self):
        """Get tasks due today"""
        today = date.today()
        return [t for t in self.get_all() 
                if t.due_date and t.due_date == today and not t.completed]

    def get_overdue_tasks(self):
        """Get overdue tasks"""
        today = date.today()
        return [t for t in self.get_all() 
                if t.due_date and t.due_date < today and not t.completed]

    def get_upcoming_tasks(self, days=7):
        """Get tasks due in the next X days"""
        today = date.today()
        cutoff = today + timedelta(days=days)
        return [t for t in self.get_all() 
                if t.due_date and today <= t.due_date <= cutoff and not t.completed]

    # -------------------------
    # Smart Scoring Engine
    # -------------------------

    def calculate_score(self, task):
        from models.financial_model import FinancialRecord
        
        if task.completed or task.archived:
            return 0
            
        score = 0
        today = date.today()

        # Priority Weight
        if task.priority == "Critical":
            score += 5
        elif task.priority == "High":
            score += 3
        
        # Financial urgency injection
        try:
            pending_bills = FinancialRecord.query.filter_by(status="Pending", category="Bill").all()
            for bill in pending_bills:
                if bill.due_date and bill.due_date <= today:
                    score += 3
        except:
            pass

        # Due Date Logic
        if task.due_date:
            if isinstance(task.due_date, str):
                try:
                    task_due = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                except:
                    task_due = today
            else:
                task_due = task.due_date
                
            if task_due < today:
                score += 6  # Overdue
            elif task_due == today:
                score += 4
            elif task_due <= today + timedelta(days=3):
                score += 2

        # Recurring tasks get a small boost
        if task.repeat:
            score += 1

        return score

    def get_ranked_tasks(self):
        tasks = self.get_all()
        scored = [(task, self.calculate_score(task)) for task in tasks]
        scored.sort(key=lambda x: (x[0].completed, -x[1]))
        return scored

    def get_stability_index(self):
        tasks = self.get_all()
        score = 100

        for task in tasks:
            if not task.completed:
                if task.priority == "Critical":
                    score -= 5
                elif task.priority == "High":
                    score -= 3
                elif task.priority == "Medium":
                    score -= 2
                elif task.priority == "Low":
                    score -= 1

        if score < 0:
            score = 0
        return score

    def get_suggestions(self):
        ranked = self.get_ranked_tasks()
        return [task for task, score in ranked if not task.completed][:5]

    # -------------------------
    # Filtering
    # -------------------------

    def get_filtered_tasks(self, filter_type="all"):
        """Get tasks based on filter type"""
        query = TaskModel.query.filter_by(archived=False)
        today = date.today()

        if filter_type == "today":
            query = query.filter(TaskModel.due_date == today)
        elif filter_type == "overdue":
            query = query.filter(TaskModel.due_date < today, TaskModel.completed == False)
        elif filter_type == "upcoming":
            query = query.filter(TaskModel.due_date > today)
        elif filter_type == "active":
            query = query.filter_by(completed=False)
        elif filter_type == "completed":
            query = query.filter_by(completed=True)
        elif filter_type == "high":
            query = query.filter(TaskModel.priority.in_(["High", "Critical"]))
        elif filter_type.startswith("domain:"):
            domain_name = filter_type.split(":")[1]
            query = query.filter_by(domain=domain_name)
        elif filter_type == "recurring":
            query = query.filter(TaskModel.repeat.isnot(None))
        
        return query.order_by(TaskModel.due_date.asc(), TaskModel.priority.desc()).all()
    
    def get_todays_mission(self):
        ranked = self.get_ranked_tasks()
        return [t for t, score in ranked if not t.completed][:3]