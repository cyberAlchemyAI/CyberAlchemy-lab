"""Pure schema syntax cache never caches source, dependency or instance verdicts."""
import unittest
from episode import *


class SchemaCacheGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context=engine(EnginePins(**parse((HERE/'pins.json').read_bytes())))
        cls.handle=cls.context.__enter__()
    @classmethod
    def tearDownClass(cls):cls.context.__exit__(None,None,None)
    def setUp(self):
        self.sources=self.handle.sources;self.sources.checked_schema_syntax.cache_clear()
        self.documents={'schema.json':{'type':'integer'}}
    def validate(self,value):self.sources.validate_schema(value,'schema.json',None,self.documents)
    def test_identical_syntax_reused(self):
        self.validate(1);self.validate(2);info=self.sources.checked_schema_syntax.cache_info()
        self.assertEqual((info.misses,info.hits,info.maxsize),(1,1,128))
    def test_invalid_instance_checked_after_cache_hit(self):
        self.validate(1)
        with self.assertRaises(Exception):self.validate('wrong')
        self.assertEqual(self.sources.checked_schema_syntax.cache_info().hits,1)
    def test_changed_schema_syntax_rechecked(self):
        self.validate(1);self.documents['schema.json']={'type':'unrecognized-type'}
        with self.assertRaises(Exception):self.validate(1)
        self.assertEqual(self.sources.checked_schema_syntax.cache_info().misses,2)
    def test_changed_valid_schema_changes_instance_verdict(self):
        self.validate(1);self.documents['schema.json']={'type':'string'}
        with self.assertRaises(Exception):self.validate(1)
        self.validate('valid');self.assertEqual(self.sources.checked_schema_syntax.cache_info().misses,2)
    def test_changed_dependency_changes_instance_verdict(self):
        self.documents={'schema.json':{'$ref':'dependency.json'},'dependency.json':{'type':'integer'}}
        self.validate(1);self.documents['dependency.json']={'type':'string'}
        with self.assertRaises(Exception):self.validate(1)
        self.assertEqual(self.sources.checked_schema_syntax.cache_info().hits,1)
    def test_removed_dependency_rejected_even_with_syntax_cached(self):
        self.documents={'schema.json':{'$ref':'dependency.json'},'dependency.json':{'type':'integer'}}
        self.validate(1);self.documents.pop('dependency.json')
        with self.assertRaises(Exception):self.validate(1)
    def test_remote_dependency_rejected(self):
        self.documents={'schema.json':{'$ref':'https://example.org/schema.json'}}
        with self.assertRaises(Exception):self.validate(1)
    def test_exact_selector_schema_rechecked(self):
        self.documents={'schema.json':{'$defs':{'selected':{'type':'integer'}}}}
        self.sources.validate_schema(1,'schema.json','#/$defs/selected',self.documents)
        self.documents['schema.json']['$defs']['selected']['type']='string'
        with self.assertRaises(Exception):self.sources.validate_schema(1,'schema.json','#/$defs/selected',self.documents)
    def test_cache_capacity_bounded(self):
        for n in range(129):self.sources.checked_schema_syntax(encoded({'const':n}))
        self.assertEqual(self.sources.checked_schema_syntax.cache_info().currsize,128)


if __name__=='__main__':unittest.main()
