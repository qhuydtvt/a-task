from flask import Flask
from datetime import date
from mongoengine import  *
from flask_restful import Api, reqparse, Resource, marshal, marshal_with, fields
import mlab
from task import Task
from task_progress import TaskProgress
import utils
import json

app = Flask(__name__)
api = Api(app)
mlab.connect()

parser = reqparse.RequestParser()
parser.add_argument("local_id", type=str, help="Local id of task")
parser.add_argument("name", type=str, help="Name of task")
parser.add_argument("due_date", type=str, help="Due date of task")
parser.add_argument("color", type=str, help="Color of task")
parser.add_argument("payment_per_hour", type=float, help="Payment rate of task")
parser.add_argument("done", type=bool, help="Status of task")

parser.add_argument("task_id", type=str, help="Id of task")
parser.add_argument("date", type=str, help="Date of progress")
parser.add_argument("duration_in_secs", type=int, help="Duration of task progress")

class TaskListRes(Resource):
    def get(self):
        tasks = Task.objects()
        return [task.get_json() for task in tasks], 200

    def post(self):
        args = parser.parse_args()
        local_id = args["local_id"]
        name = args["name"]
        due_date = utils.date_from_iso8601(args["due_date"])
        color = args["color"]
        payment_per_hour = args["payment_per_hour"]

        task = Task(local_id=local_id,
                    name=name,
                    due_date=due_date,
                    color=color,
                    payment_per_hour=payment_per_hour,
                    done=False)

        print(task.due_date)
        task.save()
        return task.get_json(), 201

class TaskRes(Resource):

    def get(self, task_id):
        task = Task.objects().with_id(task_id)
        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        else:
            return task.get_json(), 200

    def delete(self, task_id):
        task = Task.objects().with_id(task_id)
        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        else:
            task.delete()
            return {"code": 1, "message":"Deleted"}, 200

    def put(self, task_id):
        task = Task.objects().with_id(task_id)
        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        else:
            args = parser.parse_args()
            local_id = args["local_id"]
            name = args["name"]
            due_date = utils.date_from_iso8601(args["due_date"])
            color = args["color"]
            done = args["done"]
            payment_per_hour = args["payment_per_hour"]

            task.update(set__local_id=local_id,
                        set__name=name,
                        set__due_date=due_date,
                        set__color=color,
                        set__done=done,
                        set__payment_per_hour=payment_per_hour
                        )
            return Task.objects().with_id(task.id).get_json(), 200


class TaskProgressListRes(Resource):
    def get(self):
        return [task_progress.get_json() for task_progress in TaskProgress.objects()], 200


    def post(self):
        args = parser.parse_args()
        task_id = args["task_id"]
        date = utils.date_from_iso8601(args["date"])
        duration_in_secs = args["duration_in_secs"]

        task = Task.objects().with_id(task_id)
        if task is None:
            return {"code": 0, "message": "Task not found"}, 404
        else:
            task_progress = TaskProgress(task=task, date=date, duration_in_secs=duration_in_secs)
            task_progress.save()
            return TaskProgress.objects().with_id(task_progress.id).get_json(), 200

class TaskProgressRes(Resource):
    def get(self, task_progress_id):
        task_progress = TaskProgress.objects().with_id(task_progress_id)
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        else:
            return task_progress.get_json(), 200

    def put(self, task_progress_id):
        task_progress = TaskProgress.objects().with_id(task_progress_id)
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        else:
            args = parser.parse_args()
            date = utils.date_from_iso8601(args["date"])
            duration_in_secs = args["duration_in_secs"]
            task_progress.update(set__date=date, set__duration_in_secs=duration_in_secs)
            return TaskProgress.objects().with_id(task_progress.id).get_json(), 200

    def delete(self, task_progress_id):
        task_progress = TaskProgress.objects().with_id(task_progress_id)
        if task_progress is None:
            return {"code": 0, "message": "Task progress not found"}, 404
        else:
            task_progress.delete()
            return {"code": 1, "message": "Task progress deleted"}, 200

api.add_resource(TaskListRes, "/api/task")
api.add_resource(TaskRes, "/api/task/<task_id>")

api.add_resource(TaskProgressListRes, "/api/task-progress")
api.add_resource(TaskProgressRes, "/api/task-progress/<task_progress_id>")


if __name__ == '__main__':
    app.run(port=6969)
