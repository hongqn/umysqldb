from pymysql.err import *

def map_umysql_error_to_umysqldb_exception(umysql_exc):
    errorclass = error_map.get(umysql_exc.args[0])
    if errorclass:
        return errorclass(*umysql_exc.args)

    # couldn't find the right error number
    code, message  = umysql_exc.args[:2]
    if code == 0 and message.startswith("Connection reset by peer"):
        return OperationalError(2013, "Lost connection to MySQL server during query")

    return InternalError(*umysql_exc.args)

def map_runtime_error_to_umysqldb_exception(exc):
    if exc.args == ('Not connected',):
        return ProgrammingError("cursor closed")
    return exc
