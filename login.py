from flask import jsonify, redirect
from collections import OrderedDict
from flask_restful import Resource, reqparse
from user import *
import user_token
import  datetime
from werkzeug.security import safe_str_cmp
from flask_jwt import JWT, current_identity, jwt_required, JWTError

parser = reqparse.RequestParser()
parser.add_argument("username", type=str, help="Username")
parser.add_argument("password", type=str, help="Password")

class LoginCredentials:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @classmethod
    def create(cls, user):
        return LoginCredentials(id=str(user.id),username=user.username, password=user.password)

    def user(self):
        return User.objects().with_id(self.id)

class RegisterRes(Resource):
    def post(self):
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        found_user = User.objects(username=username).first()
        if found_user is not None:
            return {"code": 0, "message": "User already exists", "token":""}, 400
        user = User(username=username, password=password, token=user_token.generate())
        user.save()
        # Afer successfully registered, redirect user to login immediately
        return redirect('/api/login', 307)

def authenticate(username, password):
    user = find(username)
    if user is not None and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return LoginCredentials.create(user)

def identity(payload):
    user_id = payload['identity']
    user = User.objects.with_id(user_id)
    if user is not None:
        return LoginCredentials.create(user)

def handle_user_exception_again(e):
    if isinstance(e, JWTError):
        return jsonify(OrderedDict([
            ('status_code', e.status_code),
            ('error', e.error),
            ('description', e.description),
        ])), e.status_code, e.headers
    return e

def jwt_init(app):
    app.config['SECRET_KEY'] = 'Xk]ywC83pO!&`AN|Ak1T;=L6ezZE[g'
    app.config["JWT_EXPIRATION_DELTA"] = datetime.timedelta(hours=24)
    app.config["JWT_AUTH_URL_RULE"] = "/api/login"
    # Catch exception and return it to users
    # https://github.com/mattupstate/flask-jwt/issues/32
    app.handle_user_exception = handle_user_exception_again
    jwt = JWT(app=app,
              authentication_handler=authenticate,
              identity_handler=identity)
    return jwt
