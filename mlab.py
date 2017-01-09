import mongoengine

#mongodb://<dbuser>:<dbpassword>@ds159208.mlab.com:59208/a-task

host = "ds159208.mlab.com"
port = 59208
db_name = "a-task"
user_name = "admin"
password = "admin"


def connect():
    mongoengine.connect(db_name, host=host, port=port, username=user_name, password=password)

def list2json(l):
    import json
    return [json.loads(item.to_json()) for item in l]


def item2json(item):
    import json
    return json.loads(item.to_json())