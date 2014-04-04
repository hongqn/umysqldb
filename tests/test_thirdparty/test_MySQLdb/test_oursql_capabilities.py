#!/usr/bin/env python
import capabilities
import unittest
import umysqldb
import warnings

from nose.plugins.skip import SkipTest

warnings.filterwarnings('error')

class test_umysqldb(capabilities.DatabaseTest):

    db_module = umysqldb 
    connect_args = ()
    connect_kwargs = dict(db='test',
                           host='127.0.0.1',
                           user='test',
                           passwd='',
                           charset='utf8',
                           sql_mode="ANSI,STRICT_TRANS_TABLES,TRADITIONAL")
    create_table_extra = "ENGINE=INNODB CHARACTER SET UTF8"
    leak_test = False
    
    def quote_identifier(self, ident):
        return "`%s`" % ident

    def test_TIME(self):
        from datetime import timedelta
        def generator(row,col):
            return timedelta(0, row*8000)
        self.check_data_integrity(
                 ('col1 TIME',),
                 generator)

    def test_DECIMAL(self):
        from decimal import Decimal
        def generator(row,col):
            return Decimal("3.14")
        self.check_data_integrity(
                 ('col1 DECIMAL(3, 2)',),
                 generator)

    def test_TINYINT(self):
        # Number data
        def generator(row,col):
            v = (row*row) % 256
            if v > 127:
                v = v-256
            return v
        self.check_data_integrity(
            ('col1 TINYINT',),
            generator)
        
    def test_stored_procedures(self):
        raise SkipTest("umysql does not support procedures")
        db = self.connection
        c = self.cursor
        self.create_table(('pos INT', 'tree CHAR(20)'))
        c.executemany("INSERT INTO %s (pos,tree) VALUES (%%s,%%s)" % self.table,
                      list(enumerate('ash birch cedar larch pine'.split())))
        db.commit()
        
        c.execute("""
        CREATE PROCEDURE test_sp(IN t VARCHAR(255))
        BEGIN
            SELECT pos FROM %s WHERE tree = t;
        END
        """ % self.table)
        db.commit()

        c.callproc('test_sp', ('larch',))
        rows = c.fetchall()
        self.assertEquals(len(rows), 1)
        self.assertEquals(rows[0][0], 3)
        c.nextset()
        
        c.execute("DROP PROCEDURE test_sp")
        c.execute('drop table %s' % (self.table))

    def test_small_CHAR(self):
        # Character data
        def generator(row,col):
            i = (row*col+62)%256
            if i == 62: return ''
            if i == 63: return None
            return chr(i)
        self.check_data_integrity(
            ('col1 char(1)','col2 char(1)'),
            generator)
    
    def test_bug_2671682(self):
        from umysqldb.constants import ER
        try:
            self.cursor.execute("describe some_non_existent_table");
        except self.connection.ProgrammingError, msg:
            self.assertTrue(msg[0] == ER.NO_SUCH_TABLE)
    
    def test_ping(self):
        raise SkipTest("umysql does not support PING command")
        self.connection.ping()
