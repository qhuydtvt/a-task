from mongoengine import *
from datetime import date
import utils
import user_token
from user import *
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from task_progress import *

parser = reqparse.RequestParser()
parser.add_argument('token', type=str, help='Token of noter', location="headers")

parser.add_argument("local_id", type=str, help="Local id of task")
parser.add_argument("name", type=str, help="Name of task")
parser.add_argument("due_date", type=str, help="Due date of task")
parser.add_argument("color", type=str, help="Color of task")
parser.add_argument("payment_per_hour", type=float, help="Payment rate of task")
parser.add_argument("done", type=bool, help="Status of task")

class Task(Document):
    user = ReferenceField("User")
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
            "due_date": utils.toISO8601(self.due_date),
            "color": self.color,
            "payment_per_hour" : self.payment_per_hour,
            "done" : self.done
        }

def task_from_id(id):
    return Task.objects().with_id(id)

# def task_from_local_id(local_id):
#     return Task.objects(local_id=local_id).first()

class TaskListRes(Resource):

    @jwt_required()
    def get(self):
        user = current_identity.user()
        tasks = Task.objects(user=user)
        return [task.get_json() for task in tasks], 200

    @jwt_required()
    def post(self):
        args = parser.parse_args()

        user = current_identity.user()
        local_id = args["local_id"]
        name = args["name"]
        due_date = utils.date_from_iso8601(args["due_date"])
        color = args["color"]
        payment_per_hour = args["payment_per_hour"]

        task = Task(user=user,
                    local_id=local_id,
                    name=name,
                    due_date=due_date,
                    color=color,
                    payment_per_hour=payment_per_hour,
                    done=False)

        task.save()
        return task.get_json(), 201


class TaskRes(Resource):
    @jwt_required()
    def get(self, task_id):
        args = parser.parse_args()
        user = current_identity.user()
        task = Task.objects(local_id=task_id, user=user).first()

        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        else:
            return task.get_json(), 200

    @jwt_required()
    def delete(self, task_id):
        args = parser.parse_args()
        user = current_identity.user()
        task = Task.objects(local_id=task_id, user=user).first()

        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        else:
            for task_progress in TaskProgress.objects(task=task):
                task_progress.delete()
            task.delete()
            return {"code": 1, "message": "Deleted"}, 200

    @jwt_required()
    def put(self, task_id):
        args = parser.parse_args()
        user = current_identity.user()
        task = Task.objects(local_id=task_id, user=user).first()

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
                        set__payment_per_hour=payment_per_hour)
            return Task.objects().with_id(task.id).get_json(), 200
