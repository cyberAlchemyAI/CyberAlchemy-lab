"""Independent checks of actual maintained schema, not just the transform output."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'))
from jsonschema import Draft202012Validator,FormatChecker
from referencing import Registry,Resource

def need(ok,reason):
    if not ok:raise ValueError(reason)
def main():
    api=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
    raw=(api/'authentication.schema.json').read_bytes();schema=json.loads(raw)
    registry=Registry()
    for file in sorted((api.parent/'source8-protocol-v2/schemas').glob('*.json')):
        document=json.loads(file.read_bytes());registry=registry.with_resource(document['$id'],Resource.from_contents(document))
    registry=registry.crawl();checker=FormatChecker()
    def valid(s,p):return Draft202012Validator(s,registry=registry,format_checker=checker).is_valid(p)
    path=ROOT/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/test_auth_schema_current_names.py'
    spec=importlib.util.spec_from_file_location('_independent_auth_policy_examples',path);examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(examples)
    cases=[]
    for version in ('lab-local-metadata-candidate-policy/v1-candidate','lab-local-workflow-transition-policy/v1-candidate','lab-local-ontology-projection-policy/v1-candidate'):
        selected=[r for r in schema['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')==version]
        need(len(selected)==1,'one exact maintained metadata policy contract required')
        row=selected[0]
        for source_name in ('completion-legacy:legacy-local-4636eca980a5d94d','completion-legacy:fresh-3600-fixture'):
            p=examples.metadata(source_name);p.update(schema_version=version,purpose=row['properties']['purpose']['const'],allowed_operations=copy.deepcopy(row['properties']['allowed_operations']['const']))
            if 'workflow' in version:
                b={'ref':'fixture:binding','sha256':'a'*64};p.update(workflow_control={k:copy.deepcopy(b) for k in ('routing_binding','kernel_binding','journal_binding')},
                  workflow_source_control={k:copy.deepcopy(b) for k in ('adapter_binding','source_binding','package_binding')})
            elif 'ontology' in version:
                p['ontology_control']={k:{'ref':'fixture:binding','sha256':'a'*64} for k in ('routing_binding','method_binding')}
            need(valid(schema,p) and sum(valid(r,p) for r in schema['oneOf'])==1,'full maintained policy does not match exactly one actual contract')
            bad=copy.deepcopy(p);bad['unselected_authority']=True;need(not valid(schema,bad),'extra authority field accepted')
            for bad_name in ('completion-legacy:../escaped','completion-legacy:','unselected-other-profile'):
                bad=copy.deepcopy(p);bad['source_name']=bad_name;need(not valid(schema,bad),'unknown/traversal selector accepted')
            cases.append({'policy':version,'source_name':source_name,'full_actual_Draft_contract_matches':1,'extra_authority_and_unknown_names_refused':True})
    # These branches share schema-version labels. Their lexical selectors must
    # remain disjoint before any host checks, including new current 3600 rows.
    for version in ('lab-local-candidate-policy/v4-candidate','lab-local-lesson-read-policy/v1-candidate',
      'lab-local-lesson-assessment-policy/v1-candidate','lab-local-lesson-application-policy/v2-candidate','lab-local-challenge-resolution-policy/v1-candidate'):
        rows=[r for r in schema['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')==version]
        count=sum(valid(r['properties']['source_name'],'completion-legacy:fresh-3600-fixture') for r in rows)
        need(count==1,'renewed current-family selector overlaps another contract')
    need((api/'authentication.schema.json').read_bytes()==raw,'actual schema changed during review')
    print(json.dumps({'result':'PASS-independent-actual-current-metadata-schema-composition','schema_sha256':hashlib.sha256(raw).hexdigest(),
      'full_metadata_policies_checked':cases,'dedicated_current_variant_selector_counts':1,
      'actual_private_Source_period_grant_authentication_claimed':False,'lexical_schema_is_not_permission':True,'authority_effect':'none'},sort_keys=True))
if __name__=='__main__':main()
