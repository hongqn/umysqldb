#import umysql
from pymysql.connections import Connection as PyMySQLConnection

class Connection(PyMySQLConnection):
    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
#        self._conn = umysql.Connection(*args, **kwargs)

