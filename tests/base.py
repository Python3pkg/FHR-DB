import unittest
import MySQLdb as mysqlDb
import uuid

from tornado.options import options


class DatabaseTestHelper:

    con = None
    cursor = None

    def connectToDb(self):
        if DatabaseTestHelper.con is not None:
            return DatabaseTestHelper.cursor
        hostAndPort = options.mysql_host.split(":")
        DatabaseTestHelper.con = mysqlDb.connect(host=hostAndPort[0], port=int(hostAndPort[1]),user=options.mysql_user, passwd=options.mysql_password )
        DatabaseTestHelper.cursor =  DatabaseTestHelper.con.cursor()
        return DatabaseTestHelper.cursor

    def createDatabase(self, database, databasFile):
        file = open(databasFile, 'r')
        self.connectToDb().execute("CREATE DATABASE " + database + " CHARACTER SET utf8 COLLATE utf8_unicode_ci")
        DatabaseTestHelper.con.database = database
        self.connectToDb().execute("USE  " + database)
        split_sql = file.read().strip().split(";\n")
        for row in split_sql:
            self.connectToDb().execute(row)
        DatabaseTestHelper.con.commit()

    def dropDatabase(self, database):
        self.connectToDb().execute("DROP DATABASE " + database)

class BaseDbTest(unittest.TestCase):

    dbName = "test_" + str(uuid.uuid4().hex[0:6])

    def setUp(self):
        DatabaseTestHelper().createDatabase(BaseDbTest.dbName, BaseDbTest.dbFile)

    def tearDown(self):
        DatabaseTestHelper().dropDatabase(BaseDbTest.dbName)
