import sys
from datetime import timedelta

import umysql
import pymysql.connections
from pymysql.constants import FIELD_TYPE

from .utils import setdocstring
from .cursors import Cursor
from .err import (
    map_umysql_exception_to_oursql_exception,
    map_runtime_error_to_oursql_exception,
    Error,
)
from .times import (
    TimeDelta_or_None,
    DateTimeDelta2literal,
    mysql_timestamp_converter,
)


conversions = {
    FIELD_TYPE.TIME: TimeDelta_or_None,
    FIELD_TYPE.TIMESTAMP: mysql_timestamp_converter,
}

def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    raise errorclass, errorvalue


class ResultSet(object):
    def __init__(self, fields, rows):
        self.fields = fields
        self.rows = rows


class Connection(pymysql.connections.Connection):

    """MySQL Database Connection Object"""

    errorhandler = defaulterrorhandler

    @setdocstring(pymysql.connections.Connection.__init__)
    def __init__(self, *args, **kwargs):
        if 'cursorclass' not in kwargs:
            kwargs['cursorclass'] = Cursor
        if 'conv' not in kwargs:
            kwargs['conv'] = conversions
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

    @setdocstring(pymysql.connections.Connection.rollback)
    def rollback(self):
        self.query("ROLLBACK")

    @setdocstring(pymysql.connections.Connection.close)
    def close(self):
        if not self._umysql_conn.is_connected():
            raise Error("Already closed")
        self._umysql_conn.close()

    def _connect(self):
        self._umysql_conn.connect(self.host, self.port, self.user,
                                  self.password, self.db, False, self.charset)

    def query(self, sql, args=()):
        args = self._convert_args(args)
        try:
            result_set = self._umysql_conn.query(sql, args)
        except umysql.Error, exc:
            traceback = sys.exc_info()[2]
            exc = map_umysql_exception_to_oursql_exception(exc)
            raise exc, None, traceback
        except RuntimeError, exc:
            traceback = sys.exc_info()[2]
            exc = map_runtime_error_to_oursql_exception(exc)
            raise exc, None, traceback
        else:
            if not isinstance(result_set, tuple):
                result_set = self._convert_result_set(result_set)
            return result_set

    def _convert_args(self, args):
        def _():
            for arg in args:
                if isinstance(arg, timedelta):
                    arg = DateTimeDelta2literal(arg)
                yield arg
        return tuple(_())

    def _convert_result_set(self, result_set):
        converters = [self.decoders.get(field[1]) for field in
                      result_set.fields]
        rows = [tuple(conv(data) if conv else data
                      for data, conv in zip(row, converters))
                for row in result_set.rows]
        rs = ResultSet(result_set.fields, rows)
        return rs
