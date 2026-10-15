"""Construct a native candidate type revision and owned instance successors."""
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def prepare(projection,config,handle):
    """Use actual selected descriptor slots; preserve original v3 bodies in history.

    This function creates targets and schema bytes. The independently selected
    native engine must prepare/review/authorize/apply them in the owned branch.
    It supplies no repository admission or policy to revise foreign scopes.
    """
    old='cal.artifact-type.typed-relation/v3';new='cal.artifact-type.typed-relation/v4'
    source=projection['subjects'][old];contract=projection['contracts'][old]
    handle.common.require(source['effective_state'] in ('admitted-current','local-admitted-current')
        and contract['lifecycle_state'] in ('admitted-current','local-admitted-current'),'exact current type predecessor required')
    schema_raw=(HERE/'schema.json').read_bytes();schema=json.loads(schema_raw)
    schema_path='runtime/schemas/typed-relation-v4.json';digest=hashlib.sha256(schema_raw).hexdigest()
    descriptor={'artifact_type_ref':new,'semantic_kind':'typed-relation',
        'semantic_definition_refs':copy.deepcopy(contract['artifact']['semantic_definition_refs']),
        'schema_path':schema_path,'schema_selector':None,'schema_sha256':digest,
        'distinct_validation_purpose':'Exact independent connection identity and all550already declared current ordered endpoint pairs and closed qualifier contracts.'}
    selected={key:copy.deepcopy(contract[key]) for key in ('semantic_kind','instance_discriminator','identity_field','allowed_relation_kinds','relation_roles')}
    selected.update(schema_path=schema_path,schema_selector=None,schema_sha256=digest)
    selected['instance_discriminator']['value']='cyberalchemy-lab-typed-relation/v4'
    raw=(json.dumps(descriptor,indent=2,sort_keys=True)+'\n').encode()
    targets=[{'category':'artifact-type','operation':'revise','version_ref':new,
        'carrier_ref':'cal.artifact-type.artifact-type/v3','record':descriptor,'predecessor_ref':old,
        'decision_ref':'decision:owned-typed-relation-v4:representation-closure','contract':selected}]
    originals={new:raw};compatibility=[];foreign=[]
    for version,row in sorted(projection['subjects'].items()):
        if row['carrier_ref']!=old or row['effective_state'] not in ('admitted-current','local-admitted-current'):continue
        if row['record']['scope_ref']!=config['scope_ref']:
            foreign.append({'version_ref':version,'scope_ref':row['record']['scope_ref'],
                            'disposition':'preserved-foreign-source-no-effect-authority'})
            continue
        body=copy.deepcopy(row['record']);body['schema_version']='cyberalchemy-lab-typed-relation/v4'
        successor=row['identity']+'@typed-schema-v4.representation.1'
        raw=(json.dumps(body,indent=2,sort_keys=True)+'\n').encode()
        targets.append({'category':'typed-relation','operation':'revise','version_ref':successor,
            'carrier_ref':new,'record':body,'predecessor_ref':version,
            'decision_ref':'decision:owned-typed-relation-v4:'+row['identity'],'contract':None})
        originals[successor]=raw
        before=copy.deepcopy(row['record']);before['schema_version']=body['schema_version']
        handle.common.require(body==before,'representation successor changed connection semantics')
        compatibility.append({'predecessor_ref':version,'successor_ref':successor,'semantic_payload_unchanged':True})
    return targets,originals,{schema_path:schema},{schema_path:schema_raw},compatibility,foreign
