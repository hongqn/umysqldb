import pymysql.cursors

from .utils import setdocstring

class Cursor(pymysql.cursors.Cursor):
    setdocstring(pymysql.cursors.Cursor)
    def execute(self, query, args=()):
        conn = self._get_db()
        return conn.query(query, args)
