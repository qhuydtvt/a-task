from mongoengine import *
from datetime import date
import utils
import user_token
from user import *
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()
parser.add_argument('token', type=str, help='Token of noter', location="headers")

parser.add_argument("local_id", type=str, help="Local id of task")
parser.add_argument("name", type=str, help="Name of task")
parser.add_argument("due_date", type=str, help="Due date of task")
parser.add_argument("color", type=str, help="Color of task")
parser.add_argument("payment_per_hour", type=float, help="Payment rate of task")
parser.add_argument("done", type=bool, help="Status of task")

class Task(Document):
    user_id = ObjectIdField()
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

def task_from_id(id):
    return Task.objects().with_id(id)

class TaskListRes(Resource):

    def get(self):
        args = parser.parse_args()
        token = args["token"]
        user = user_from_token(token)
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": token}, 401

        tasks = Task.objects(user_id=user.id)
        return [task.get_json() for task in tasks], 200

    def post(self):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        local_id = args["local_id"]
        name = args["name"]
        due_date = utils.date_from_iso8601(args["due_date"])
        color = args["color"]
        payment_per_hour = args["payment_per_hour"]

        task = Task(user_id=user.id,
                    local_id=local_id,
                    name=name,
                    due_date=due_date,
                    color=color,
                    payment_per_hour=payment_per_hour,
                    done=False)

        task.save()
        return task.get_json(), 201


class TaskRes(Resource):
    def get(self, task_id):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task = Task.objects().with_id(task_id)

        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        elif task.user_id != user.id:
            return {"code": 0, "message": "This taks is not yours, fuck off"}, 401
        else:
            return task.get_json(), 200

    def delete(self, task_id):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task = Task.objects().with_id(task_id)

        if task.user_id != user.id:
            return {"code": 0, "message": "This taks is not yours, fuck off"}, 401
        elif task.user_id != user.id:
            return {"code": 0, "message": "This taks is not yours, fuck off"}, 401
        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        else:
            task.delete()
            return {"code": 1, "message": "Deleted"}, 200

    def put(self, task_id):
        args = parser.parse_args()
        user = user_from_token(args["token"])
        if user is None:
            return {"code": 0, "message": "Not authorized", "token": args["token"]}, 401

        task = Task.objects().with_id(task_id)
        if task is None:
            return {"code": 0, "message": "Not found"}, 404
        elif task.user_id != user.id:
            return {"code": 0, "message": "This taks is not yours, fuck off"}, 401
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
