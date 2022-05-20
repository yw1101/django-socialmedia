from datetime import datetime
import pytz
#python timezone

def utc_now():
    return datetime.now().replace(tzinfo = pytz.utc)
