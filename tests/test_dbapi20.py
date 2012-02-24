import oursql

from . import dbapi20

class OurSQLDBAPI20Tests(dbapi20.DatabaseAPI20Test):
    driver = oursql
    connect_kw_args = {
            'host': '127.0.0.1',
            'user': 'test',
            'passwd': '',
            'db': 'test',
        }


