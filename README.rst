========
umysqldb
========

A MySQLdb compatible wrapper around ultramysql_.

.. _ultramysql: https://github.com/esnme/ultramysql

Usage
-----

::

  >>> import umysqldb
  >>> umysqldb.install_as_MySQLdb()
  >>> import MySQLdb
  >>> MySQLdb is umysqldb
  True
  >>> conn = MySQLdb.connect(host='localhost')
  >>> curs = conn.cursor()
  >>> curs.execute("select 1")
  1
  >>> curs.fetchone()
  (1L,)
  >>> conn.close()


.. image:: https://travis-ci.org/hongqn/umysqldb.png?branch=master,develop
   :alt: Build Status
   :target: https://travis-ci.org/hongqn/umysqldb
