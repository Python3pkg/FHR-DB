import unittest
import json
import os

from tornado.options import define, options
from tests.base import BaseDbTest

from fhr_db.fhr_db import Database
from fhr_db.fhr_db import Index, Model, Fql, Cleaner

define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="paidanswerstest", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="", help="database password")

# simple model class with interface for index more not needed
class SimpleIndexInterface():

    def __init__(self):
        self._id = 10
        self.data = {'field1' : 'field1', 'field2' : 'field2'}

class TestIndex(BaseDbTest):

    def test_init(self):
        index = Index("index", "t", "e")
        self.assertEqual(index.indexOrIndices, ["index"])
        self.assertEqual(index.indexTable, "t")
        self.assertEqual(index.entityField, "e")

    def test_put_single(self):
        index = Index("field1", "simple_field1_index", "simple_id")
        model = SimpleIndexInterface()
        index.put(model)
        result = Database.get().get("SELECT field1 FROM simple_field1_index WHERE simple_id = %s", model._id)
        self.assertNotEqual(result, None)
        self.assertEqual(result['field1'], 'field1')

    def test_put_single_none(self):
        index = Index("field1", "simple_field1_index", "simple_id")
        model = SimpleIndexInterface()
        model.data['field1'] = None
        index.put(model)
        result = Database.get().get("SELECT field1 FROM simple_field1_index WHERE simple_id = %s", model._id)
        self.assertEqual(result, None)

    def test_put_single_2x(self):
        index = Index("field1", "simple_field1_index", "simple_id")
        model = SimpleIndexInterface()
        index.put(model)
        model.data['field1'] = 'neu'
        index.put(model)
        result = Database.get().get("SELECT field1 FROM simple_field1_index WHERE simple_id = %s", model._id)
        self.assertNotEqual(result, None)
        self.assertEqual(result['field1'], 'neu')

    def test_put_dobule(self):
        index = Index(["field1", "field2"], "simple_field_double_index", "simple_id")
        model = SimpleIndexInterface()
        index.put(model)
        result = Database.get().get("SELECT field1, field2 FROM simple_field_double_index WHERE simple_id = %s", model._id)
        self.assertEqual(result['field1'], 'field1')
        self.assertEqual(result['field2'], 'field2')

    def test_put_single_inner_dict(self):
        index = Index(["field1.inner"], "simple_inner_index", "simple_id")
        model = SimpleIndexInterface()
        model.data['field1'] = {'inner' : 'innerValue'}
        index.put(model)
        result = Database.get().get("SELECT field1_inner FROM simple_inner_index WHERE simple_id = %s", model._id)
        self.assertEqual(result['field1_inner'], 'innerValue')


class SimpldeMOdel(Model):

    fields = {}

class SimpleModelWithUpdated(Model):
    fields = {'new' : 'new', 'email' : {'token' : { 'field': 'test'}}}
    table = 'complex_inner_model'
    indices = [Index(["updated"], "simple_updated_index", "simple_id")]

class SimpleModelWithCreated(Model):
    fields = {'new' : 'new', 'email' : {'token' : { 'field': 'test'}}}
    table = 'complex_inner_model'
    indices = [Index(["created"], "simple_created_index", "simple_id")]

class ComplexModel(Model):

    fields = {'field' : 'field', 'field2' : 'field2'}

class ComplexInnerModel(Model):

    fields = {'new' : 'new', 'email' : {'token' : 'test'}}
    table = 'complex_inner_model'
    indices = [Index(["email.token"], "simple_token_index", "simple_id"), Index(["new"], "simple_new_index", "simple_id")]

class ComplexComplexInnerModel(Model):

    fields = {'new' : 'new', 'email' : {'token' : { 'field': 'test'}}}
    table = 'complex_inner_model'

class Complex2InnerModel(Model):

    fields = {'new' : 'new', 'email' : {'token' : 'test', 'other_token' : 'test1'}}
    table = 'complex_inner_model'


class ComplexInnerModelWithLists(Model):
    fields = {'new' : [], 'new2': [], 'new3': [], 'email' : {'token' : []}}
    table = 'complex_inner_model'
    indices = [Index(["new"], "simple_new_index", "simple_id"),
               Index(["email.token"], "simple_token_index", "simple_id")]


class ComplexInnerModelWith2Lists(Model):
    fields = {'new' : [], 'new2': []}
    table = 'complex_inner_model'
    indices = [Index(["new", "new2"], "simple_new_new2_index", "simple_id")]

class ComplexModelWith2List1Normal(Model):
    fields = {'new' : [], 'new2': [], 'new3' : 'normal'}
    table = 'complex_inner_model'
    indices = [Index(["new", "new3", "new2"], "simple_new_new2_new3_index", "simple_id")]


class TestModel(BaseDbTest):
    def test_init(self):
        model = ComplexModel()
        self.assertEquals(model._id, None)

    def test_set_fields(self):
        model = ComplexModel()
        self.assertEquals(model.data['field'], 'field')

    def test_set_fields_not_known(self):
        model = ComplexModel(data={'unknown_field' : None})
        self.assertEquals(False, 'unknown_field' in model.data)

    def test_data_loaded(self):
        model = ComplexModel(data={'field' : 1})
        self.assertEquals(model.data['field'], 1)

    def test_get(self):
        model = ComplexModel(data={'field' : 1})
        self.assertEquals(model.get('field'), 1)

    def test_get_all(self):
        model = ComplexModel(data={'field' : 1})
        self.assertEquals(model.get(), {'id' : None, 'field' : 1, 'field2' : 'field2'})

    def test_get_remove(self):
        model = ComplexModel(data={'field1' : 1})
        self.assertEquals(model.get(remove=['field']), {'id': None, 'field2' : 'field2'})

    def test_inner_get(self):
        model = ComplexInnerModel()
        self.assertEquals(model.get('email.token'), 'test')

    def test_set(self):
        model = ComplexInnerModel()
        model.set(new='old')
        self.assertEquals(model.get('new'), 'old')

    def test_set_inner(self):
        model = ComplexInnerModel()
        model.set(email__token='old_token')
        self.assertEquals(model.get('email.token'), 'old_token')

    def test_set_inner_complete(self):
        model = ComplexInnerModel()
        model.set(email={'token' : 'old_token'})
        self.assertEquals(model.get('email.token'), 'old_token')

    def test_put_insert(self):
        model = ComplexInnerModel()
        model.put()
        sql = "SELECT body FROM  %(table)s  WHERE id = %(id)s" % {'table' : model.table, 'id' : '%s' }
        result = Database.get().get(sql, model._id)
        self.assertEquals(json.loads(result['body']), model.get(remove=['id']))

    def test_put_save(self):
        model = ComplexInnerModel()
        model.put()
        model.set(new='old')
        model.put()
        sql = "SELECT body FROM  %(table)s  WHERE id = %(id)s" % {'table' : model.table, 'id' : '%s' }
        result = Database.get().get(sql, model._id)
        self.assertEquals(json.loads(result['body'])['new'], 'old')
        self.assertEquals(json.loads(result['body']), model.get(remove=['id']))

    def test_put_index(self):
        model = ComplexInnerModel()
        model.put()
        sql = "SELECT email_token FROM simple_token_index WHERE simple_id = %s"
        result = Database.get().get(sql, model._id)
        self.assertEquals(result['email_token'], model.get('email.token'))

    def test_get_fql_no_index_hit(self):
        with self.assertRaises(Exception) as cmd:
            ComplexInnerModel.fqlGet("")
        self.assertEquals(str(cmd.exception), "NO_INDEX_HIT")

    def test_get_fql_no_index_hit_but_value(self):
        with self.assertRaises(Exception) as cmd:
            ComplexInnerModel.fqlGet("test",3)
        self.assertEquals(str(cmd.exception), "NO_INDEX_HIT")

    def test_get_fql_index_hit(self):
        result = ComplexInnerModel.fqlGet("email.token = 3")
        self.assertEquals(result, None)

    def test_get_fql_index_hit_none(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlGet("email.token = %s", 5)
        self.assertEquals(result, None)

    def test_get_fql_index_hit_value(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlGet("email.token = %s", "test")
        self.assertEquals(result.get('email.token'), "test")
        self.assertEquals(result._id, model._id)

    def test_get_fql_all_index_hit_none(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlAll("email.token = %s", 5)
        self.assertEquals(result, [])

    def test_get_fql__all_index_hit_value(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlAll("email.token = %s", "test")
        self.assertEquals(result[0].get('email.token'), "test")
        self.assertEquals(result[0]._id, model._id)

    def test_get_fql_all_all(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        model = ComplexInnerModel({'email' : {'token' : 'test1'}})
        model.put()
        result = ComplexInnerModel.fqlAll()
        self.assertEqual(len(result), 2)

    def test_get_fql_all_limit(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        model = ComplexInnerModel({'email' : {'token' : 'test1'}})
        model.put()
        model = ComplexInnerModel({'email' : {'token' : 'test2'}})
        model.put()
        result = ComplexInnerModel.fqlAll("LIMIT %s", 2)
        self.assertEqual(len(result), 2)
        result = ComplexInnerModel.fqlAll()
        self.assertEqual(len(result), 3)

    def test_get_fql_get_id(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlGet("id = %s", model._id)
        self.assertNotEquals(result, None)

    def test_get_fql_get__all_id(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlAll("id = %s", model._id)
        self.assertEquals(len(result), 1)

    def test_delete(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlAll("id = %s", model._id)
        self.assertEquals(len(result), 1)
        model.delete()
        self.assertEquals(model._id, None)
        result = ComplexInnerModel.fqlAll("id = %s", model._id)
        self.assertEquals(len(result), 0)

    def test_delete_with_index(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlAll("email.token = %s", "test")
        self.assertEquals(len(result), 1)
        model.delete()
        result = ComplexInnerModel.fqlAll("email.token = %s", "test")
        self.assertEquals(len(result), 0)


    def test_inner_model_should_not_be_none(self):
        with self.assertRaises(Exception) as cmd:
            ComplexInnerModel({'email' : None})
        self.assertEquals(str(cmd.exception), "DICT_CAN_NOT_BE_NULL")

    def test_inner_model_must_be_dict(self):
        with self.assertRaises(Exception) as cmd:
            ComplexInnerModel({'email' : 'as'})
        self.assertEquals(str(cmd.exception), "DICT_CAN_NOT_BE_PRIMITIVE")

    def test_inner_model_set_standard_values(self):
        model = ComplexInnerModel({'email' : {'unknown' : True }})
        self.assertEquals(model.get('email'), {'token' : 'test'})

    def test_inner_model_set_values(self):
        model = ComplexInnerModel({'email' : {'token' : 'neu' }})
        self.assertEquals(model.get('email'), {'token' : 'neu'})

    def test_inner_inner_model_must_dict(self):
        with self.assertRaises(Exception) as cmd:
            ComplexComplexInnerModel({'email' : {'token' : True }})
        self.assertEquals(str(cmd.exception), "DICT_CAN_NOT_BE_PRIMITIVE")

    def test_inner_inner_model_should_not_be_none(self):
        with self.assertRaises(Exception) as cmd:
            ComplexComplexInnerModel({'email' : {'token' : None }})
        self.assertEquals(str(cmd.exception), "DICT_CAN_NOT_BE_NULL")

    def test_inner_inner_model_set_standard_values(self):
        model = ComplexComplexInnerModel({'email' : {'token' : {'unknonw' : 'unknown'} }})
        self.assertEquals(model.get('email'), {'token' : {'field' : 'test'}})

    def test_inner_inner_model_set_values(self):
        model = ComplexComplexInnerModel({'email' : {'token' : {'field' : 'neu'} }})
        self.assertEquals(model.get('email'), {'token' : {'field' : 'neu'}})

    def test_fields_have_the_same_standard_value_after_set(self):
        model = ComplexInnerModel({'new' : '123' })
        model.set(email__token = 'neu1')
        self.assertEquals(model.get('email.token'), 'neu1')
        model1 = ComplexInnerModel()
        self.assertEquals(model1.get('email.token'), 'test')

    def test_fields_2_time_set(self):
        model = ComplexInnerModel({'new' : '123' })
        model.put()
        model.set(email__token='neu1')
        self.assertEquals(model.get('email.token'), 'neu1')
        self.assertEquals(model.get('new'), '123')

    def test_fields_inner_non_standard(self):
        model = ComplexInnerModel({'new' : '123' })
        model.set(email={'token1' : 'notstandard'})
        self.assertEquals(model.get('email.token'), 'test')
        self.assertEquals(model.get('email'), {'token' : 'test'})

    def test_fields_inner_2_set(self):
        model = Complex2InnerModel({'email' : {'token' : 'newvalue' }})
        self.assertEquals(model.get('email.token'), 'newvalue')
        model.set(email__other_token='hallo')
        self.assertEquals(model.get('email.other_token'), 'hallo')
        self.assertEquals(model.get('email.token'), 'newvalue')

    def test_id_reserved(self):
        class IdReserved(Model):
            fields = {'id' : None}
        with self.assertRaises(Exception) as cmd:
            IdReserved()
        self.assertEquals(str(cmd.exception), "ID_IS_RESERVED")

    def test_id_reserved_not_in_inner(self):
        class IdReservedNotInner(Model):
            fields = {'test' : {'id' : None} }
        model = IdReservedNotInner()
        self.assertEquals(model.get('test.id'), None)

    def test_created_reserved(self):
        class CreatedReserved(Model):
            fields = {'created' : None}
        with self.assertRaises(Exception) as cmd:
            CreatedReserved()
        self.assertEquals(str(cmd.exception), "CREATED_IS_RESERVED")

    def test_updated_reserved(self):
        class CreatedReserved(Model):
            fields = {'updated' : None}
        with self.assertRaises(Exception) as cmd:
            CreatedReserved()
        self.assertEquals(str(cmd.exception), "UPDATED_IS_RESERVED")

    def test_created_set(self):
        model = ComplexInnerModel()
        model.put()
        sql = "SELECT created FROM %(table)s WHERE id = %(arg)s" % {'table' : model.table, 'arg' : "%s"}
        result = Database.get().get(sql, model.get('id'))
        self.assertEquals(model.get('created'), result['created'])

    def test_updated_set(self):
        model = ComplexInnerModel()
        model.put()
        sql = "SELECT updated FROM %(table)s WHERE id = %(arg)s" % {'table' : model.table, 'arg' : "%s"}
        result = Database.get().get(sql, model.get('id'))
        self.assertEquals(model.get('updated'), result['updated'])

    def test_get_fql_get_updated(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlGet("updated <= %s", model.get('updated'))
        self.assertNotEquals(result, None)

    def test_get_fql_get_created(self):
        model = ComplexInnerModel({'email' : {'token' : 'test'}})
        model.put()
        result = ComplexInnerModel.fqlGet("created >= %s", model.get('created'))
        self.assertNotEquals(result, None)

    def test_simple_model_with_empty_list(self):
        model = ComplexInnerModelWithLists()
        model.put()
        sql = "SELECT id FROM simple_token_index WHERE simple_id = %s"
        result = Database.get().get(sql, model.get('id'))
        self.assertEquals(result, None)

    def test_simple_model_with_1_list(self):
        model = ComplexInnerModelWithLists()
        model.set(new=[1])
        model.put()
        sql = "SELECT id FROM simple_new_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 1)

    def test_simple_model_with_2_list(self):
        model = ComplexInnerModelWithLists()
        model.set(new=[1,2])
        model.put()
        sql = "SELECT id FROM simple_new_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 2)

    def test_simple_model_with_string_to_list(self):
        model = ComplexInnerModelWithLists()
        with self.assertRaises(Exception) as cmd:
            model.set(new='als')
        self.assertEquals(str(cmd.exception), "SHOULD_BE_LIST")

    def test_complex_model_with_empty_list(self):
        model = ComplexInnerModelWithLists()
        model.put()
        sql = "SELECT id FROM simple_token_index WHERE simple_id = %s"
        result = Database.get().get(sql, model.get('id'))
        self.assertEquals(result, None)

    def test_complex_model_with_string_to_list(self):
        model = ComplexInnerModelWithLists()
        with self.assertRaises(Exception) as cmd:
            model.set(email__token='als')
        self.assertEquals(str(cmd.exception), "SHOULD_BE_LIST")

    def test_complex_model_with_1_list(self):
        model = ComplexInnerModelWithLists()
        model.set(email__token=[1])
        model.put()
        sql = "SELECT id FROM simple_token_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 1)

    def test_complex_model_with_2_list(self):
        model = ComplexInnerModelWithLists()
        model.set(email__token=[1,2])
        model.put()
        sql = "SELECT id FROM simple_token_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 2)

    def test_complex_model_with_2_list_2_saves(self):
        model = ComplexInnerModelWithLists()
        model.set(email__token=[1,2])
        model.put()
        model.set(email__token=[2,3,4])
        model.put()
        sql = "SELECT id FROM simple_token_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 3)

    def test_complex_model_with_2list_empty(self):
        model = ComplexInnerModelWith2Lists()
        model.put()
        sql = "SELECT id FROM simple_new_new2_index WHERE simple_id = %s"
        result = Database.get().get(sql, model.get('id'))
        self.assertEquals(result, None)

    def test_complex_model_with_2list_1_empty(self):
        model = ComplexInnerModelWith2Lists()
        model.set(new=['fuck'])
        model.put()
        sql = "SELECT id FROM simple_new_new2_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 0)

    def test_complex_model_with_2list_1_element(self):
        model = ComplexInnerModelWith2Lists()
        model.set(new=[1], new2=[2])
        model.put()
        sql = "SELECT id FROM simple_new_new2_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 1)

    def test_complex_model_with_2list_2_elements(self):
        model = ComplexInnerModelWith2Lists()
        model.set(new=[1,2], new2=[3,4])
        model.put()
        sql = "SELECT new, new2 FROM simple_new_new2_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 4)
        expectedResult = [{'new' : '1', 'new2' : '3'}, {'new' : '1', 'new2' : '4'}, {'new' : '2', 'new2' : '3'}, {'new' : '2', 'new2' : '4'}]
        self.assertEquals(result, expectedResult)

    def test_complex_model_with_2list_12_elements(self):
        model = ComplexInnerModelWith2Lists()
        model.set(new=[1,2], new2=[3])
        model.put()
        sql = "SELECT id FROM simple_new_new2_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 2)

    def test_complex_model_with_2_list_2_elements_and_scalar(self):
        model = ComplexModelWith2List1Normal()
        model.set(new=[1,2], new2=[3,4])
        model.put()
        sql = "SELECT new, new2, new3 FROM simple_new_new2_new3_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(len(result), 4)
        expectedResult = [{'new' : '1', 'new2' : '3', 'new3' : 'normal'}, {'new' : '1', 'new2' : '4', 'new3' : 'normal'}, {'new' : '2', 'new2' : '3', 'new3' : 'normal'}, {'new' : '2', 'new2' : '4', 'new3' : 'normal'}]
        self.assertEquals(result, expectedResult)

    def test_complex_model_with_2_list_2_elements_and_scalar_and_overwrite(self):
        model = ComplexModelWith2List1Normal()
        model.set(new=[1,2], new2=[3,4])
        model.put()
        model.set(new=[1], new2=[3])
        model.put()
        sql = "SELECT new, new2, new3 FROM simple_new_new2_new3_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        expectedResult = [{'new' : '1', 'new2' : '3', 'new3' : 'normal'}]
        self.assertEquals(result, expectedResult)

    def test_index_with_updated_in_it(self):
        model = SimpleModelWithUpdated()
        model.set(new=[1])
        model.put()
        sql = "SELECT updated FROM simple_updated_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(model._updated, result[0]['updated'])

    def test_index_with_created_in_it(self):
        model = SimpleModelWithCreated()
        model.set(new=[1])
        model.put()
        sql = "SELECT created FROM simple_created_index WHERE simple_id = %s"
        result = Database.get().query(sql, model.get('id'))
        self.assertEquals(model._updated, result[0]['created'])

class TestFql(unittest.TestCase):

    def test_query(self):
        fql = Fql("")
        self.assertEquals(fql.paramList, [])

    def test_query_field(self):
        fql = Fql("field > field2")
        self.assertEquals(fql.paramList, ['field', 'field2'])

    def test_inner_query(self):
        fql = Fql("field.id > field2")
        self.assertEquals(fql.paramList, ['field.id', 'field2'])

    def test_inner_query_underscore(self):
        fql = Fql("field_test.id > field2")
        self.assertEquals(fql.paramList, ['field_test.id', 'field2'])

    def test_inner_query_procent_s(self):
        fql = Fql("field > %s")
        self.assertEquals(fql.paramList, ['field'])

    def test_double(self):
        fql = Fql("field > field")
        self.assertEquals(fql.paramList, ['field'])

    def test_determin_noindex(self):
        fql = Fql("field > field")
        index = fql.determineIndex([])
        self.assertEquals(index, None)

    def test_determine_no_index_field(self):
        fql = Fql("")
        index = fql.determineIndex([])
        self.assertEquals(index, None)

    def test_determine_direct_hit(self):
        fql = Fql("field > %s")
        index_1 = Index(["field"], "simple_inner_index", "simple_id")
        index = fql.determineIndex([index_1])
        self.assertEquals(index, index_1)

    def test_determine_direct_hit(self):
        fql = Fql("field > %s")
        index_1 = Index(["field"], "simple_inner_index", "simple_id")
        index_2 = Index(["field2"], "simple_inner_index", "simple_id")
        index = fql.determineIndex([index_1, index_2])
        self.assertEquals(index, index_1)

    def test_determine_direct_hit_2_fields(self):
        fql = Fql("field1 > field2")
        index_1 = Index(["field"], "simple_inner_index", "simple_id")
        index_2 = Index(["field2"], "simple_inner_index", "simple_id")
        index_3 = Index(["field1", "field2"], "simple_inner_index", "simple_id")
        index = fql.determineIndex([index_1, index_2, index_3])
        self.assertEquals(index, index_3)


import time

class TestCleaner(BaseDbTest):

    def test_cleaner_update_all(self):
        model = ComplexInnerModel()
        model.put()
        cleaner = Cleaner()
        time.sleep(2)
        cleaner.cleanModel(ComplexInnerModel)
        newModel = ComplexInnerModel.fqlGet('id = %s', model.get('id'))
        self.assertNotEquals(model.get('updated'), newModel.get('updated'))

    def test_cleaner_update_both_index(self):
        model = ComplexInnerModel()
        model.put()
        sql = "DELETE FROM simple_token_index"
        Database.get().execute(sql)
        sql = "DELETE FROM simple_new_index"
        Database.get().execute(sql)
        cleaner = Cleaner()
        cleaner.cleanModel(ComplexInnerModel)
        self.assertEquals(1, len(Database.get().query('SELECT id FROM simple_token_index')))
        self.assertEquals(1, len(Database.get().query('SELECT id FROM simple_new_index')))

    def test_cleaner_update_one_index(self):
        model = ComplexInnerModel()
        model.put()
        sql = "DELETE FROM simple_token_index"
        Database.get().execute(sql)
        sql = "DELETE FROM simple_new_index"
        Database.get().execute(sql)
        cleaner = Cleaner()
        cleaner.cleanModel(ComplexInnerModel, [ComplexInnerModel.indices[0]])
        self.assertEquals(1, len(Database.get().query('SELECT id FROM simple_token_index')))
        self.assertEquals(0, len(Database.get().query('SELECT id FROM simple_new_index')))


def main():
    options.parse_command_line()
    options.mysql_database = BaseDbTest.dbName
    BaseDbTest.dbFile = '%s/fhr_tables.sql' % os.path.dirname(os.path.abspath(__file__))
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFql)
    unittest.TextTestRunner(verbosity=1).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
    unittest.TextTestRunner(verbosity=1).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModel)
    unittest.TextTestRunner(verbosity=1).run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestCleaner)
    unittest.TextTestRunner(verbosity=1).run(suite)

if __name__ == "__main__":
    main()
