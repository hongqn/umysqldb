from mock import patch, Mock
import umysqldb.cursors as M


def test_executemany_should_handle_on_duplicate_key_update_clause():
    with patch.object(M.Cursor, '_query') as mock_query:
        sql = 'INSERT INTO _test(id,val) VALUES(%s,%s) ' \
              'ON DUPLICATE KEY UPDATE id=VALUES(id),val=VALUES(val)'
        args = [(44495, 1), (44495, 2)]
        mock_conn = Mock()
        mock_conn.literal.side_effect = repr
        cursor = M.Cursor(mock_conn)
        cursor.executemany(sql, args)
        mock_query.assert_called_once_with(
            'INSERT INTO _test(id,val) VALUES\n(%s,%s),(%s,%s)\n '
            'ON DUPLICATE KEY UPDATE id=VALUES(id),val=VALUES(val)',
            (44495, 1, 44495, 2))
