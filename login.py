from flask_restful import Resource, reqparse
from user import *
import user_token

parser = reqparse.RequestParser()
parser.add_argument("username", type=str, help="Username")
parser.add_argument("password", type=str, help="Password")

class LoginRes(Resource):
    def post(self):
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        user = User.objects(username=username).first()
        if user is None:
            print("Could not find user")
            return {"code": 0, "message": "User doesn't exist"}, 401
        if password != user.password:
            print("user name and password mismatch")
            return {"code": 0, "message": "User or password doesn't match"}, 401

        token = user_token.generate()
        User.objects().with_id(user.id).update(set__token=token)
        return {"code": 1, "message": "Logged in", "token": token}, 200


class RegisterRes(Resource):
    def post(self):
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        found_user = User.objects(username=username).first()
        if found_user is not None:
            return {"code": 0, "message": "User already exists"}, 400
        user = User(username=username, password=password, token=user_token.generate())
        user.save()
        return {"code": 1, "message": 'Registered', "token": user.token}, 200