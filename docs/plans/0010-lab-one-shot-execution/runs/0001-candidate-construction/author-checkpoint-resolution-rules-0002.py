"""Retain the failed v1 run and resolve only byte-identical schema copies."""
import ast
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'checkpoint-resolution-rules-v1';NEW=BASE/'checkpoint-resolution-rules-v2'
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not NEW.exists()
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json'))
    p=NEW/'rules.py';s=p.read_text()
    s=s.replace('resources=[];self.schemas={}','resources=[];self.schemas={};self.schema_originals={}',1)
    before="""                value=parse((ROOT/row['path']).read_bytes())
                if '$id' in value:
                    require(value['$id'] not in self.schemas,'duplicate selected schema identity')
                    self.schemas[value['$id']]=value
                    resources.append((value['$id'],Resource.from_contents(value,default_specification=DRAFT202012)))"""
    assert s.count(before)==1
    s=s.replace(before,"                self.register_original_schema((ROOT/row['path']).read_bytes(),resources)",1)
    needle='    def valid(self,uri,value):'
    helper="""    def register_original_schema(self,raw,resources):
        value=parse(raw)
        if '$id' not in value:return
        identity=value['$id']
        if identity in self.schema_originals:
            require(self.schema_originals[identity]==raw,'conflicting original schema identity')
            return
        self.schema_originals[identity]=raw;self.schemas[identity]=value
        resources.append((identity,Resource.from_contents(value,default_specification=DRAFT202012)))
"""
    assert s.count(needle)==1;p.write_text(s.replace(needle,helper+needle,1))
    p=NEW/'test_rules.py';s=p.read_text();needle="if __name__=='__main__':unittest.main()"
    extra="""    def test_46_byte_identical_schema_copies_share_one_resource(self):
        f=self.example();resources=[];raw=E.encoded({'$id':'urn:fixture:schema-copy','type':'object'})
        f.engine.register_original_schema(raw,resources);f.engine.register_original_schema(raw,resources)
        self.assertEqual(len(resources),1)
    def test_47_similar_schema_bytes_with_same_identity_are_not_collapsed(self):
        f=self.example();resources=[];raw=E.encoded({'$id':'urn:fixture:schema-conflict','type':'object'})
        f.engine.register_original_schema(raw,resources)
        with self.assertRaisesRegex(E.ResolutionFault,'conflicting original schema identity'):
            f.engine.register_original_schema(raw+b'\\n',resources)

"""
    assert s.count(needle)==1;p.write_text(s.replace(needle,extra+needle,1))
    assert all(methods(p)[n]==v for n,v in methods(OLD/'test_rules.py').items()) and len(methods(p))==47
    p=NEW/'checks.py';s=p.read_text().replace('_cal_checkpoint_resolution_rules_v1','_cal_checkpoint_resolution_rules_v2').replace('==45','==47').replace("'expected_cases':45","'expected_cases':47")
    p.write_text(s)
    p=NEW/'README.md';p.write_text(p.read_text().replace('Forty-five','Forty-seven')+'''\nThe original v1 run stopped in registry setup because the original storage schema\nand its exact native copy have the same identifier. Both are retained and guarded.\nVersion2 registers a byte-identical copy once and rejects any different original\nbytes under the same identifier. All45 original test methods are unchanged; two\nadditional cases verify exact-copy handling and refusal of a whitespace-different\nschema with the same identifier. The v1 failed report remains unchanged.\n''')
    freeze=(RUN/'freeze-checkpoint-resolution-rules-0001.py').read_text().replace('checkpoint-resolution-rules-v1','checkpoint-resolution-rules-v2')
    freeze=freeze.replace("own=[bind(p) for p in files]+[bind(Path(__file__).resolve())]", "own=[bind(p) for p in files]+[bind(Path(__file__).resolve()),bind(RUN/'author-checkpoint-resolution-rules-0002.py')]")
    freeze=freeze.replace("inputs.append(bind(ROOT/'authority/artifact-types/work/v1/fixtures/valid/record.json'))", "inputs.append(bind(ROOT/'authority/artifact-types/work/v1/fixtures/valid/record.json'))\n    inputs.extend(bind(ROOT/p) for p in ('product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v1/source-manifest.json','product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v1/receipts/checks-0001.json','product/lab/release-candidates/v1/interface/checkpoint-resolution-rules-v1/receipts/actual-0001.log'))")
    with (RUN/'freeze-checkpoint-resolution-rules-0002.py').open('x') as f:f.write(freeze)
    print('Authored unfrozen rules v2 with all45 original methods unchanged and two additional registry cases.',flush=True)
if __name__=='__main__':main()
