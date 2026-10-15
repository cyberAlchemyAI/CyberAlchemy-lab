"""Materialize exact reader coverage gaps without changing source admission."""
from collections import Counter
import artifact_model as model
from protocol import *


def run(output):
    output=Path(output).resolve();source.require(output.is_relative_to(HERE/'receipts') and not output.exists(),'fresh scoped audit output required')
    schemas=Schemas()
    with source.replay_source('engineering') as view:
        failures=[];counts=Counter()
        for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
            c=model.carrier(view,subject)
            fit=schemas.protocol_valid('urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate',{'carrier_ref':c,'body':subject['record']})
            counts['body-fit' if fit else 'body-contract-gap']+=1
            if not fit:failures.append({'version_ref':subject['version_ref'],'category':subject['category'],'carrier_ref':c,
                'source_binding':subject['source'],'effective_admission':subject['effective_state'],
                'reason':'Exact generic domain envelope body does not fit the declared root schema; captured admission posture remains independent.',
                'owner_route':'R03/S02/R08'})
        rows,gaps=model.connections(view,schemas)
        heads={}
        for subject in view.subjects.values():
            if subject['effective_state'] in ('admitted-current','local-admitted-current'):
                heads.setdefault(subject['identity'],[]).append(subject['version_ref'])
        result={'schema_version':'lab-R03-reader-coverage/v1-candidate','result':'PASS','task_complete':False,
            'selected_source':view.selected,'subject_count':len(view.subjects),'body_counts':dict(counts),
            'body_contract_gaps':failures,'captured_typed_relations':sum(s['kind']=='typed-relation' for s in view.subjects.values()),
            'closed_api_connections':len(rows),'connection_gaps':gaps,
            'ambiguous_current_heads':[{'identity_ref':identity,'version_refs':sorted(versions),'owner_route':'R03/S02/R08'}
                for identity,versions in sorted(heads.items()) if len(versions)>1],
            'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,
            'claim_ceiling':'Exact saved signed engineering cut coverage audit only. Schema gap does not alter admission; API/ontology/workflow completion remains unproven.'}
        with output.open('xb') as stream:stream.write(source.encoded(result))
        print(__import__('json').dumps({'result':'PASS','subjects':len(view.subjects),'body_counts':dict(counts),
            'closed_connections':len(rows),'connection_gaps':len(gaps),'ambiguous_heads':len(result['ambiguous_current_heads']),
            'output':source.bind(output)},sort_keys=True))


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: audit.py fresh-receipts-output');run(sys.argv[1])
