import sys
import pymysql.cursors

from .util import setdocstring

class Cursor(pymysql.cursors.Cursor):
    @setdocstring(pymysql.cursors.Cursor.execute)
    def execute(self, query, args=None):
        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list, dict)):
            args = (args,)

        result = 0
        try:
            result = self._query(query, args)
        except:
            exc, value, tb = sys.exc_info()
            del tb
            self.errorhandler(self, exc, value)

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
        conn.query(query, args)
        self.rowcount = conn._result.affected_rows
        self.rownumber = 0
        self.description = conn._result.description
        self.lastrowid = conn._result.insert_id
        self._rows = conn._result.rows
        self._has_next = 0
        return self.rowcount


class DictCursor(Cursor):
    """A cursor which returns results as a dictionary"""

    def execute(self, query, args=None):
        result = super(DictCursor, self).execute(query, args)
        if self.description:
            self._fields = [ field[0] for field in self.description ]
        return result

    def fetchone(self):
        ''' Fetch the next row '''
        self._check_executed()
        if self._rows is None or self.rownumber >= len(self._rows):
            return None
        result = dict(zip(self._fields, self._rows[self.rownumber]))
        self.rownumber += 1
        return result

    def fetchmany(self, size=None):
        ''' Fetch several rows '''
        self._check_executed()
        if self._rows is None:
            return None
        end = self.rownumber + (size or self.arraysize)
        result = [ dict(zip(self._fields, r)) for r in self._rows[self.rownumber:end] ]
        self.rownumber = min(end, len(self._rows))
        return tuple(result)

    def fetchall(self):
        ''' Fetch all the rows '''
        self._check_executed()
        if self._rows is None:
            return None
        if self.rownumber:
            result = [ dict(zip(self._fields, r)) for r in self._rows[self.rownumber:] ]
        else:
            result = [ dict(zip(self._fields, r)) for r in self._rows ]
        self.rownumber = len(self._rows)
        return tuple(result)

