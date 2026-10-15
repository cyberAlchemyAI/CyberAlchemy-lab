#!/usr/bin/env python3
"""Fresh original-byte catalog/view reconstruction without source effects."""
from represented_subjects import *


def observe():
    observations = []
    with signed_catalog() as (catalog,operations):
        adapter = CandidateRepresentationAdapter(catalog,operations)
        for domain in ['engineering','research','failure','learning']:
            path = ROOT/f'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0001/scenarios/{domain}/case.json'
            case = parse(path.read_bytes())
            cut = {'cut_id':case['case_id'],'authority_effect':'none','actual_owner_outcome':None,
                'records':[{k:r[k] for k in ['path','sha256','kind','version_ref']} for r in case['records']]}
            view = adapter.candidate_cut(cut)
            relations = adapter.validate_candidate_relations(view)
            observations.append({'domain':domain,'cut_id':cut['cut_id'],'case_binding':bind(path),
                'represented_records':len(view['views']),'view_digest':object_sha(view),
                'checked_relations':relations,'mapping_views':[
                    {k:v[k] for k in ['carrier','represented_subject','mapping_binding','mapping_proposal',
                        'source_admission','signed_catalog_subject_binding','confirmed_global_edge_eligible',
                        'signed_transaction_mapping_implemented']}
                    for v in view['views'].values() if v['mapping_proposal'] is not None]})
    require([o['represented_records'] for o in observations]==[31,55,54,57], 'selected case coverage differs')
    require([len(o['checked_relations']) for o in observations]==[7,22,26,15], 'relation coverage differs')
    return {'schema_version':'lab-O02-representation-observation/v1-candidate','result':'PASS',
        'authority_effect':'none','actual_owner_outcome':None,'observations':observations,
        'original_domain_effects_reexecuted':0,'transactions_applied':0,'canonical_ontology_events_applied':0,
        'signed_transaction_mapping_implemented':False,'complete_ontology_adapter':False,
        'source_archive_binding':bind(ARCHIVE),'mapping_binding':bind(MAPPING)}


if __name__=='__main__':
    print(json.dumps(observe(),indent=2,sort_keys=True,allow_nan=False))
