import hmac
from datetime import datetime

def generate():
    return hmac.new(str.encode(str(datetime.now()))).hexdigest()