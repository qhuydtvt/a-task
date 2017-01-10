from flask import Flask
from datetime import date
from mongoengine import *
from flask_restful import Api, reqparse, Resource, marshal, marshal_with, fields
from datetime import datetime

import utils
import json

from user import *
import user_token
import mlab
from task import TaskListRes, TaskRes
from task_progress import TaskProgressListRes, TaskProgressRes
from login import LoginRes, RegisterRes

app = Flask(__name__)
api = Api(app)
mlab.connect()

api.add_resource(TaskListRes, "/api/task")
api.add_resource(TaskRes, "/api/task/<task_id>")

api.add_resource(TaskProgressListRes, "/api/task-progress")
api.add_resource(TaskProgressRes, "/api/task-progress/<task_progress_id>")

api.add_resource(LoginRes, "/api/login")
api.add_resource(RegisterRes, "/api/register")

if __name__ == '__main__':
    app.run(port=9696)
