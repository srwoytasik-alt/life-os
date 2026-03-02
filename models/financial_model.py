from database import db


class FinancialRecord(db.Model):
    __tablename__ = "financial_records"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # Pending, Paid, Received
    category = db.Column(db.String(50), nullable=False)  # Bill, Income, Goal

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "due_date": str(self.due_date) if self.due_date else None,
            "status": self.status,
            "category": self.category
        }
        