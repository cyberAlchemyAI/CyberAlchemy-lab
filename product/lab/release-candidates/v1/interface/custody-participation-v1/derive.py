"""Compose exact predecessor code with explicit original-content successors."""
import ast,hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];OLD=HERE.parent/'session-participation-v2'
changes=[]
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def edit(p,a,b):
    s=p.read_text();assert a in s,(p,a);n=s.count(a);p.write_text(s.replace(a,b));changes.append({'path':p.relative_to(ROOT).as_posix(),'before':a,'after':b,'occurrences':n})
shutil.copyfile(OLD/'records.py',HERE/'records.py')
edit(HERE/'records.py','from base import ROOT, encoded, require, sha','from .base import ROOT, encoded, require, sha')
edit(HERE/'records.py',"PREFIX = 'R03-fresh-reader'","PREFIX = 'R03-original-reader'")
edit(HERE/'records.py','session-participation-v2/reader.py#open_signed','custody-participation-v1/reader.py#open_signed')
source=HERE.parent/'inspection/lab_operator.py';raw=source.read_text();tree=ast.parse(raw)
pieces=[ast.get_source_segment(raw,n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['facets','differences','Inspection']]
(HERE/'inspection.py').write_text('"""Exact captured inspection with explicit original content support."""\nfrom collections import Counter\nfrom .base import ROOT,sha,parse,encoded,original,require,original_bridge\nMAX_ENTRIES=1000\nCLAIM="Exact owned candidate source; no canonical admission, live Agent, Session or public permission."\n\n'+'\n\n'.join(pieces)+'\n')
edit(HERE/'inspection.py',"binding = subject['source']; path = binding['path']","binding = subject['source']; path = binding['path']\n        if binding.get('encoding'):\n            report,_=original_bridge.source_record(self,subject)\n            return report")
adapter_source=HERE.parent/'operator-context-v6/source_adapter.py';shutil.copyfile(adapter_source,HERE/'adapter.py')
p=HERE/'adapter.py';s=p.read_text();start=s.index("API = HERE.parent / 'api-v12'");end=s.index('# Explicit domain-carrier policy.')
s=s[:start]+"from . import base as source,model,eligibility\nfrom .base import cut\n\n"+s[end:];p.write_text(s)
start=s.index('def verify_package(');end=s.index('\n\nclass SignedSources:')
s=s[:start]+"def verify_package(expected_sha256):\n    return source.verify_source(expected_sha256)\n"+s[end:];p.write_text(s)
edit(p,'self.selection_reader = selection_reader or source.source_selection','source.require(callable(selection_reader), "independent source selection reader required")\n        self.selection_reader = selection_reader')
edit(p,'self.closed = False','self.closed = False\n        self._trusted_records=None;self._trusted_sources=None;self._trusted_schemas=None')
edit(p,'for record in self.records: self.sources.get(record.artifact)',
    'for record in self.records: self.sources.get(record.artifact)\n        self._trusted_records=self.record_stamp(self.records)\n        self._trusted_sources=self.record_stamp(self.sources.records.values())\n        self._trusted_schemas=self.schema_stamp(self.schemas)')
edit(p,'    def guard(self):',"""    @staticmethod
    def record_stamp(rows):
        def witness(w):
            if w is None:return None
            return {'source_cut':w.source_cut,'artifact_ref':w.artifact_ref,'enclosing_sha256':w.enclosing_sha256,
                'actual_enclosing_sha256':source.sha(w.enclosing_original),'selector':w.selector,'encoding':w.encoding}
        return source.encoded([{'artifact':r.artifact,'raw_sha256':source.sha(r.original),'posture':r.posture,
            'source_ref':r.source_ref,'witness':witness(r.revision_witness)} for r in rows])
    @staticmethod
    def schema_stamp(rows):
        return source.encoded([{'carrier':s.carrier_ref,'kind':s.semantic_kind,'identity_field':s.identity_field,
            'raw_sha256':source.sha(s.original_schema),'expected_sha256':s.expected_sha256,'rule':s.version_binding_rule} for s in rows])
    def guard(self):""")
edit(p,"source.require(not self.closed, 'closed source adapter cannot serve context')", "source.require(not self.closed, 'closed source adapter cannot serve context')\n        if self._trusted_records is not None:\n            source.require(self.record_stamp(self.records)==self._trusted_records\n                and self.record_stamp(self.sources.records.values())==self._trusted_sources\n                and self.schema_stamp(self.schemas)==self._trusted_schemas,'captured source records or schemas changed')")
eligibility_source=HERE.parent/'session-authority-v2/eligibility.py';shutil.copyfile(eligibility_source,HERE/'eligibility.py')
p=HERE/'eligibility.py';edit(p,'import copy','import copy\nimport base64')
insert="""            elif witness.encoding=='base64-original-json/v1-candidate':
                match=re.fullmatch(r'/proposal/targets/(0|[1-9][0-9]*)/content/data',witness.selector)
                require(match is not None,'explicit original-content revision pointer required')
                tx=parse(witness.enclosing_original)
                families={'lab-runtime-original-json-proposal/v1-candidate':'lab-runtime-original-json-transaction/v1-candidate',
                    'lab-runtime-reviewed-original-json-proposal/v1-candidate':'lab-runtime-reviewed-original-json-transaction/v1-candidate',
                    'lab-runtime-original-json-proposal/v2-candidate':'lab-runtime-original-json-transaction/v2-candidate',
                    'lab-runtime-reviewed-original-json-proposal/v2-candidate':'lab-runtime-reviewed-original-json-transaction/v2-candidate'}
                proposal=tx.get('proposal',{})
                require(proposal.get('schema_version') in families and tx.get('schema_version')==families[proposal['schema_version']],
                    'explicit original-content transaction family required')
                index=int(match.group(1));targets=proposal.get('targets',[])
                require(index<len(targets),'original-content revision target absent');target=targets[index]
                require(target.get('version_ref')==wanted['version_ref'] and target.get('carrier_ref')==wanted['carrier_ref']
                    and proposal.get('scope_ref')==wanted['scope_ref'],'original-content revision target differs')
                entry=target.get('content');require(type(entry) is dict and set(entry)==set('schema_version content_ref media_type byte_sha256 size_bytes encoding data semantic_binding'.split()),
                    'closed original-content revision entry required')
                require(entry['schema_version']=='lab-artifact-content-entry/v1-candidate' and entry['encoding']=='base64'
                    and entry['media_type']=='application/json' and entry['semantic_binding'] is None,'original-content revision profile differs')
                try:raw=base64.b64decode(entry['data'],validate=True)
                except (ValueError,TypeError) as error:raise EligibilityFault('invalid original-content revision bytes') from error
                require(base64.b64encode(raw).decode()==entry['data'] and type(entry['size_bytes']) is int
                    and entry['size_bytes']==len(raw)<=1048576,'original-content revision encoding or size differs')
                require(raw==record.original and digest(raw)==entry['byte_sha256']==wanted['byte_sha256']
                    and entry['content_ref']=='runtime-content:sha256:'+wanted['byte_sha256'],'original-content revision bytes differ')
                structural=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
                require(structural(parse(raw))==structural(target.get('record')),'original-content parsed revision differs')
"""
edit(p,"            else:require(False,'unknown signed revision witness encoding')",insert+"            else:require(False,'unknown signed revision witness encoding')")
old_test=OLD/'run_checks.py';raw=old_test.read_text();tree=ast.parse(raw);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RealBranchChecks')
(HERE/'test_original_branch.py').write_text('"""All predecessor branch criteria with one declared raw-byte successor."""\nimport copy\nfrom datetime import datetime,timezone\nimport unittest\nfrom .base import *\nfrom . import records,reader\n\n'+ast.get_source_segment(raw,cls)+'\n')
edit(HERE/'test_original_branch.py',"self.assertEqual(encoded(subject['record']),original(row['original_binding']))", "actual=reader.adapter.model.record_bytes(self.adapter.view,subject)[0]\n            self.assertEqual(actual,original(row['original_binding']))\n            self.assertNotEqual(encoded(subject['record']),actual)\n            self.assertEqual(parse(actual),subject['record'])")
(HERE/'derivation.json').write_text(json.dumps({'authority_effect':'none','actual_owner_outcome':None,
    'parent_bindings':[bind(p) for p in [OLD/'records.py',source,adapter_source,eligibility_source,old_test]],
    'recorded_edits':changes,'source_adapter_import_delta':'Use closed package-relative source/model/eligibility modules, whole-source independent preflight and trusted record/schema seals.',
    'original_branch_assertion_delta':'The inherited serializer-equals-original assertion is incompatible with the required original-byte end state. Its exact source is retained; the new assertion requires original equality, different inherited bytes and identical parsed value. All other 21 methods remain exact.',
    'new_source_profile_cut_rule':'Bind SourceCut.source_profile_sha256 to the selected executable profile, independently of the old API static PINS constant.'},indent=2,sort_keys=True)+'\n')
print(json.dumps({'derived':str(HERE),'recorded_edits':len(changes),'authority_effect':'none'}))
"""Static derivation only. No store, key or Agent is created here."""
