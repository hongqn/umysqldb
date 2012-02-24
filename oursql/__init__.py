import pymysql
from pymysql import *
from pymysql import DATETIME
from pymysql import __all__

from .utils import setdocstring

__all__ += ['DATETIME']

@setdocstring(pymysql.Connect)
def Connect(*args, **kwargs):
    from .connections import Connection
    return Connection(*args, **kwargs)

connect = Connection = Connect
