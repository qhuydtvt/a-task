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


def user_from_token(token):
  return User.objects(token=token).first()