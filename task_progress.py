from mongoengine import *
from task import *
from datetime import datetime


class TaskProgress(Document):
    task = Document("Task")
    date = DateTimeField()
    duration_in_secs = LongField()

    def get_json(self):
        return {
            "id": str(self.id),
            "task": self.task.get_json(),
            "date": utils.date_from_str(str(self.date)).isoformat(),
            "duration_in_secs": self.duration_in_secs
        }