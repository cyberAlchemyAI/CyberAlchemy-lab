"""C13 actual Work continuity; candidate transition and current state are distinct."""
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import importlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent; ROOT = PACKAGE.parents[3]
WORK = ROOT/'implementation/lab-work/candidates/v1'
sys.path.insert(0,str(WORK))
import verification as work_verification
from verification import restore_archive, decode_archive
from episode import diagnostic_native_fixture
from local_context import *
from lab_runtime.replay import ReplayPins, legacy_runtime, full_replay
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.profiles import select
from lab_runtime.sources import capture
from lab_runtime.transition import (LocalPolicy, BranchPins, prepare_transition, authorize_transition,
    apply_transition, replay_successor, committed_files)

RUN = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
ARCHIVE = WORK/'packages/0002/branch.snapshot'
WORK_RECEIPT = WORK/'receipts/C12/0001.json'
MAPPING = RUNTIME/'design/contract-impact.json'
MANIFEST = PACKAGE/'packages/0001/generator-manifest.json'
L1_DEFERRALS = [
    {'obligation':'Actual owner admission and admitted continuity','route':'R08/A01/A03'},
    {'obligation':'Current answering-owner authority and final exact new generator members','route':'S02/R08'},
    {'obligation':'General trusted actor/action adapter and semantic Work restrictions','route':'W02/R03'},
    {'obligation':'General successor append and broad workflow execution','route':'W02/W03/W04'},
    {'obligation':'Native domain Artifact mapping and broader typed-property profiles','route':'O02/O03'},
    {'obligation':'SQLite disposable query/read model','route':'R03'},
    {'obligation':'Measured performance limits and Product pilot/conformance','route':'R04/R05/R07'},
    {'obligation':'Permanent operator/store provisioning','route':'A02'},
    {'obligation':'Power-loss durability and external/release effects','route':'R02/R07/A04'}]


def verify_inputs():
    context=load(RUN/'context-C13-v2.json')
    for row in context['source_bindings']:
        require(byte_digest(regular(ROOT/row['path']))==row['sha256'],'C13 selected source drift')
    receipt=load(WORK_RECEIPT)
    require(receipt['result']=='PASS' and receipt['task_complete'] is True,'C12 real Work proof incomplete')
    for row in receipt['files']+receipt['source_bindings']:
        require(byte_digest(regular(ROOT/row['path']))==row['sha256'],'C12 real Work proof drift')
    archive_row=next(r for r in receipt['files'] if r['path']==ARCHIVE.relative_to(ROOT).as_posix())
    decode_archive(ARCHIVE,archive_row['sha256'])
    return archive_row['sha256']


def selected_source():
    row=next(r for r in load(RUNTIME/'profiles/selections.json')['selections'] if r['name']=='d75')
    selection=select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']})
    return row,selection,capture(selection)


def session_for(parent,snapshot,native,root_ref,**options):
    row=next(r for r in load(RUNTIME/'profiles/selections.json')['selections'] if r['name']=='d75')
    return ContextSession(parent,snapshot,native,generator_manifest=MANIFEST,
        generator_pins=GeneratorPins(byte_digest(regular(MANIFEST)),IMPLEMENTATION_VERSION),
        owner_ref='principal:repository-owner@candidate.1',context_ref='context:cyberalchemy-v2-to-lab-migration',
        scope_ref='project:cyberalchemy-v2-to-lab-migration',capability_ref='product-capability:cyberalchemy-lab:governed-knowledge-lifecycle',
        expected_profile_sha256=row['profile_sha256'],expected_snapshot_digest=snapshot['snapshot_digest'],
        subject_ref=root_ref,references={'assignment_ref':'agent-assignment:first-governed-agent-episode@candidate.1',
        'profile_ref':'agent-profile:governed-repository-candidate-authoring@candidate.1'},**options)


def audit_typed_relations(data):
    """Check actual deterministic connections, not inferred semantic certification."""
    rows=[];subjects=data['projection']['subjects'];kinds=data['projection']['relation_contracts']
    for tx in data['transactions'][1:]:
        for relation in tx['consequences']['typed_relations']:
            payload=relation['payload'];contract=kinds[payload['relation_kind_ref']]['payload']
            pair={'source_kind':payload['source']['kind'],'target_kind':payload['target']['kind']}
            require(pair in contract['allowed_endpoint_pairs'],'committed relation ordered pair undeclared')
            qualifier=contract['qualifier_contract']
            Draft202012Validator({'type':'object','additionalProperties':False,'properties':qualifier['properties'],
                'required':qualifier['required_axes']}).validate(payload['qualifiers'])
            endpoints=[]
            for endpoint in [payload['source'],payload['target']]:
                require(endpoint['version_ref'] in subjects,'committed relation endpoint unresolved')
                subject=subjects[endpoint['version_ref']]
                require(subject['identity']==endpoint['ref'] and subject['kind']==endpoint['kind'],'committed endpoint identity/kind differs')
                require(subject['effective_state'] in ['admitted-current','admitted-historical','local-admitted-current','local-admitted-historical'], 'committed endpoint not eligible')
                endpoints.append({'version_ref':endpoint['version_ref'],'effective_state':subject['effective_state']})
            rows.append({'relation_ref':relation['node_id'],'kind_ref':payload['relation_kind_ref'],
                'axis_id':contract['axis_id'],'ordered_pair':pair,'qualifiers':payload['qualifiers'],
                'endpoint_postures':endpoints,'result':'PASS'})
    require(len(rows)==6,'C12 deterministic relation inventory changed')
    return {'result':'PASS','connections':rows,'semantic_noncollapse_certification':False,
        'scope':'Actual six deterministic C12 connections under their exact existing declared axes, ordered pairs and qualifier contracts.'}


def recover_committed_parent(parent):
    before=committed_files(parent,parent.verify_full())
    name,engine,stage=legacy_runtime(ROOT,parent.pins)
    try:
        recovery=engine.Store(parent.path,ROOT).recover(parent.pins.expected_head)
    finally:
        stage.cleanup()
        for key in list(sys.modules):
            if key==name or key.startswith(name+'.'):sys.modules.pop(key,None)
    require(committed_files(parent,parent.verify_full())==before,'recovery changed committed parent bytes')
    return recovery


def reconstruct_actual_Work(parent,selection,root):
    """New candidate genesis; never copies a parent signature or grants admission."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    private=Ed25519PrivateKey.generate();key=root/'new-transition-only.pem'
    import os
    fd=os.open(key,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as handle:handle.write(private.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
    public=private.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
    policy=LocalPolicy('role:candidate-c13-transition',public,'c13-selected-work-successor',str(root/'successor'),
        'scope:C13:isolated-actual-Work-reconstruction',(datetime.now(timezone.utc)+timedelta(minutes=30)).isoformat())
    data=parent.verify_full();target=data['transactions'][1]['proposal']['targets'][0]
    selected=[{'version_ref':target['version_ref'],'new_carrier_ref':target['carrier_ref'],
        'disposition':'carry','reason':'Preserve exact completed bounded C12 audit as reconstructed candidate only; no signature or Decision carry.'}]
    mapping_sha=byte_digest(regular(MAPPING));prepared=prepare_transition(parent,selection,selected,MAPPING,mapping_sha,policy)
    require(prepared['plan']['applicable'],'actual selected Work cannot reconstruct')
    response=authorize_transition(prepared,policy,key)
    outcome=apply_transition(parent,selection,prepared,response,MAPPING,policy)
    pins=BranchPins(**outcome['pins']);verified=replay_successor(policy.destination,pins,policy)
    require(verified['records'][target['version_ref']]==target['record'],'reconstructed Work body differs')
    require(verified['subjects'][target['version_ref']]['decision_ref'] is None,'successor inherited local admission authority')
    require(response['signature']!=data['transactions'][1]['approval']['signature'],'old signature copied')
    return {'policy':policy,'pins':pins,'outcome':outcome,'prepared':prepared,'response':response,'verified':verified}
