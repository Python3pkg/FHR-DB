import torndb
from tornado.options import options
import json
import re
import itertools

"""
Just the Database wrapper
"""
class Database:
    db = None

    @staticmethod
    def get():
        if Database.db is None:
            Database.db = torndb.Connection(host=options.mysql_host ,  database=options.mysql_database,
                                            user=options.mysql_user, password=options.mysql_password, connect_timeout=5)
        return Database.db

    @staticmethod
    def closeConnection():
        Database.db = None

"""
Class Index which represents an index
"""
class Index():

    def __init__(self, indexOrIndices, indexTable, entitiyFieldInIndexTable):
        self.indexTable = indexTable
        self.indexOrIndices = indexOrIndices
        if isinstance(indexOrIndices, str):
            self.indexOrIndices = []
            self.indexOrIndices.append(indexOrIndices)
        self.entityField = entitiyFieldInIndexTable

    def delete(self, model):
        sql = "DELETE FROM  %(index_table)s WHERE %(entityFieldName)s = " % {'index_table' : self.indexTable, 'entityFieldName' : self.entityField}
        sql += "%s"
        Database.get().execute(sql, model._id)

    def _determineValueAndFieldName(self, field, model):
        innerFields = field.split(".")
        value = model.data[innerFields[0]]
        innerFields.pop(0)
        for innerField in innerFields:
            value = value[innerField]
        return (field.replace('.', '_'), value)

    def _determeinFieldsAndValues(self, model):
        _fields = []
        values = []
        for field in self.indexOrIndices:
            (field, value) = self._determineValueAndFieldName(field, model)
            _fields.append(field)
            values.append(value)
        return (_fields, values)

    def put(self, model):
        self.delete(model)
        (_fields, args) = self._determeinFieldsAndValues(model)
        if None in args:
            return
        args.append(model._id)
        paramString = ", ".join(_fields) + "," + self.entityField
        valueString = ", ".join(["%s"] * (len(_fields) + 1))
        sql = "INSERT INTO %(index_table)s (%(param_string)s) VALUES (%(value_string)s)" % {'index_table' : self.indexTable, 'param_string' : paramString, 'value_string' : valueString }

        # if one args is list we have to permutate
        argsIndexWhichAreList = []
        argsValWhichAreList = []
        argsMapping = {}
        for idx, val in enumerate(args):
            if isinstance(val, list):
                argsIndexWhichAreList.append(idx)
                argsMapping[idx] = len(argsValWhichAreList)
                argsValWhichAreList.append(val)
        if len(argsIndexWhichAreList) > 0:
            for r in itertools.product(*argsValWhichAreList):
                new_args = copy.deepcopy(args)
                for index in argsIndexWhichAreList:
                    new_args[index] = r[argsMapping[index]]
                Database.get().execute(sql, *new_args)
            return
        Database.get().execute(sql, *args)

    def get(self, query, *args):
        query = query.replace(".", "_")
        sql = "SELECT %(entity_id)s FROM %(index_table)s WHERE %(query)s" % {'entity_id' : self.entityField, 'index_table' : self.indexTable, 'query' : query, '%s' : '%s'}
        result = Database.get().get(sql, *args)
        if result is not None:
            return result[self.entityField]

    def all(self, query, *args):
        query = query.replace(".", "_")
        sql = "SELECT %(entity_id)s FROM %(index_table)s WHERE %(query)s" % {'entity_id' : self.entityField, 'index_table' : self.indexTable, 'query' : query, '%s' : '%s'}
        result = Database.get().query(sql, *args)
        list_of_ids = []
        for row in result:
            list_of_ids.append(row[self.entityField])
        return list_of_ids

"""
Class Fql for parsing the query languae
"""
from collections import OrderedDict

class Fql():

    def __init__(self, query):
        self.paramList = []
        self.parseQuery(query)

    def parseQuery(self, query):
        if query is None:
            query = ''
        query = query.replace('%s', '')
        parsedQuery = re.sub(r'[^a-zA-Z0-9_\.]+', ' ', query).split(" ")
        reserved_words = ['limit', 'id', 'and', 'or', 'offset', '', 'updated', 'created']
        self.paramList = list(filter((lambda x: not x.isdigit() and x.lower() not in reserved_words ), parsedQuery))
        # remove duplicateds
        self.paramList = list(OrderedDict.fromkeys(self.paramList))

    def _determineIndexValue(self, index):
        intersect = set(self.paramList).intersection(index.indexOrIndices)
        if len(self.paramList) == 0:
            return 0
        return float(len(intersect)) / float(len(self.paramList))

    def determineIndex(self, indices):
        maxValue = 0
        selectIndex = None
        for index in indices:
            if self._determineIndexValue(index) > maxValue:
                selectIndex = index
        return selectIndex

"""
Class Model which represents an entity

Its abstract you have to extend and write static var

table
field
indices
"""
import copy

class Model():

    def __init__(self, data={}):
        self._id = None
        self._loadData(data)

    def _loadData(self, data):
        self.data = self._loadDataInner({}, copy.deepcopy(self.fields), data)

    def _loadDataInner(self, data_left, _fields, data, recursion = 1):
        for field in _fields:
            if field.lower() == 'id' and recursion == 1:
                raise Exception("ID_IS_RESERVED")
            elif field.lower() == 'created' and recursion == 1:
                raise Exception("CREATED_IS_RESERVED")
            elif field.lower() == 'updated' and recursion == 1:
                raise Exception("UPDATED_IS_RESERVED")
            if field in data:
                if isinstance(_fields[field], dict) and data[field] is None:
                    raise Exception("DICT_CAN_NOT_BE_NULL")
                elif isinstance(_fields[field], dict) and not isinstance(data[field], dict):
                    raise Exception("DICT_CAN_NOT_BE_PRIMITIVE")
                elif isinstance(_fields[field], dict):
                    data_left[field] = self._loadDataInner({}, _fields[field], data[field], recursion + 1)
                elif isinstance(_fields[field], list) and not isinstance(data[field], list):
                    raise Exception("SHOULD_BE_LIST")
                else:
                    data_left[field] = data[field]
            else:
                data_left[field] = _fields[field]
        return data_left

    def _determineValue(self, field):
        _fields = field.split(".")
        value = self.data[_fields[0]]
        _fields.pop(0)
        for singleField in _fields:
            value = value[singleField]
        return value

    def get(self, field = None, remove=[]):
        if field == 'id':
            return self._id
        elif field == 'created':
            return self._created
        elif field == 'updated':
            return self._updated
        if field is not None:
            return self._determineValue(field)
        result = copy.deepcopy(self.data)
        result['id'] = self._id
        for removeField in remove:
            if removeField in result:
                del result[removeField]
        return result

    def set(self, **kwargs):
        _data = copy.deepcopy(self.data)
        for field in kwargs:
            splitField = field.split("__")
            base = _data
            for idx, val in enumerate(splitField):
                base[val] = {}
                if idx+1 < len(splitField):
                    base = base[val]
            base[val] = kwargs[field]
        self.data = self._loadDataInner({}, copy.deepcopy(self.data), _data)

    def put(self, indices = None):
        data = copy.deepcopy(self.data)
        if self._id is None:
            sql = "INSERT INTO %(table)s (id,body,created,updated) VALUES(%(args)s)" % {'table' : self.table, 'args' : '%s,%s,NOW(),NOW()'}
            self._id = Database.get().execute(sql, None, json.dumps(data))
        else:
            sql = "UPDATE %(table)s SET body = %(arg)s, updated = NOW() WHERE id = %(arg)s" % {'table' : self.table, 'arg' : '%s'}
            Database.get().execute(sql, json.dumps(data), self._id )
        # load updated created
        sql = "SELECT created, updated FROM %(table)s WHERE id = %(arg)s " % {'table' : self.table, 'arg' : '%s'}
        result = Database.get().get(sql, self._id)
        self._created = result['created']
        self._updated = result['updated']
        if indices is None:
            for index in self.indices:
                index.put(self)
        else:
            for index in indices:
                index.put(self)

    def delete(self):
        for index in self.indices:
            index.delete(self)
        sql = "DELETE FROM %(table)s WHERE id = %(args)s" % {'table' : self.table, 'args' : '%s'}
        Database.get().execute(sql, self._id)
        self._id = None
        self._created = None
        self._updated = None

    @classmethod
    def _loadFromId(cls, id):
        if id is not None:
            sql = "SELECT id, body, created, updated FROM %(table)s WHERE id = %(args)s" % { 'table' : cls.table, 'args' : '%s' }
            result = Database.get().get(sql, id)
            model = cls(json.loads(result['body']))
            model._id = result['id']
            model._updated = result['updated']
            model._created = result['created']
            return model

    @classmethod
    def _loadAll(cls, fql, query, *args):
        if query is not None and fql.paramList == [] and "limit " in query.strip().lower():
            query = query
        elif query != '' and query is not None:
            query = " WHERE %(query)s" % {'query' : query }
        elif query is None:
            query = ''
        sql = "SELECT id, body FROM %(table)s %(query)s" % { 'table' : cls.table, 'query' : query }
        result = Database.get().query(sql, *args)
        objects = []
        for row in result:
            model = cls(json.loads(row['body']))
            model._id = row['id']
            objects.append(model)
        return objects

    @classmethod
    def _loadGet(cls, query, *args):
        sql = "SELECT id, body, created, updated FROM %(table)s WHERE %(query)s" % { 'table' : cls.table, 'query' : query }
        result = Database.get().get(sql, *args)
        if result is None:
            return None
        model = cls(json.loads(result['body']))
        model._id = result['id']
        model._created = result['created']
        model._updated = result['updated']
        return model


    @classmethod
    def fqlGet(cls, query, *args):
        fql = Fql(query)
        index = fql.determineIndex(cls.indices)
        if fql.paramList == [] and query.strip() != '':
            return cls._loadGet(query, *args)
        if index is None:
            raise Exception("NO_INDEX_HIT")
        return cls._loadFromId(index.get(query, *args))

    @classmethod
    def fqlAll(cls, query = None, *args):
        fql = Fql(query)
        index = fql.determineIndex(cls.indices)
        if fql.paramList == []:
            return cls._loadAll(fql, query, *args)
        if index is None:
            raise Exception("NO_INDEX_HIT")
        ids = index.all(query, *args)
        for idx, val in enumerate(ids):
            ids[idx] = cls._loadFromId(val)
        return ids


"""
Class CleanKeeper
"""
from datetime import datetime
from calendar import timegm
import time

class Cleaner():

    def _setTimeEpoch(self, dttm = None):
        if dttm is None:
            dttm = datetime.utcnow()
        self.timeEpoch = timegm(dttm.utctimetuple())
        self.timeEpochString = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timeEpoch + 3600))

    def cleanModel(self, model, indices = None, dttm = None):
        self._setTimeEpoch(dttm)
        result = model.fqlAll('updated <= %s', self.timeEpochString)
        for row in result:
            row.put(indices)

