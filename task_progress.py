from mongoengine import *
from task import *
from datetime import datetime
from flask_jwt import jwt_required

parser = reqparse.RequestParser()

parser.add_argument('token', type=str, help='Token of noter', location="headers")

parser.add_argument("task_id", type=str, help="Id of task")
parser.add_argument("date", type=str, help="Date of progress")
parser.add_argument("duration_in_secs", type=int, help="Duration of task progress")
parser.add_argument("local_id", type=int, help="Local id of task progress")

class TaskProgressListRes(Resource):
    @jwt_required()
    def get(self):
        args = parser.parse_args()
        user = current_identity.user()
        task_progress_list = TaskProgress.objects(user=user)

        return [task_progress.get_json() for task_progress in task_progress_list], 200

    @jwt_required()
    def post(self):
        args = parser.parse_args()

        user = current_identity.user()

        task_id = args["task_id"]
        date = utils.date_from_iso8601(args["date"])
        duration_in_secs = args["duration_in_secs"]

        task = Task.objects(local_id=task_id, user=user).first()
        if task is None:
            return {"code": 0, "message": "Task not found"}, 404
        else:
            task_progress_id = add_task_progress(
                user=user,
                task=task,
                date=date,
                duration_in_secs=duration_in_secs)
            return get_task_progress(task_progress_id).get_json(), 200

class TaskProgressRes(Resource):

    @jwt_required()
    def get(self, task_progress_id):
        args = parser.parse_args()
        user = current_identity.user()

        task_progress = TaskProgress.objects(id=task_progress_id, user=user).first()
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        else:
            return task_progress.get_json(), 200

    @jwt_required()
    def put(self, task_progress_id):
        user = current_identity.user()

        task_progress = TaskProgress.objects(id=task_progress_id, user=user).first()
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        else:
            args = parser.parse_args()
            date = utils.date_from_iso8601(args["date"])
            duration_in_secs = args["duration_in_secs"]
            task_progress.update(set__date=date, set__duration_in_secs=duration_in_secs)
            return TaskProgress.objects().with_id(task_progress_id).get_json(), 200

    @jwt_required()
    def delete(self, task_progress_id):
        user = current_identity.user()

        task_progress = TaskProgress.objects(id=task_progress_id, user=user).first()
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        else:
            task_progress.delete()
            return {"code": 1, "message": "Task progress deleted"}, 200


class TaskProgress(Document):
    user = ReferenceField("User")
    task = ReferenceField("Task")
    date = DateTimeField()
    duration_in_secs = LongField()

    def get_json(self):
        return {
            "id": str(self.id),
            "task": self.task.get_json(),
            "date": utils.toISO8601(self.date),
            "duration_in_secs": self.duration_in_secs
        }


def add_task_progress(user, task, date, duration_in_secs):
    task_progress = TaskProgress(user=user, task=task, date=date, duration_in_secs=duration_in_secs)
    task_progress.save()
    return task_progress.id


def get_task_progress(id):
    return TaskProgress.objects().with_id(id)
