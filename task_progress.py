from mongoengine import *
from task import *
from datetime import datetime

parser = reqparse.RequestParser()

parser.add_argument('token', type=str, help='Token of noter', location="headers")

parser.add_argument("task_id", type=str, help="Id of task")
parser.add_argument("date", type=str, help="Date of progress")
parser.add_argument("duration_in_secs", type=int, help="Duration of task progress")


class TaskProgressListRes(Resource):
    def get(self):
        args = parser.parse_args()
        user = user_from_token(args["token"])

        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        return [task_progress.get_json() for task_progress in TaskProgress.objects() if task_progress.get_user_id()==user.id], 200

    def post(self):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task_id = args["task_id"]
        date = utils.date_from_iso8601(args["date"])
        duration_in_secs = args["duration_in_secs"]

        task = Task.objects().with_id(task_id)
        if task is None:
            return {"code": 0, "message": "Task not found"}, 404
        elif task.user_id != user.id:
            return {"code": 0, "message": "This task is not yours, fuck off"}, 401
        else:
            task_progress_id = add_task_progress(
                task_id=task_id,
                date=date,
                duration_in_secs=duration_in_secs)
            return get_task_progress(task_progress_id).get_json(), 200


class TaskProgressRes(Resource):
    def get(self, task_progress_id):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task_progress = TaskProgress.objects().with_id(task_progress_id)
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        elif task_progress.get_user_id() != user.id:
            return {"code": 0, "message": "This task is not yours, fuck off"}, 401
        else:
            return task_progress.get_json(), 200

    def put(self, task_progress_id):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task_progress = TaskProgress.objects().with_id(task_progress_id)
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        elif task_progress.get_user_id() != user.id:
            return {"code": 0, "message": "This task is not yours, fuck off"}, 401
        else:
            args = parser.parse_args()
            date = utils.date_from_iso8601(args["date"])
            duration_in_secs = args["duration_in_secs"]
            task_progress.update(set__date=date, set__duration_in_secs=duration_in_secs)
            return TaskProgress.objects().with_id(task_progress_id).get_json(), 200

    def delete(self, task_progress_id):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task_progress = TaskProgress.objects().with_id(task_progress_id)
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        elif task_progress.get_user_id() != user.id:
            return {"code": 0, "message": "This task is not yours, fuck off"}, 401
        else:
            task_progress.delete()
            return {"code": 1, "message": "Task progress deleted"}, 200


class TaskProgress(Document):
    user_id = ObjectIdField()
    task_id = ObjectIdField()
    date = DateTimeField()
    duration_in_secs = LongField()

    def get_json(self):
        return {
            "id": str(self.id),
            "task": task_from_id(self.task_id).get_json(),
            "date": utils.toISO8601(self.date),
            "duration_in_secs": self.duration_in_secs
        }

    def get_user_id(self):
        # print("getting user id...")
        # print(self.task_id)
        task = task_from_id(self.task_id)
        if task is not None:
            return task.user_id
        else:
            return None


def add_task_progress(task_id, date, duration_in_secs):
    task_progress = TaskProgress(task_id=task_id, date=date, duration_in_secs=duration_in_secs)
    task_progress.save()
    return task_progress.id


def get_task_progress(id):
    return TaskProgress.objects().with_id(id)
