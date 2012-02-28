import pymysql.cursors

from .util import setdocstring
from .err import (
    ProgrammingError,
    NotSupportedError,
)

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


class SSCursor(Cursor):
    """
    Unbuffered Cursor, mainly useful for queries that return a lot of data,
    or for connections to remote servers over a slow network.

    Instead of copying every row of data into a buffer, this will fetch
    rows as needed. The upside of this, is the client uses much less memory,
    and rows are returned much faster when traveling over a slow network,
    or if the result set is very big.

    There are limitations, though. The MySQL protocol doesn't support
    returning the total number of rows, so the only way to tell how many rows
    there are is to iterate over every row returned. Also, it currently isn't
    possible to scroll backwards, as only the current row is held in memory.
    """

    def close(self):
        conn = self._get_db()
        conn._result._finish_unbuffered_query()

        try:
            if self._has_next:
                while self.nextset(): pass
        except: pass

    def _query(self, q):
        conn = self._get_db()
        self._last_executed = q
        conn.query(q, unbuffered=True)
        self._do_get_result()
        return self.rowcount

    def read_next(self):
        """ Read next row """

        conn = self._get_db()
        conn._result._read_rowdata_packet_unbuffered()
        return conn._result.rows

    def fetchone(self):
        """ Fetch next row """

        self._check_executed()
        row = self.read_next()
        if row is None:
            return None
        self.rownumber += 1
        return row

    def fetchall(self):
        """
        Fetch all, as per MySQLdb. Pretty useless for large queries, as
        it is buffered. See fetchall_unbuffered(), if you want an unbuffered
        generator version of this method.
        """

        rows = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            rows.append(row)
        return tuple(rows)

    def fetchall_unbuffered(self):
        """
        Fetch all, implemented as a generator, which isn't to standard,
        however, it doesn't make sense to return everything in a list, as that
        would use ridiculous memory for large result sets.
        """

        row = self.fetchone()
        while row is not None:
            yield row
            row = self.fetchone()

    def fetchmany(self, size=None):
        """ Fetch many """

        self._check_executed()
        if size is None:
            size = self.arraysize

        rows = []
        for i in range(0, size):
            row = self.read_next()
            if row is None:
                break
            rows.append(row)
            self.rownumber += 1
        return tuple(rows)
        
    def scroll(self, value, mode='relative'):
        self._check_executed()
        if not mode == 'relative' and not mode == 'absolute':
            self.errorhandler(self, ProgrammingError,
                    "unknown scroll mode %s" % mode)
    
        if mode == 'relative':
            if value < 0:
                self.errorhandler(self, NotSupportedError,
                    "Backwards scrolling not supported by this cursor")
            
            for i in range(0, value): self.read_next()
            self.rownumber += value
        else:
            if value < self.rownumber:
                self.errorhandler(self, NotSupportedError,
                    "Backwards scrolling not supported by this cursor")
                
            end = value - self.rownumber
            for i in range(0, end): self.read_next()
            self.rownumber = value
