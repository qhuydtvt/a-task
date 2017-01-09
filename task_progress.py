from mongoengine import *
from task import *


class TaskProgress(Document):
    task = EmbeddedDocumentField("Task")
    date = DateTimeField()
    duration_in_secs = LongField()