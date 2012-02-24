import pymysql.cursors

from .utils import setdocstring

class Cursor(pymysql.cursors.Cursor):
    @setdocstring(pymysql.cursors.Cursor)
    def execute(self, query, args=None):
        conn = self._get_db()

        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list, dict)):
            args = (args,)
        return conn.query(query, args)
