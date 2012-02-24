import pymysql
from pymysql import *
from pymysql import DATETIME
from pymysql import __all__

__all__ += ['DATETIME']

def Connect(*args, **kwargs):
    pymysql.Connect.__docstring__

    from .connections import Connection
    return Connection(*args, **kwargs)

connect = Connection = Connect
