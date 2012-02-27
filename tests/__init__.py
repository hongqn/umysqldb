def setup_package():
    @apply
    def print_sqls():
        print "patch"
        import oursql.connections
        orig_query = oursql.connections.Connection.query
        def query(self, *a, **kw):
            print "QUERY:", str(a)[:100], str(kw)[:100]
            return orig_query(self, *a, **kw)
        oursql.connections.Connection.query = query


