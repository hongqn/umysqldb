from pymysql.err import *

def map_umysql_exception_to_oursql_exception(umysql_exc):
    errorclass = error_map.get(umysql_exc.args[0])
    if errorclass:
        return errorclass(umysql_exc.args)

    # couldn't find the right error number
    return InternalError(umysql_exc.args)
