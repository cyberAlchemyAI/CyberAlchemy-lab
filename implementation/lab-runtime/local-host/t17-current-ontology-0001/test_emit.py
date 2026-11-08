"""Pure selected-recipe and mapper-origin tests, no native projection claim."""
import ast
import copy
import hashlib
import json
from pathlib import Path
from types import ModuleType,SimpleNamespace
import unittest
from emit import ROOT,ORIGINAL,transform,HEADER_HELPER,ORIGIN_HELPER


def require(value,message):
    if not value:raise ValueError(message)


class CurrentOntology(unittest.TestCase):
    def setUp(self):
        self.root=Path('/tmp/synthetic-qualified-mapper')
        self.mapper=ModuleType('_synthetic_current_mapper');self.mapper.__file__=str(self.root/'build.py');self.mapper.HERE=self.root
        self.namespace={'require':require,'Path':Path,'MAPPER':self.root,'MAPPER_EXECUTION':self.root,
            'SOURCE':SimpleNamespace(current_legacy_delivery=lambda:SimpleNamespace(MAPPED=self.mapper))}
        exec(HEADER_HELPER+ORIGIN_HELPER,self.namespace)
        self.mapping={'rows':[{'subject_identity':{'subject_kind':'node' if i<18 else 'edge'},
            'artifact':{'version_ref':'fixture:source:'+str(i)+'@1'}} for i in range(30)]}

    def test_complete_exact_current_recipe(self):
        self.assertEqual(len(self.namespace['selected_mapping_headers'](self.mapping)),30)
        self.assertIs(self.namespace['selected_mapper'](self.mapper),self.mapper)

    def test_missing_extra_or_duplicate_original_refuses(self):
        for rows in (self.mapping['rows'][:-1],self.mapping['rows']+[self.mapping['rows'][0]],
                     self.mapping['rows'][:-1]+[self.mapping['rows'][0]]):
            with self.assertRaises(ValueError):self.namespace['selected_mapping_headers']({'rows':rows})

    def test_wrong_node_edge_contract_refuses(self):
        changed=copy.deepcopy(self.mapping);changed['rows'][0]['subject_identity']['subject_kind']='edge'
        with self.assertRaises(ValueError):self.namespace['selected_mapping_headers'](changed)

    def test_same_path_foreign_object_and_wrong_module_origin_refuse(self):
        fake=SimpleNamespace(__file__=self.mapper.__file__,HERE=self.root)
        with self.assertRaises(ValueError):self.namespace['selected_mapper'](fake)
        self.mapper.__file__=str(self.root/'foreign.py')
        with self.assertRaises(ValueError):self.namespace['selected_mapper'](self.mapper)

    def test_original_owned_apply_and_cold_replay_logic_unchanged(self):
        old=ast.parse(ORIGINAL.read_bytes());new=ast.parse(transform(ORIGINAL.read_bytes()))
        def classes(tree):return next(n for n in tree.body if isinstance(n,ast.ClassDef))
        x,y=classes(old),classes(new)
        # apply only retargets the selected Source delivery used by hydration;
        # all locks, byte comparisons, native calls, publication and deadlines stay.
        ox=next(n for n in x.body if isinstance(n,ast.FunctionDef) and n.name=='apply')
        ny=next(n for n in y.body if isinstance(n,ast.FunctionDef) and n.name=='apply')
        class RestoreDelivery(ast.NodeTransformer):
            def visit_Attribute(self,node):
                if node.attr=='current_legacy_delivery':node.attr='custody_delivery'
                return self.generic_visit(node)
        self.assertEqual(ast.dump(ox,include_attributes=False),ast.dump(RestoreDelivery().visit(ny),include_attributes=False))
        for name in ('head','cut','check_deadline'):
            a=next(n for n in x.body if isinstance(n,ast.FunctionDef) and n.name==name)
            b=next(n for n in y.body if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))

    def test_actual_selected_mapping_originals_hydrate_all_18_nodes_and_12_edges(self):
        # Actual already produced Mapper originals, not an executed native
        # projection or a substitute for its future permission/commit proof.
        family=ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d'
        package=family/'mapped/packages/0001'
        manifest_raw=(package/'manifest.json').read_bytes()
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(),'311b1f0c982b2a64b0148b85f6c9add49b281bf945c97e5ffa7162464ed15419')
        manifest=json.loads(manifest_raw)
        for row in manifest['files']:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(),row['sha256'])
        mapping=json.loads((package/'mapping.json').read_bytes())
        files={p.relative_to(package).as_posix():p.read_bytes() for name in ('semantic','governance') for p in (package/name).glob('*.json')}
        # The exact original template constructor is pure and schema-backed.
        context=ast.parse((family/'context/generation.py').read_bytes())
        functions=[n for n in context.body if isinstance(n,ast.FunctionDef) and n.name in ('fixture','common')]
        namespace={'ROOT':ROOT,'load':lambda p:json.loads(Path(p).read_bytes()),
            'CARRIERS':{'ontology-node':'v2','ontology-edge':'v1'},
            'records':SimpleNamespace(PRINCIPAL='principal:fixture'),'CLAIM':'Original template hydration component only.'}
        exec(compile(ast.Module(body=functions,type_ignores=[]),str(family/'context/generation.py'),'exec'),namespace)
        producer=SimpleNamespace(common=namespace['common'],MAPPED=SimpleNamespace(ONTOLOGY='ontology:completion-legacy-local-4636eca980a5d94d-domain-projection:v3'))
        source=SimpleNamespace(current_legacy_delivery=lambda:producer,parse=json.loads,
            sha=lambda raw:hashlib.sha256(raw).hexdigest(),encoded=lambda value:(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode())
        tree=ast.parse(transform(ORIGINAL.read_bytes()))
        rich=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='rich_carriers')
        ns={'SOURCE':source,'CLAIM':'Actual retained Mapper original hydration component test only.','require':require}
        exec(compile(ast.Module(body=[rich],type_ignores=[]),str(ORIGINAL),'exec'),ns)
        bodies,nodes,edges,correspondence=ns['rich_carriers'](mapping,files,'scope:hydration-component','fixture:manifest','principal:fixture')
        self.assertEqual((len(nodes),len(edges),len(bodies),len(correspondence)),(18,12,30,30))
        from jsonschema import Draft202012Validator
        for body in bodies.values():
            version='v2' if body['kind']=='ontology-node' else 'v1'
            schema=json.loads((ROOT/'authority/artifact-types'/body['kind']/version/'schema.json').read_bytes())
            Draft202012Validator(schema).validate(body)
        changed=copy.deepcopy(files);name=next(n for n in changed if n.startswith('governance/'))
        value=json.loads(changed[name]);value['semantic_ref']['semantic_event_digest']='0'*64
        changed[name]=json.dumps(value).encode()
        with self.assertRaisesRegex(ValueError,'exact governance join'):
            ns['rich_carriers'](mapping,changed,'scope:hydration-component','fixture:manifest','principal:fixture')


if __name__=='__main__':unittest.main()
