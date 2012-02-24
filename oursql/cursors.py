import pymysql.cursors

from .utils import setdocstring

class Cursor(pymysql.cursors.Cursor):
    @setdocstring(pymysql.cursors.Cursor)
    def execute(self, query, args=None):
        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list, dict)):
            args = (args,)

        return self._query(query, args)

    def _query(self, query, args):
        conn = self._get_db()
        return conn.query(query, args)

