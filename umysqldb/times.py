import time
from datetime import datetime, date, timedelta
import math

Timestamp = datetime

def encode_struct_time(obj):
    return time.strftime("%Y-%m-%d %H:%M:%S", obj)

def encode_timedelta(delta):
    seconds = int(delta.seconds) % 60
    minutes = int(delta.seconds // 60) % 60
    hours = int(delta.seconds // 3600) % 24 + int(delta.days) * 24
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

def encode_time(obj):
    s = "%02d:%02d:%02d" % (int(obj.hour), int(obj.minute), int(obj.second))
    if obj.microsecond:
        s += ".%f" % obj.microsecond
    return s

def Date_or_None(s):
    try: return date(*[ int(x) for x in s.split('-',2)])
    except: return None


def DateTime_or_None(s):
    if ' ' in s:
        sep = ' '
    elif 'T' in s:
        sep = 'T'
    else:
        return Date_or_None(s)

    try:
        d, t = s.split(sep, 1)
        return datetime(*[ int(x) for x in d.split('-')+t.split(':') ])
    except:
        return Date_or_None(s)

def TimeDelta_or_None(s):
    try:
        h, m, s = s.split(':')
        h, m, s = int(h), int(m), float(s)
        td = timedelta(hours=abs(h), minutes=m, seconds=int(s),
                       microseconds=int(math.modf(s)[0] * 1000000))
        if h < 0:
            return -td
        else:
            return td
    except ValueError:
        # unpacking or int/float conversion failed
        return None

def mysql_timestamp_converter(s):
    """Convert a MySQL TIMESTAMP to a Timestamp object."""
    # MySQL>4.1 returns TIMESTAMP in the same format as DATETIME
    if s[4] == '-': return DateTime_or_None(s)
    s += "0"*(14-len(s))
    parts = [int(x) for x in (s[:4],s[4:6],s[6:8],s[8:10],s[10:12],s[12:14])
             if x]
    try:
        return Timestamp(*parts)
    except Exception:
        return None
