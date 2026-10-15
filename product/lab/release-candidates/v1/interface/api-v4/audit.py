"""Exact representation and lifecycle-qualified connection coverage for both cuts."""
from collections import Counter
import artifact_model as model
from handlers import cut
from protocol import *


def run(output):
    output=Path(output).resolve();source.require(output.is_relative_to(HERE/'receipts') and not output.exists(),'fresh selected coverage output required')
    schemas=Schemas();results=[]
    for name in ['engineering','reference-corrected']:
        with source.replay_source(name) as view:
            counts=Counter();failures=[];original_domain_mismatches=[]
            for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
                domain={'carrier_ref':model.carrier(view,subject),'body':subject['record']}
                fit=schemas.protocol_valid('urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate',domain)
                if not fit:original_domain_mismatches.append(subject['version_ref'])
                if subject['category']=='artifact-type':
                    counts['catalog-representations']+=1
                    fit=schemas.valid('catalog-envelope',model.representations.envelope(view,subject,cut(view),[]))
                else:counts['domain-instances']+=1
                counts['representation-fit' if fit else 'representation-gap']+=1
                if not fit:failures.append(subject['version_ref'])
            connection=model.connection_coverage(view,schemas);rows,gaps=model.connections(view,schemas)
            results.append({'name':name,'selected_source':view.selected,'source_cut':cut(view),'subjects':len(view.subjects),
                'representations':dict(counts),'representation_gaps':failures,'original_domain_mismatches':original_domain_mismatches,
                'connection_coverage':connection,'closed_relation_refs':[r['version_ref'] for r in rows],'connection_gaps':gaps,
                'canonical_effects_applied':0,'authority_effect':'none','actual_owner_outcome':None})
    result={'schema_version':'lab-R03-corrected-reader-coverage/v1-candidate','result':'PASS','task_complete':False,'cuts':results,
        'authority_effect':'none','actual_owner_outcome':None,'claim_ceiling':'Exact separately selected current/historical candidate cuts. Preserved historical gaps and original domain mismatches are independently visible; no canonical admission.'}
    output.write_bytes(source.encoded(result));print(json.dumps({'result':'PASS','cuts':[{k:r[k] for k in ['name','subjects','representations','connection_coverage']} for r in results]},sort_keys=True))


if __name__=='__main__':
    source.require(len(sys.argv)==2,'usage: audit.py fresh-selected-coverage-json');run(sys.argv[1])
