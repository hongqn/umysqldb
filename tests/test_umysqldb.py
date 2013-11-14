from nose.tools import raises

import umysqldb
import umysqldb.err

@raises(umysqldb.err.OperationalError)
def test_access_denied_should_raise_OperationalError():
    umysqldb.connect(host='127.0.0.1', user='asdf', passwd='fdsa')
