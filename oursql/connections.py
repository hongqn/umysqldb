import umysql
import pymysql.connections

class Connection(pymysql.connections.Connection):
    pass
#    def _connect(self):
#        self._umysql_conn = umysql.Connection()
