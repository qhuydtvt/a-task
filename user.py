from mongoengine import *


class User(Document):
    username = StringField()
    password = StringField()
    token = StringField()

    def get_json(self):
        return {
            "username": self.username,
            "password": self.password,
            "token": self.token
        }

def find(username):
    return User.objects(username=username).first()

def user_from_token(token):
  return User.objects(token=token).first()