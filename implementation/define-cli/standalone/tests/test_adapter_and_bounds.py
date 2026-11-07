import copy
import json
from pathlib import Path
import random
import tempfile
from unittest import mock

from define_core import call
from define_core.adapters.lab import snapshot
from define_core.contracts import check
from define_core.exact import Refusal, binding, decode, encode, sha, write_package
from support import Case, add_source, base, b64, materialization, no_sources, raw_members, refresh


class LabSnapshot(Case):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='define-lab-source-test-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.request,self.inputs=base()
        source=decode(self.inputs['investigation-boundary.json'])
        self.registry={'entries':[{'definition_id':source['definition_id'],'version':source['version'],'path':'investigation-boundary.json',
                        'sha256':sha(self.inputs['investigation-boundary.json']),'admission_decision_ref':'example:historical-only'}],
                       'current_lookup':{source['definition_id']:source['definition_id']+'@'+source['version']},'definition_artifact_type_ref':'example.definition/v1'}
        self.write()

    def write(self):
        for name,raw in {**self.inputs,'authority/definitions/registry.json':encode(self.registry)}.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)

    def test_lab_adapter_preserves_registry_but_never_promotes_standing(self):
        c,m,report=snapshot(encode(self.request),self.root,permit_retention=True)
        self.assertIn('authority/definitions/registry.json',m)
        self.assertEqual(report['reference_observations'][0]['registry_match'],'historical-match')
        d=self.ok(self.invoke('prepare',{'request_utf8':encode(self.request).decode(),'capture_utf8':encode(c).decode(),'inputs':b64(m)}))
        self.assertEqual(d['pack']['status'],'candidate');self.assertIsNone(report['actual_owner_outcome'])
        self.assertTrue(all(r['standing_observation']['status']=='local-reference' for r in c['input_rows']))

    def test_missing_registry_refuses_without_initializing_anything(self):
        (self.root/'authority/definitions/registry.json').unlink()
        before={str(p.relative_to(self.root)) for p in self.root.rglob('*')}
        with self.assertRaises(Refusal):snapshot(encode(self.request),self.root)
        self.assertEqual(before,{str(p.relative_to(self.root)) for p in self.root.rglob('*')})

    def test_old_or_digest_mismatched_registry_is_explicitly_unverified(self):
        for mutation in ('lookup','digest'):
            saved=copy.deepcopy(self.registry)
            if mutation=='lookup':self.registry['current_lookup']={}
            else:self.registry['entries'][0]['sha256']='f'*64
            self.write();c,m,report=snapshot(encode(self.request),self.root)
            self.assertEqual(report['reference_observations'][0]['registry_match'],'not-established')
            self.registry=saved

    def test_ambiguous_registry_is_refused(self):
        self.registry['entries'].append(copy.deepcopy(self.registry['entries'][0]));self.write()
        with self.assertRaises(Refusal) as e:snapshot(encode(self.request),self.root)
        self.assertEqual(e.exception.code,'ambiguous-registry-entry')

    def test_registry_carrier_cannot_claim_different_reference(self):
        self.registry['definition_artifact_type_ref']='example:other-carrier';self.write()
        with self.assertRaises(Refusal) as e:snapshot(encode(self.request),self.root)
        self.assertEqual(e.exception.code,'registry-reference-mismatch')


class ContractBounds(Case):
    def test_generated_gaps_do_not_exceed_output_contract(self):
        r,i=no_sources()
        # 240 source rows are accepted; each unresolved retention status adds a gap.
        for x in range(240):add_source(r,i,f'source-{x}.json',b'{}')
        c=self.captured(r,i,permit_retention=False)
        c['capture']['gaps']=[{'gap_id':f'open-{x}','reason':'Unresolved source requirement','affected_use':'prepare-owner-review','continuation':'Review source'} for x in range(256)]
        c['capture_utf8']=encode(c['capture']).decode()
        d=self.ok(self.prepared(r,i,c));self.assertGreater(len(d['pack']['gaps']),490)
        self.assertGreater(len(d['pack']['readiness']['prepare-owner-review']['obligations']),490)

    def test_capture_row_limit_is_explicit(self):
        r,i=no_sources()
        for x in range(241):add_source(r,i,f'source-{x}.json',b'{}')
        self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(i)}),'capture-budget')

    def test_oversize_source_budget_refuses(self):
        r,i=no_sources();add_source(r,i,'large.txt',b'x'*(12*1024*1024+1))
        self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(i)}),'capture-budget')

    def test_malformed_json_entrypoints_do_not_escape_envelope(self):
        randomizer=random.Random(1042)
        values=[None,True,False,0,[],{},'x',{'nested':[]},[{}]]
        for _ in range(120):
            field=randomizer.choice(['api_version','id','operation','params'])
            doc={'api_version':'define.api/v1','id':'fuzz','operation':'capabilities','params':{}}
            doc[field]=copy.deepcopy(randomizer.choice(values))
            result=call(doc);check(result,'api-result')
            self.assertIn(result['outcome'],('prepared','invalid-input','unsupported','blocked'))

    def test_no_diagnostics_leak_source_or_values(self):
        marker='SOURCE_VALUE_MUST_NOT_APPEAR_IN_DIAGNOSTICS'
        r,i=base();r['applications'][0]['bindings']['A']=marker;refresh(r)
        result=self.prepared(r,i);self.refused(result)
        self.assertNotIn(marker,json.dumps(result['diagnostics']))

    def test_corrupted_lineage_and_provider_binding_refuse_materialization(self):
        for mutation in ('lineage','provider'):
            r,i=materialization()
            if mutation=='lineage':
                record=decode(i['candidate-lineage.json']);record['fields'].pop();raw=encode(record)
                i['candidate-lineage.json']=raw;b=binding(raw,'candidate-lineage.json')
                r['source_bindings'][-1]=b;r['materialization_selection'][0]['field_lineage_binding']=b
            else:
                body=decode(i['candidate-definition.json']);body['source_direction']['generator_sha256']='f'*64;raw=encode(body)
                i['candidate-definition.json']=raw;b=binding(raw,'candidate-definition.json')
                r['source_bindings'][-2]=b;r['materialization_selection'][0]['definition_binding']=b
                lineage=decode(i['candidate-lineage.json'])
                for entry in lineage['fields']:entry['source_binding']=b
                raw=encode(lineage);i['candidate-lineage.json']=raw;lb=binding(raw,'candidate-lineage.json')
                r['source_bindings'][-1]=lb;r['materialization_selection'][0]['field_lineage_binding']=lb
            d=self.package(r,i);self.refused(self.invoke('materialize',{'package_members':d['package_members']}))

    def test_later_revision_requires_same_pack_identity(self):
        r,i=base();old=self.package(r,i);raw=raw_members(old['package_members'])['pack.json']
        add_source(r,i,'predecessor.json',raw);r['predecessor_package_binding']=binding(raw,'predecessor.json')
        r['request_id']='another-pack';r['request_revision']=2;refresh(r)
        self.refused(self.prepared(r,i),'invalid-successor-lineage')
