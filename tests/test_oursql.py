from nose.tools import raises

import oursql

@raises(oursql.err.OperationalError)
def test_access_denied_should_raise_OperationalError():
    oursql.connect(host='127.0.0.1', user='asdf', passwd='fdsa')
