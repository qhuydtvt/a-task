from datetime import datetime

def date_from_iso8601(date_time_str):
    if date_time_str != None and date_time_str != "":
        return datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
    else:
        return None


def toISO8601(datetime):
    if datetime != None and datetime != "":
        return datetime.strptime(str(datetime), '%Y-%m-%d %H:%M:%S').isoformat()
    else:
        return ""
