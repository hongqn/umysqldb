import pymysql.cursors

from .utils import setdocstring

class Cursor(pymysql.cursors.Cursor):
    @setdocstring(pymysql.cursors.Cursor.execute)
    def execute(self, query, args=None):
        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list, dict)):
            args = (args,)

        return self._query(query, args)

    def _query(self, query, args):
        conn = self._get_db()
        result = conn.query(query, args)
        if isinstance(result, tuple):
            self.rowcount = result[0]
            self._rows = ()
        else:
            self.rowcount = len(result.rows)
            self._rows = result.rows
        self.rownumber = 0
        return self.rowcount