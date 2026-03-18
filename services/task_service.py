# services/task_service.py

from datetime import date, datetime, timedelta


class TaskService:
    def __init__(self, repo):
        self.repo = repo

    # -------------------------
    # Core CRUD
    # -------------------------

    def get_all(self):
        return self.repo.get_all()

    def add_task(self, title, priority, due_date, domain):
        self.repo.add(title, priority, due_date, domain)

    def toggle(self, task_id):
        self.repo.toggle(task_id)

    def delete(self, task_id):
        self.repo.delete(task_id)

    # -------------------------
    # Smart Scoring Engine
    # -------------------------

    def calculate_score(self, task):
        from models.financial_model import FinancialRecord
        from database import db
        
        score = 0
        today = date.today()

        # Priority Weight
        if task.priority == "Critical":
            score += 5
        elif task.priority == "High":
            score += 3
        
        # Financial urgency injection - wrap in try/except in case table doesn't exist
        try:
            pending_bills = FinancialRecord.query.filter_by(status="Pending", category="Bill").all()
            for bill in pending_bills:
                if bill.due_date and bill.due_date <= today:
                    score += 3
        except:
            # FinancialRecord table might not exist, just skip
            pass

        # Due Date Logic
        if task.due_date:
            # Convert string to date if needed
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

        # Incomplete tasks matter more
        if not task.completed:
            score += 1

        return score

    def get_ranked_tasks(self):
        tasks = self.repo.get_all()

        # Build scored tuples
        scored = [(task, self.calculate_score(task)) for task in tasks]

        # Sort logic:
        # 1️⃣ Incomplete first (False < True)
        # 2️⃣ Higher score first
        scored.sort(
            key=lambda x: (x[0].completed, -x[1])
        )

        return scored

    def get_stability_index(self):
        tasks = self.repo.get_all()
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

        # Prevent negative
        if score < 0:
            score = 0

        return score

    def get_top_critical(self):
        tasks = [
            t for t in self.repo.get_all()
            if t.priority == "Critical" and not t.completed
        ]

        scored = [(task, self.calculate_score(task)) for task in tasks]
        scored.sort(key=lambda x: -x[1])
        return scored[:5]

    def get_suggestions(self):
        ranked = self.get_ranked_tasks()
        # ranked is now list of (task, score)
        return [task for task, score in ranked if not task.completed][:5]

    # -------------------------
    # Filtering
    # -------------------------

    def get_filtered_tasks(self, filter_type="all"):
        tasks = self.repo.get_all()
        today = date.today()

        if filter_type == "active":
            return [t for t in tasks if not t.completed]

        elif filter_type == "completed":
            return [t for t in tasks if t.completed]

        elif filter_type == "overdue":
            return [t for t in tasks if t.due_date and 
                   (t.due_date if isinstance(t.due_date, date) 
                    else datetime.strptime(t.due_date, "%Y-%m-%d").date()) < today 
                    and not t.completed]

        elif filter_type == "high":
            return [t for t in tasks if t.priority in ["High", "Critical"]]

        elif filter_type.startswith("domain:"):
            domain_name = filter_type.split(":")[1]
            return [t for t in tasks if t.domain == domain_name]

        return tasks
    
    def get_todays_mission(self):
        ranked = self.get_ranked_tasks()
        return [t for t, score in ranked if not t.completed][:3]