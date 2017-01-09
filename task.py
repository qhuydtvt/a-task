from mongoengine import *
from datetime import date
import utils

class Task(Document):
    user_id = StringField()
    local_id = StringField()
    name = StringField()
    due_date = DateTimeField()
    color = StringField()
    payment_per_hour = FloatField()
    done = BooleanField()

    def get_json(self):
        return {
            "id": str(self.id),
            "local_id": self.local_id,
            "name" : self.name,
            "due_date": utils.date_from_str(str(self.due_date)).isoformat(),
            "color": self.color,
            "payment_per_hour" : self.payment_per_hour,
            "done" : self.done
        }
