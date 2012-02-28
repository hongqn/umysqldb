import pymysql.cursors

from .util import setdocstring

class Cursor(pymysql.cursors.Cursor):
    @setdocstring(pymysql.cursors.Cursor.execute)
    def execute(self, query, args=None):
        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list, dict)):
            args = (args,)

        result = self._query(query, args)

        self._executed = query
        return result

    @setdocstring(pymysql.cursors.Cursor.executemany)
    def executemany(self, query, args):
        if not args:
            return
        self.rowcount = sum([self.execute(query, arg) for arg in args])
        return self.rowcount

    def _query(self, query, args=()):
        conn = self._get_db()
        self._umysql_result = result = conn.query(query, args)
        if isinstance(result, tuple):
            self.rowcount = result[0]
            self.description = None
            self._rows = ()
        else:
            self.rowcount = len(result.rows)
            # fill field to 7-item tuple to meet DBAPI spec
            self.description = tuple(f + (None,) * (7 - len(f))
                                     for f in result.fields)
            self._rows = result.rows
        self.rownumber = 0
        return self.rowcount
