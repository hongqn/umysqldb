import pymysql
from pymysql import *
from pymysql import DATETIME
from pymysql import __all__

from .util import setdocstring

VERSION = '0.1'

__all__ += ['DATETIME']

@setdocstring(pymysql.Connect)
def Connect(*args, **kwargs):
    from .connections import Connection
    return Connection(*args, **kwargs)

def thread_safe():
    return True  # match MySQLdb.thread_safe()

connect = Connection = Connect
