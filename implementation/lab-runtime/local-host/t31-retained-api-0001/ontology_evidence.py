"""Private runtime source evidence, explicitly replacing no SourceAdmission.

This producer observes exact retained projection/package originals. Its open
hypothesis and candidate metadata grant no source admission or active authority.
"""
import copy
import importlib
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
import retained as R
ROOT=Path(__file__).resolve().parents[4]
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def produce(*,records,observations,controls):
    R.need(type(controls)is dict and set(controls)=={'projection_observation_ref'},'closed actual projection observation selection required')
    selected=[o for o in observations if o['observation_binding']['ref']==controls['projection_observation_ref']]
    R.need(len(selected)==1,'one exact original projection producer required');observed=selected[0];projection=observed['projection_producer']
    R.need(projection is not None and projection['producer_kind']=='actual-ontology-projection','actual successful projection producer required')
    receipt=projection['receipt'];files=observed['files'];view=receipt['ontology_view'];view={key:view[key]for key in R.FIELDS}
    R.need(view['version_ref']in records and records[view['version_ref']][0]==view,'actual returned projection view original required')
    actual=sys.modules.get('cal_installed_runtime_selection_v1');R.need(actual is not None and actual.root()==ROOT,'actual selected-root runtime source-evidence producer required');actual.guard()
    api=ROOT/actual.current().package['entrypoint']['api_directory'];portable=importlib.import_module(api.name+'.runtime_selection');P=importlib.import_module(api.name+'.protocol')
    originals={}
    for role in ('family.source','family.source_package','family.period'):
        binding=portable.binding(role);raw=P.source.original(binding);R.need(R.sha(raw)==binding['sha256'],'actual independent signed family original differs');originals[role]=(binding,raw)
    head_raw=files['vault/ontology/HEAD.json'];head=json.loads(head_raw);generation=R.relative(head['generation'])
    R.need(len(generation.parts)==1 and generation.name.startswith('generation-') and R.sha(head_raw)==receipt['ontology_applied_cut']['commit_sha256']
           and head['store_ref']==view['scope_ref']==receipt['ontology_applied_cut']['store_ref'],'actual projection head/store correspondence differs')
    prefix='vault/ontology/'+str(generation)+'/';manifest_raw=files[prefix+'manifest.json'];manifest=json.loads(manifest_raw)
    R.need(R.sha(manifest_raw)==head['generation_sha256'] and manifest['lab_source_cut']==observed['original_source_cut']==receipt['lab_source_cut']
           and manifest['mapping_binding']==receipt['mapping_binding'],'actual projection generation/source/mapping correspondence differs')
    members={}
    for row in manifest['files']:
        R.need(type(row)is dict and set(row)=={'path','sha256'},'closed actual native projection generation member required');name=str(R.relative(row['path']))
        R.need(name not in members and prefix+name in files and R.sha(files[prefix+name])==row['sha256'],'actual native projection original member differs');members[name]=row['sha256']
    R.need({name[len(prefix):]for name in files if name.startswith(prefix)}==set(members)|{'manifest.json'},'exact actual native generation closure required')
    report={'schema_version':'lab-private-runtime-source-evidence-observation/v1','projection_observation_binding':observed['observation_binding'],
            'projection_receipt_original_binding':projection['receipt_original_binding'],'head_sha256':R.sha(head_raw),'manifest_sha256':R.sha(manifest_raw),
            'generation_original_hashes':members,'independently_selected_family_bindings':{role:row[0]for role,row in originals.items()},
            'source_cut':observed['original_source_cut'],'SourceAdmission_requirement_satisfied':False,'authority_effect':'none'}
    report_raw=enc(report);seed=R.sha(report_raw);period=json.loads(originals['family.period'][1])
    # The original projection request selects a Project through its authenticated
    # actor policy. Mapping native scope must never replace this Project axis.
    mapping=json.loads(files['native-inputs/mapping.json']);scopes={row['artifact']['scope_ref']for row in mapping['rows']}
    R.need(len(scopes)==1,'one exact mapped Project scope required');scope=next(iter(scopes));workspace=json.loads(files['vault/workspace.json'])
    owner=observed['original_request']['message']['actor']['principal_ref']
    R.need(type(scope)is str and scope.startswith('project:') and scope==portable.value('identity.scope')
           and workspace['scope_refs']==[scope] and workspace['principal_ref']==owner and mapping['source_cut']==observed['original_source_cut'],
           'exact original projection Project/Actor/mapping scope correspondence required')
    version='private-runtime-evidence.1'
    labels={'source':('source','v1'),'evidence':('evidence-set','v1'),'generated':('generated-output','v2'),'hypothesis':('hypothesis','v1'),'source_edge':('typed-relation','v3'),'evidence_edge':('typed-relation','v3')}
    ids={label:kind+':local-runtime-evidence:'+seed+':'+label for label,(kind,v)in labels.items()};refs={label:identity+'@'+version for label,identity in ids.items()};bodies={};schemas={}
    for label,(kind,v)in labels.items():
        folder=ROOT/'authority/artifact-types'/kind/v
        if not (folder/'schema.json').is_file():folder=ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors'/kind/v
        body=json.loads((folder/'fixtures/valid/record.json').read_bytes());body.update(node_id=ids[label],scope_ref=scope,owner_ref=owner,lifecycle_state='candidate',successor_refs=[],
            evidence_refs=[observed['observation_binding']['ref'],projection['receipt_original_binding']['ref']],
            claim_ceiling='Private candidate metadata over exact retained local signed package/projection originals only. No SourceAdmission, canonical admission, active authority, cold replay inference or original Work completion.')
        bodies[label]=body;schemas[label]=json.loads((folder/'schema.json').read_bytes())
    bodies['source']['payload'].update(source_kind='retained-signed-local-fixture-package',locator=originals['family.source_package'][0]['path'],content_digest='sha256:'+originals['family.source_package'][0]['sha256'],captured_at=period['not_before'],provenance_refs=[originals['family.source'][0]['path']])
    bodies['source']['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'target','counterpart_kind':'generated-output','counterpart_ref':refs['generated']}]
    bodies['generated']['payload'].update(generator_ref='protocol:private-runtime-source-evidence-observation',input_refs=[refs['source']],output_digest='sha256:'+R.sha(report_raw),reproducibility_receipt_ref='private-runtime-evidence-observation:'+seed)
    bodies['generated']['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'source','counterpart_kind':'source','counterpart_ref':refs['source']}]
    bodies['evidence']['payload'].update(source_refs=[refs['source']],item_refs=[observed['observation_binding']['ref'],projection['receipt_original_binding']['ref'],'private-runtime-evidence-observation:'+seed],coverage_statement='Exact signed package and actual retained applied projection HEAD/generation correspondence.',limitations=['Original domainspec SourceAdmission requirement is not represented or satisfied.','Fresh native cold replay and current permission are separately required.'])
    bodies['evidence']['relation_refs']=[{'relation_kind_ref':'relation.evidence-bears-on','direction':'source','counterpart_kind':'hypothesis','counterpart_ref':refs['hypothesis']}]
    bodies['hypothesis']['payload'].update(proposition='The exact selected signed package admits a reproducible bounded local native representation.',disposition='open',falsification_conditions=['Exact cold native replay differs from retained native bytes.','Selected Source, package, generation or mapping digest changes.'],observation_targets=[R.sha(head_raw),R.sha(manifest_raw)])
    bodies['hypothesis']['relation_refs']=[{'relation_kind_ref':'relation.evidence-bears-on','direction':'target','counterpart_kind':'evidence-set','counterpart_ref':refs['evidence']}]
    for label,relation,left,right,qualifiers in [('source_edge','relation.derives-from','generated','source',{'derivation_role':'Exact private runtime metadata observation of signed package/projection originals'}),('evidence_edge','relation.evidence-bears-on','evidence','hypothesis',{'polarity':'Retained byte correspondence only; fresh cold replay remains separately required'})]:
        bodies[label]['payload'].update(relation_kind_ref=relation,source={'kind':labels[left][0],'ref':ids[left],'version_ref':refs[left]},target={'kind':labels[right][0],'ref':ids[right],'version_ref':refs[right]},qualifiers=qualifiers,relation_evidence_refs=[observed['observation_binding']['ref']]);bodies[label]['relation_refs']=[]
    output=[];roles={}
    for label,body in bodies.items():
        Draft202012Validator(schemas[label]).validate(body);raw=enc(body);kind,v=labels[label];header={'scope_ref':scope,'identity_ref':ids[label],'version_ref':refs[label],'carrier_ref':'cal.artifact-type.'+kind+'/'+v,'byte_sha256':R.sha(raw)};output.append((header,raw));roles[label]=header
    actual.guard()
    return {'records':output,'consumed_input_refs':[view['version_ref']],'consumed_observation_refs':[observed['observation_binding']['ref']],
            'receipt':{'schema_version':'lab-private-runtime-source-evidence-production/v1','observation':report,'observation_original_sha256':R.sha(report_raw),'roles':roles,
                       'hypothesis_disposition':'open','SourceAdmission_requirement_satisfied':False,'authority_effect':'none'}}
