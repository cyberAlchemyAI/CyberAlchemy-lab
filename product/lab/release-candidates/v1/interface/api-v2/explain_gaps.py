"""Original failure stages for captured connections; source records stay unchanged."""
from jsonschema import Draft202012Validator
import artifact_model as model
from protocol import *


def run(output):
    output=Path(output).resolve();source.require(output.is_relative_to(HERE/'receipts') and not output.exists(),'fresh scoped gap explanation required')
    schemas=Schemas();rows=[]
    dispatcher=source.parse((SCHEMAS/'schemas/typed-connection.schema.json').read_bytes())
    with source.replay_source('engineering') as view:
        _,gaps=model.connections(view,schemas)
        for gap in gaps:
            subject=view.subjects[gap['subject_ref']];record=subject['record'];p=record['payload']
            observed={'version_ref':subject['version_ref'],'source_binding':subject['source'],'stages':[],'owner_route':'W07/R03/O03/S02/R08'}
            try:
                view.handle.operations.validate_relation(record,view.data['projection'],allow_historical=True)
                observed['stages'].append({'stage':'signed-runtime-endpoint-validation','result':'PASS'})
            except Exception as error:
                observed['stages'].append({'stage':'signed-runtime-endpoint-validation','result':'FAIL','error_class':type(error).__name__,
                    'reason':str(error)[:500]})
            try:
                signature,binding=model.signature(view,p['relation_kind_ref'])
                value={'relation_kind_ref':p['relation_kind_ref'],'signature_sha256':binding['sha256'],
                    'axis_ref':signature['payload']['axis_id'],'qualifiers':p['qualifiers']}
                ends=[]
                for key in ['source','target']:
                    endpoint=p[key];resolved=view.subjects.get(endpoint['version_ref'])
                    source.require(resolved is not None,'exact endpoint revision not captured: '+endpoint['version_ref'])
                    ends.append({'side':key,'declared_identity':endpoint['ref'],'captured_identity':resolved['identity'],
                        'declared_kind':endpoint['kind'],'captured_kind':resolved['kind'],'identity_matches':endpoint['ref']==resolved['identity']})
                    value[key]={'artifact':model.artifact_ref(view,resolved),'semantic_kind':endpoint['kind']}
                observed['endpoint_views']=ends
                branch=next(s for s in dispatcher['oneOf'] if s['properties']['relation_kind_ref']['const']==p['relation_kind_ref'])
                errors=list(Draft202012Validator(branch,registry=schemas.registry,format_checker=schemas.checker).iter_errors(value))
                observed['stages'].append({'stage':'exact-api-pair-qualifier-signature','result':'FAIL' if errors else 'PASS',
                    'errors':[{'pointer':'/'+ '/'.join(str(x) for x in error.path),'reason':error.message[:500]} for error in errors[:8]]})
                kinds=[s for s in view.subjects.values() if s['category']=='relation-kind' and s['record']==signature and s['source']['sha256']==binding['sha256']]
                observed['stages'].append({'stage':'exact-signature-subject-revision','result':'PASS' if len(kinds)==1 else 'FAIL','matching_revisions':[s['version_ref'] for s in kinds]})
            except Exception as error:
                observed['stages'].append({'stage':'exact-captured-endpoint-signature-closure','result':'FAIL',
                    'error_class':type(error).__name__,'reason':str(error)[:500]})
            rows.append(observed)
        result={'schema_version':'lab-R03-original-connection-gaps/v1-candidate','result':'PASS','task_complete':False,
            'selected_source':view.selected,'connection_gaps':rows,'authority_effect':'none','actual_owner_outcome':None,
            'canonical_effects_applied':0,'claim_ceiling':'Failure-stage observations from exact saved candidate inputs only; no implicit relation/endpoint repair or source admission.'}
        with output.open('xb') as stream:stream.write(source.encoded(result))
        print(__import__('json').dumps({'result':'PASS','gaps':len(rows),'binding':source.bind(output)},sort_keys=True))


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: explain_gaps.py fresh-receipts-output');run(sys.argv[1])
