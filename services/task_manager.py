from models.task import Task


class TaskManager:
    def __init__(self, storage):
        self.storage = storage
        self.tasks = self.storage.load()

    # ----------------------------
    # Core CRUD Operations
    # ----------------------------

    def add_task(self, title, priority="Medium", due_date=None, domain="General"):
        if self.tasks:
            new_id = max(task.id for task in self.tasks) + 1
        else:
            new_id = 1

        new_task = Task(
            new_id,
            title,
            priority=priority,
            due_date=due_date,
            domain=domain
        )

        self.tasks.append(new_task)
        self.storage.save(self.tasks)

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]
        self.storage.save(self.tasks)

    def toggle_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                task.toggle()
                break

        self.storage.save(self.tasks)

    def get_all_tasks(self):
        return self.tasks

    # ----------------------------
    # Filtering Logic
    # ----------------------------

    def get_filtered_tasks(self, filter_type="all", sort_type="default"):

        # -------- Filtering --------
        if filter_type == "active":
            filtered = [t for t in self.tasks if not t.completed]

        elif filter_type == "completed":
            filtered = [t for t in self.tasks if t.completed]

        elif filter_type == "overdue":
            filtered = [t for t in self.tasks if t.is_overdue()]

        elif filter_type == "high":
            filtered = [t for t in self.tasks if t.priority in ("High", "Critical")]

        elif filter_type.startswith("domain:"):
            domain_name = filter_type.split(":")[1]
            filtered = [t for t in self.tasks if t.domain == domain_name]

        else:
            filtered = self.tasks

        # -------- Sorting --------
        if sort_type == "due_asc":
            filtered.sort(key=lambda t: t.due_date or "9999-12-31")

        elif sort_type == "due_desc":
            filtered.sort(key=lambda t: t.due_date or "0000-01-01", reverse=True)

        elif sort_type == "priority":
            priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            filtered.sort(key=lambda t: priority_order.get(t.priority, 4))

        elif sort_type == "newest":
            filtered.sort(key=lambda t: t.id, reverse=True)

        elif sort_type == "oldest":
            filtered.sort(key=lambda t: t.id)

        return filtered

    def get_stats(self):
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.completed])
        overdue = len([t for t in self.tasks if t.is_overdue()])
        high_priority = len([t for t in self.tasks if t.priority in ("High", "Critical")])

        domain_counts = {}
        for task in self.tasks:
            domain_counts[task.domain] = domain_counts.get(task.domain, 0) + 1

        return {
            "total": total,
            "completed": completed,
            "overdue": overdue,
            "high_priority": high_priority,
            "domain_counts": domain_counts
        }   
    
    def sort_tasks(self, tasks, sort_by="default"):
        if sort_by == "due":
            return sorted(tasks, key=lambda t: t.due_date or "")
        elif sort_by == "priority":
            priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
            return sorted(tasks, key=lambda t: priority_order.get(t.priority, 5))
        else:
            return tasks 
               