def setup_package():
    @apply
    def print_sqls():
        print "patch"
        import oursql.connections
        orig_query = oursql.connections.Connection.query
        def query(self, *a, **kw):
            print "QUERY:", str(a)[:800], str(kw)[:800]
            return orig_query(self, *a, **kw)
        oursql.connections.Connection.query = query


