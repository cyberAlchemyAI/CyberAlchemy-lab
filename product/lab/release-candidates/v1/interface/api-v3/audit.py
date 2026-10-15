"""Separate original domain conformance, declared metadata and candidate corrections."""
from collections import Counter
import artifact_model as model
from handlers import cut
from protocol import *


def run(output):
    output=Path(output).resolve();source.require(output.is_relative_to(HERE/'receipts') and not output.exists(),'fresh scoped audit output required')
    schemas=Schemas()
    with source.replay_source('engineering') as view:
        counts=Counter();failures=[];original_failures=[]
        for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
            decoded={'carrier_ref':model.carrier(view,subject),'body':subject['record']}
            domain_fit=schemas.protocol_valid('urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate',decoded)
            if not domain_fit:original_failures.append(subject['version_ref'])
            if subject['category']=='artifact-type':
                envelope=model.representations.envelope(view,subject,cut(view),[])
                fit=schemas.valid('catalog-envelope',envelope);counts['catalog-representations']+=1
            else:fit=domain_fit;counts['domain-instances']+=1
            counts['representation-fit' if fit else 'representation-gap']+=1
            if not fit:failures.append({'version_ref':subject['version_ref'],'source_binding':subject['source']})
        rows,gaps=model.connections(view,schemas);heads={}
        for subject in view.subjects.values():
            if subject['effective_state'] in ('admitted-current','local-admitted-current'):
                heads.setdefault(model.artifact_ref(view,subject)['identity_ref'],[]).append(subject['version_ref'])
        corrections=source.parse((HERE/'connection-corrections/manifest.json').read_bytes())
        correction_members=[source.parse(source.original(b)) for b in corrections['members']]
        result={'schema_version':'lab-R03-reader-coverage/v2-candidate','result':'PASS','task_complete':False,
            'selected_source':view.selected,'subject_count':len(view.subjects),'representation_counts':dict(counts),
            'representation_gaps':failures,'unchanged_original_domain_body_mismatches':original_failures,
            'captured_typed_relations':sum(s['kind']=='typed-relation' for s in view.subjects.values()),
            'closed_api_connections':len(rows),'connection_gaps':gaps,
            'candidate_connection_corrections':len(correction_members),'corrections_requiring_historical_project_write_profile':
                [r['member_ref'] for r in correction_members if r['current_endpoint_validation']['result']=='FAIL'],
            'ambiguous_current_heads':[{'identity_ref':identity,'version_refs':sorted(versions)}
                for identity,versions in sorted(heads.items()) if len(versions)>1],
            'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,
            'claim_ceiling':'Exact source-specific read representation succeeds separately from original domain instance schema conformance. Ten original connection gaps remain; correction candidates have not been applied.'}
        with output.open('xb') as stream:stream.write(source.encoded(result))
        print(json.dumps({'result':'PASS','subjects':len(view.subjects),'representation_counts':dict(counts),
            'closed_connections':len(rows),'original_connection_gaps':len(gaps),'ambiguous_heads':len(result['ambiguous_current_heads']),
            'candidate_corrections':len(correction_members),'output':source.bind(output)},sort_keys=True))


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: audit.py fresh-receipts-output');run(sys.argv[1])
