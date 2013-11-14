import sys
import time
import datetime
import socket

import umysql
import pymysql.connections
from pymysql.constants import FIELD_TYPE

from .util import setdocstring
from .cursors import Cursor
from .err import (
    map_umysql_error_to_umysqldb_exception,
    map_runtime_error_to_umysqldb_exception,
    Error,
    OperationalError,
)
from .times import (
    encode_struct_time,
    encode_timedelta,
    encode_time,
    TimeDelta_or_None,
    mysql_timestamp_converter,
)


encoders = {
    time.struct_time : encode_struct_time,
    datetime.timedelta: encode_timedelta,
    datetime.time: encode_time,
}

decoders = {
    FIELD_TYPE.TIME: TimeDelta_or_None,
    FIELD_TYPE.TIMESTAMP: mysql_timestamp_converter,
    FIELD_TYPE.NEWDECIMAL: float,
}

def notouch(x):
    return x

def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    raise errorclass, errorvalue


class ResultSet(object):
    def __init__(self, affected_rows=None, insert_id=None, description=None,
                 rows=None):
        self.affected_rows = affected_rows
        self.insert_id = insert_id
        self.description = description
        self.rows = rows


class Connection(pymysql.connections.Connection):

    """MySQL Database Connection Object"""

    errorhandler = defaulterrorhandler

    @setdocstring(pymysql.connections.Connection.__init__)
    def __init__(self, *args, **kwargs):
        if 'cursorclass' not in kwargs:
            kwargs['cursorclass'] = Cursor
        if 'conv' not in kwargs:
            kwargs['conv'] = decoders
        if 'charset' not in kwargs:
            kwargs['charset'] = 'utf8'
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
        try:
            self._umysql_conn.connect(self.host, self.port, self.user,
                                      self.password, self.db or '', False, self.charset)
        except socket.error, e:
            raise OperationalError(2003, "Can't connect to MySQL server on %r (%s)" % (
                self.host, e.args[0]))
        except umysql.Error, exc:
            traceback = sys.exc_info()[2]
            exc = map_umysql_error_to_umysqldb_exception(exc)
            raise exc, None, traceback

    # internal use only (called from cursor)
    def query(self, sql, args=()):
        args = self._convert_args(args)
        try:
            result_set = self._umysql_conn.query(sql, args)
        except umysql.Error, exc:
            traceback = sys.exc_info()[2]
            exc = map_umysql_error_to_umysqldb_exception(exc)
            raise exc, None, traceback
        except RuntimeError, exc:
            traceback = sys.exc_info()[2]
            exc = map_runtime_error_to_umysqldb_exception(exc)
            raise exc, None, traceback
        else:
            self._result = self._convert_result_set(result_set)
            return self._result.affected_rows

    def _convert_args(self, args):
        args = tuple(encoders.get(type(arg), notouch)(arg)
                     for arg in args)
        return args

    def _convert_result_set(self, result_set):
        if isinstance(result_set, tuple):
            rs = ResultSet(affected_rows=result_set[0],
                           insert_id=result_set[1])
        else:
            converters = [self.decoders.get(field[1]) for field in
                          result_set.fields]
            rows = tuple(tuple(conv(data) if conv and data is not None else data
                          for data, conv in zip(row, converters))
                         for row in result_set.rows)
            description = tuple(f + (None,) * (7 - len(f)) for f in result_set.fields)
            rs = ResultSet(description=description, rows=rows,
                           affected_rows=len(rows))
        return rs

    # _mysql support
    def get_proto_info(self):
        raise NotImplementedError("umysql has no proto info")

    def get_server_info(self):
        raise NotImplementedError("umysql has no server info")

    def thread_id(self):
        raise NotImplementedError("umysql has no thread info")

    def ping(self, reconnect=False):
        flag = False
        if self._umysql_conn.is_connected():
            try:
                self._umysql_conn.query("select 1;")
            except:
                self._umysql_conn.close()
                flag = True
        else:
            flag = True
        if flag:
            if reconnect:
                self._connect()
            else:
                raise OperationalError(2006, 'MySQL server has gone away')
