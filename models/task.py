from datetime import date
class Task:
    def __init__(
        self,
        task_id,
        title,
        priority="Medium",
        due_date=None,
        domain="General",
        completed=False
    ):
        self.id = task_id
        self.title = title
        self.priority = priority
        self.due_date = due_date
        self.domain = domain
        self.completed = completed

    def toggle(self):
        self.completed = not self.completed

    def is_overdue(self):
        if self.due_date and not self.completed:
            return date.fromisoformat(self.due_date) < date.today()
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date,
            "domain": self.domain,
            "completed": self.completed
        }
        