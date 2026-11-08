"""Archive real retained T03 Vaults into the existing API-original contract.

This external read-only normalization dispatches no API operation. It requires
the actual caller's terminal PASS and exact successful wire/schema bindings.
"""
import argparse
import base64
import importlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

def need(value,reason):
    if not value:raise ValueError(reason)
def run(config_path,evidence):
    selected=sys.modules.get('cal_installed_runtime_selection_v1');need(selected is not None,'actual installed native launcher required');selected.require_runtime_ready();selected.guard();root=selected.root()
    helper=root/'implementation/lab-runtime/local-host/t31-retained-api-0001';api=root/selected.current().package['entrypoint']['api_directory'];sys.path[:0]=[str(helper),str(api.parent)]
    R=importlib.import_module('retained');L=importlib.import_module('learning_records');P=importlib.import_module(api.name+'.protocol');schemas=P.Schemas(selected.binding('api.profile')['sha256'])
    config=json.loads(R.read(Path(config_path).absolute()));need(set(config)=={'first_binding','later_binding','files','application','assessment'},'closed exact actual learning normalization selection required')
    original=lambda b:L.original(b)
    first_raw=original(config['first_binding']);later_raw=original(config['later_binding']);first=json.loads(first_raw);later=json.loads(later_raw)
    need(first['result']=='PASS-local-current-one-Lesson-selection-and-close'and later['result']=='PASS-local-current-Lesson-later-application-independent-assessment',
         'actual first/later caller terminal PASS required before normalization')
    need(later['api_source_binding']==selected.binding('api.source')and later['profile_binding']==selected.binding('api.profile')and later['family_source_binding']==selected.binding('family.source'),
         'actual current learning software/family selection differs')
    evidence=Path(evidence).absolute();need(not evidence.exists()and evidence.parent.is_dir()and not evidence.is_relative_to(root),'fresh external normalization evidence required');evidence.mkdir(mode=0o700)
    path=root/'implementation/lab-runtime/local-host/t17-current-common-caller-0001/retain.py';spec=importlib.util.spec_from_file_location('_t31_actual_learning_vault_archive',path);retain=importlib.util.module_from_spec(spec);spec.loader.exec_module(retain)
    source=selected.binding('api.source')['sha256'];profile=selected.binding('api.profile')['sha256'];unit='t31:actual-T03-learning-originals';cases=[];selections=[]
    for label,operation in [('application','lesson.apply'),('assessment','lesson.assess')]:
        selection=config[label];need(type(selection)is dict and set(selection)=={'request_binding','reply_binding','workspace_descriptor_binding'},'closed exact actual learning API/Vault selection required')
        request_raw=original(selection['request_binding']);reply_raw=original(selection['reply_binding']);request,reply=json.loads(request_raw),json.loads(reply_raw)
        need(schemas.valid('api-call',request)and schemas.valid('api-reply',reply)and request['operation']==reply['operation']==operation and reply['kind']=='result'
             and reply['request_binding']['sha256']==R.sha(request_raw)and reply['contract_profile_binding']==schemas.profile_binding
             and request['expected_source_cut']==later['source_cut'],'actual original learning request/reply/schema/profile/source differs')
        row=schemas.operations[operation];need(schemas.protocol_valid(row['request_schema']['resource_uri'],request['message'])and schemas.protocol_valid(row['result_schema']['resource_uri'],reply['message']),
                                         'actual learning request/result domain schema differs')
        key='application_reply_sha256'if label=='application'else'assessment_reply_sha256'
        need(R.sha(P.compact(reply['message']))==later['actual_later_work'][key],'actual learning full wire reply differs from terminal caller observation')
        descriptor=json.loads(original(selection['workspace_descriptor_binding']));owned=Path(descriptor['root']);st=owned.stat()
        need(owned.is_relative_to(Path('/tmp'))and [st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]==descriptor['identity']and descriptor['identity'][2:]==[os.getuid(),0o700],
             'actual retained caller workspace identity differs')
        case={'operation':operation,'case':'actual-T03-'+label,'result':'PASS','expected_kind':'result','original_request_base64':base64.b64encode(request_raw).decode(),
              'request_sha256':R.sha(request_raw),'actual_reply':reply,'normalization_dispatched_API':False,
              'actual_T03_later_terminal_binding':config['later_binding'],'actual_full_reply_binding':selection['reply_binding'],'actual_workspace_descriptor_binding':selection['workspace_descriptor_binding']}
        archived=retain.archive(evidence/(label+'-originals'),owned/'workspace',{'source_sha256':source,'profile_sha256':profile,'unit':unit,'case':case.copy(),'original_request':request})
        retained_root=Path(archived['path']);workspace=json.loads(R.read(retained_root/'vault/workspace.json'))
        for target in reply['message']['targets']:
            header=target['artifact'];content=target['content'];need(target['operation']=='admit'and content is not None,'actual learning target must be a prepared candidate')
            matches=[row for row in workspace['materials']if row['ref']==content['content_ref']and row['sha256']==header['byte_sha256']==content['byte_sha256']]
            need(len(matches)==1,'actual learning target material is not independently selected');body=R.read(retained_root/'vault'/R.relative(matches[0]['path']))
            need(R.sha(body)==header['byte_sha256']and len(body)==content['size_bytes']and content['media_type']=='application/json','actual archived learning target original differs')
        case['retained_originals']={'path':archived['path'],'observation_sha256':archived['observation_sha256']};cases.append(case)
    terminal={'result':'PASS','unit':unit,'source_sha256':source,'profile_sha256':profile,'cases':cases,'actual_first_terminal_binding':config['first_binding'],
              'actual_later_terminal_binding':config['later_binding'],'API_dispatched_by_normalizer':False,'authority_effect':'none'}
    need(original(config['first_binding'])==first_raw and original(config['later_binding'])==later_raw,
         'actual caller terminal original bytes changed during normalization')
    selected.guard();schemas.guard()
    raw=P.compact(terminal);retain.write(evidence/'RESULT.json',raw)
    for case in cases:
        b=case['retained_originals'];selection={'archive':b['path'],'observation_sha256':b['observation_sha256'],'terminal_result':str(evidence/'RESULT.json'),
           'terminal_sha256':R.sha(raw),'source_sha256':source,'profile_sha256':profile,'operation':case['operation']};R.consume(**selection);selections.append(selection)
    # Recheck caller receipts after the complete original archives are sealed.
    need(original(config['first_binding'])==first_raw and original(config['later_binding'])==later_raw,
         'actual caller terminal original bytes changed during normalization')
    selected.guard();schemas.guard();retain.write(evidence/'SELECTIONS.json',P.compact({'selections':selections,'learning_controls':{key:config[key]for key in('first_binding','later_binding','files')},'authority_effect':'none'}))
    return {'result':'PASS-actual-T03-original-Vault-normalization','selections':selections,'authority_effect':'none'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--evidence',required=True);args=parser.parse_args();print(json.dumps(run(args.config,args.evidence),sort_keys=True),flush=True)
