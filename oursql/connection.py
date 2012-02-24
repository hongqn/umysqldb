import umysql
import pymysql.connections

class Connection(object):
    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__()
        self._pymysql_conn = pymysql.connections.Connection(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._pymysql_conn, name)

    def _connect(self):
        pass
