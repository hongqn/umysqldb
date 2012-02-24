import sys

import umysql
import pymysql.connections

from .utils import setdocstring
from .cursors import Cursor
from .err import (
    map_umysql_exception_to_oursql_exception,
    map_runtime_error_to_oursql_exception,
    Error,
)

def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    raise errorclass, errorvalue


class Connection(pymysql.connections.Connection):

    """MySQL Database Connection Object"""

    errorhandler = defaulterrorhandler

    @setdocstring(pymysql.connections.Connection.__init__)
    def __init__(self, *args, **kwargs):
        if 'cursorclass' not in kwargs:
            kwargs['cursorclass'] = Cursor
        self._umysql_conn = umysql.Connection()
        super(Connection, self).__init__(*args, **kwargs)

    @setdocstring(pymysql.connections.Connection.set_charset)
    def set_charset(self, charset):
        if charset:
            self._umysql_conn.query("SET NAMES %s", (charset,))
            self.charset = charset

    @setdocstring(pymysql.connections.Connection.autocommit)
    def autocommit(self, value):
        self._umysql_conn.query("SET AUTOCOMMIT = %s", (value,))

    @setdocstring(pymysql.connections.Connection.commit)
    def commit(self):
        self.query('COMMIT')

    @setdocstring(pymysql.connections.Connection.close)
    def close(self):
        if not self._umysql_conn.is_connected():
            raise Error("Already closed")
        self._umysql_conn.close()

    def _connect(self):
        self._umysql_conn.connect(self.host, self.port, self.user,
                                  self.password, self.db, False, self.charset)

    def query(self, sql, args=()):
        try:
            return self._umysql_conn.query(sql, args)
        except umysql.Error, exc:
            traceback = sys.exc_info()[2]
            exc = map_umysql_exception_to_oursql_exception(exc)
            raise exc, None, traceback
        except RuntimeError, exc:
            traceback = sys.exc_info()[2]
            exc = map_runtime_error_to_oursql_exception(exc)
            raise exc, None, traceback

