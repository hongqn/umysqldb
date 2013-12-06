import umysqldb
import unittest

class UMySQLdbTestCase(unittest.TestCase):
    # Edit this to suit your test environment.
    databases = [
        {"host":"127.0.0.1","user":"test",
         "passwd":"","db":"test_umysqldb", "use_unicode": True},
        {"host":"127.0.0.1","user":"test","passwd":"","db":"test_umysqldb2"}]

    def setUp(self):
        self.connections = []

        for params in self.databases:
            self.connections.append(umysqldb.connect(**params))

    def tearDown(self):
        for connection in self.connections:
            connection.close()

