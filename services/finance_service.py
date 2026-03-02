import csv
from datetime import datetime
from models.financial_model import FinancialRecord
from database import db


class FinanceService:

    def import_csv(self, filepath):
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                record = FinancialRecord(
                    name=row["Task Name"],
                    amount=float(row["Amount"]),
                    due_date=datetime.strptime(row["Due Date"], "%Y-%m-%d").date(),
                    status=row["Status"],
                    category=row["Category"]
                )

                db.session.add(record)

        db.session.commit()

    def get_all(self):
        return FinancialRecord.query.all()

    def get_pending_bills(self):
        return FinancialRecord.query.filter_by(status="Pending", category="Bill").all()
    