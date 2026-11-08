"""Exact whole current-family relation closure supplements ten-ref tests.

The signed Source maps twelve record originals and retains twelve native stream
relations. This checks all24 and both partitions without silently dropping any.
"""
import copy
from datetime import datetime,timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys


def need(ok,why):
    if not ok:raise ValueError(why)


def exact_versions(rows,expected,prefix):
    selected=[r for r in rows if r['version_ref'].startswith(prefix)]
    versions=[r['version_ref'] for r in selected]
    need(len(versions)==len(set(versions))==len(expected) and set(versions)==set(expected),
         'complete current family relation closure differs')
    return selected


def main():
    P=sys.modules.get('cal_installed_runtime_selection_v1')
    need(P is not None,'selected installed bootstrap required');P.require_runtime_ready();P.guard()
    root=P.root();api=root/P.current().package['entrypoint']['api_directory'];sys.path.insert(0,str(api.parent))
    module=lambda n:importlib.import_module(api.name+'.'+n)
    G,Protocol,M,H=(module(n) for n in ('guard','protocol','artifact_model','handlers'))
    source=P.binding('api.source')['sha256'];profile=P.binding('api.profile')['sha256'];G.verify(source);schemas=Protocol.Schemas(profile)
    binding=P.binding('family.record_index');raw=(root/binding['path']).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==binding['sha256'],'independently selected signed index changed')
    records=[r for r in json.loads(raw) if r['kind']=='typed-relation'];expected={r['version_ref']:r for r in records}
    prefix='typed-relation:'+P.value('identity.store')+':'
    need(len(records)==len(expected)==12 and all(ref.startswith(prefix) for ref in expected),'declared current twelve-relation fixture differs')
    period_binding=P.binding('family.period');period_raw=(root/period_binding['path']).read_bytes()
    need(hashlib.sha256(period_raw).hexdigest()==period_binding['sha256'],'current source period bytes changed')
    period=json.loads(period_raw);at=datetime.now(timezone.utc)
    need(datetime.fromisoformat(period['not_before'])<=at<datetime.fromisoformat(period['expires_at']),'actual current relation source period expired')
    mapping_binding=P.binding('family.mapping');mapping_raw=(root/mapping_binding['path']).read_bytes()
    need(hashlib.sha256(mapping_raw).hexdigest()==mapping_binding['sha256'],'selected native mapping changed')
    mapping=json.loads(mapping_raw)
    mapped=[row['artifact']['version_ref'] for row in mapping['rows'] if row['artifact']['version_ref'].startswith(prefix)]
    need(len(mapped)==len(set(mapped))==12 and set(mapped)==set(expected),'declared Mapper relation closure differs')
    with Protocol.source.replay_source(Protocol.source.CURRENT_LEGACY_NAME) as view:
        with M.model_read_batch(view):
            declared=[r for r in mapping['projection_dispositions'] if r['version_ref'].startswith(prefix)]
            whole={r['version_ref']:r for r in declared}
            need(len(declared)==len(whole)==24,'signed whole-family projection inventory differs')
            need({ref for ref,row in whole.items() if row['disposition']=='mapped-exact-context-representation'}==set(expected),
                 'signed mapped-original relation partition differs')
            stream_refs={prefix+str(commit)+':'+str(n)+'@local.'+str(commit) for commit in (1,2) for n in range(6)}
            need(set(whole)-set(expected)==stream_refs and all(whole[ref]['disposition']=='retained-source-outside-declared-context-selection' for ref in stream_refs),
                 'signed retained stream relation partition differs')
            family_subjects={ref:subject for ref,subject in view.subjects.items() if ref.startswith(prefix)}
            need(set(family_subjects)==set(whole),'whole live family has an extra or missing relation subject')
            for ref,subject in family_subjects.items():
                need(subject['kind']=='typed-relation' and subject['effective_state']==whole[ref]['effective_state']=='local-admitted-current'
                     and subject['carrier_ref']==whole[ref]['carrier_ref'],'live relation disposition/carrier differs from signed Mapper')
            rows,gaps=M.connections(view,schemas);actual=exact_versions(rows,whole,prefix)
            need(not any(row['subject_ref'].startswith(prefix) for row in gaps),'whole current relation family contains a connection gap')
            original_observations=[]
            for row in actual:
                ref=row['version_ref'];subject=view.subjects[ref]
                original,locator,encoding,file_pin=M.record_bytes(view,subject)
                if ref in expected:
                    declared_original=expected[ref]['original_binding']
                    need(hashlib.sha256(original).hexdigest()==declared_original['sha256'] and original==(root/declared_original['path']).read_bytes(),
                         'actual mapped relation original differs from signed index')
                connection=row['connection']
                need(connection['relation_kind_ref'] in view.data['projection']['relation_contracts']
                     and connection['signature_sha256']!='0'*64,'actual relation contract/signature unavailable')
                for name in ('source','target'):
                    header=connection[name]['artifact']
                    need(header==M.artifact_ref(view,view.subjects[header['version_ref']]),'actual relation endpoint/header differs')
                original_observations.append({'version_ref':ref,'original_sha256':hashlib.sha256(original).hexdigest(),
                    'source_file_sha256':file_pin,'encoding':encoding,'locator':locator,
                    'signed_disposition':whole[ref]['disposition'],'index_original':ref in expected})
            # Isolated observation perturbations test the exact whole-family
            # predicate without changing Source, model callbacks or journal.
            extra=copy.deepcopy(actual[0]);extra['version_ref']=prefix+'unexpected@1'
            for changed in (actual+[extra],actual[:-1],actual+[copy.deepcopy(actual[0])]):
                try:exact_versions(changed,whole,prefix)
                except ValueError:pass
                else:raise ValueError('extra/missing/duplicate current-family relation accepted')
        cut=H.cut(view);need(cut==mapping['source_cut'],'actual live relation source cut differs from selected Mapper')
    need(datetime.now(timezone.utc)<datetime.fromisoformat(period['expires_at']),'source period expired during observation');G.verify(source);P.guard()
    return {'result':'PASS-exact-live-24-current-family-relations','api_source_sha256':source,'api_profile_sha256':profile,
        'record_index_binding':binding,'mapping_binding':mapping_binding,'actual_source_cut':cut,'relation_count':24,'indexed_mapped_original_count':12,'retained_stream_relation_count':12,
        'relation_versions':sorted(whole),'original_observations':sorted(original_observations,key=lambda row:row['version_ref']),'actual_original_bytes_and_endpoint_headers_checked':True,
        'unexpected_same_family_missing_and_duplicate_refused':True,'Source_or_callbacks_mutated':False,
        'observed_at_utc':at.isoformat(),'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'canonical_admissions':0,'authority_effect':'none'}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True),flush=True)
