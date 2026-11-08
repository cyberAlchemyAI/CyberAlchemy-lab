"""Exact original candidate Work profiles; coordinating Source never retargets them."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
ORIGINAL=ROOT/'implementation/lab-workflows/candidates/v1/workflows'
RETAINED=ROOT/'implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001'
RESULT_SHA='c9f85acd1b9316489d26eb1bbbb3e43d617f2903b7e627b74b86983c2c9e1445'
SPECS={
 'engineering':{'folder':'0004','manifest':'input-manifest.json','sha256':'1dedb3b7ab4b0257857eae09dcdb221cef490b5410d7c5bc87010019f29618a4','code_sha256':'91eb2420596cd0ece48bfdec749342c0ebfaf0df0f6d06171e3e295e1255569f','run_sha256':'21d82f6ce3766dcb9324877ebba18e4965952130572d17b006f69bdc074823e0'},
 'research':{'folder':'0007','manifest':'selection.json','sha256':'9ea324cf32469efa00d32c522bdf9baeab710e4463b5bc0ba69aba9d2996f148','code_sha256':'20f1749ef038c5153f293615126151a87c21794dd39b52338bc0f59c3c7be8ad','run_sha256':'bd2f746854fac130e355425bbb34a9c1e9644c650daa4649445cc1a81ed1db5e'}}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def load(kind):
    need(kind in SPECS,'selected original Work profile required');spec=SPECS[kind]
    original_code=ORIGINAL/(kind+'.py');need(sha(original_code.read_bytes())==spec['code_sha256'],'original producer method bytes differ')
    sys.path.insert(0,str(ORIGINAL));module=importlib.import_module(kind)
    need(Path(module.__file__).resolve()==original_code,'original producer imported from another origin')
    inputs=ROOT/'implementation/lab-workflows/candidates/v1/examples'/kind/'packages'/spec['folder']
    raw=(inputs/spec['manifest']).read_bytes();need(sha(raw)==spec['sha256'],'independently selected original input manifest differs');manifest=json.loads(raw)
    if kind=='engineering':resolved,records=module.resolve_inputs(inputs,spec['sha256'])
    else:resolved,records,_=module.resolve(inputs,spec['sha256'])
    need(resolved==manifest,'original resolver changed selected Work meaning')
    headers={};originals={};kinds={}
    for row in manifest['records']:
        raw=(inputs/row['path']).read_bytes();need(sha(raw)==row['sha256'],'original selected record bytes differ')
        semantic=row['kind'];originals[row['version_ref']]=raw;kinds[row['version_ref']]=semantic
        if semantic=='method':continue  # Original bootstrap Method schema; no carrier fabricated.
        carrier=module.carrier(semantic)[0]['artifact_type_ref']
        h={'scope_ref':manifest['scope_ref'],'identity_ref':row['identity_ref'],'version_ref':row['version_ref'],'carrier_ref':carrier,'byte_sha256':row['sha256']}
        headers[row['version_ref']]=h;originals[row['version_ref']]=raw;kinds[row['version_ref']]=semantic
    run_raw=(RETAINED/kind/'workflow-run.json').read_bytes();need(sha(run_raw)==spec['run_sha256'],'actual retained original design-run differs')
    run=json.loads(run_raw);need(run['schema_version']=='lab-workflow-design-run/v1-candidate','retained original is not a native WorkflowRun')
    for role,key in [('intent','intent_ref'),('work','work_ref'),('coordination_context','coordination_ref')]:need(run[role]==headers[manifest[key]],'original retained Work/Intent/Context retargeted')
    goal=manifest['goal_ref'];work=records[manifest['work_ref']];coord=records[manifest['coordination_ref']]
    need(coord['project_ref']==manifest['scope_ref']==work['payload']['project_ref'] and coord['goal_ref']==goal
         and goal in work['payload']['goal_refs'],'original Work/Goal/Coordination Project meaning differs')
    result=(RETAINED/'RESULT.json').read_bytes();need(sha(result)==RESULT_SHA,'independent actual retained producer receipt differs')
    profile={'kind':kind,'module':module,'manifest':manifest,'inputs':inputs,'records':records,'headers':headers,'raws':originals,'semantic_kinds':kinds,
      'original_run':run,'original_run_raw':run_raw,'original_result_raw':result,'original_work':headers[manifest['work_ref']],
      'original_producer_source_cut':run['source_cut'],'scope_ref':manifest['scope_ref']}
    profile['seal']=stamp(profile);return profile

def stamp(profile):
    return sha(enc({k:profile[k] for k in ('kind','manifest','records','headers','semantic_kinds','original_run','original_work','original_producer_source_cut','scope_ref')}))

def guard(profile):
    spec=SPECS[profile['kind']]
    need(stamp(profile)==profile['seal'],'captured original Work profile changed')
    need(sha((ORIGINAL/(profile['kind']+'.py')).read_bytes())==spec['code_sha256'],'actual original producer code changed')
    need(sha((profile['inputs']/spec['manifest']).read_bytes())==spec['sha256'],'actual original selection changed')
    for row in profile['manifest']['records']:
        raw=(profile['inputs']/row['path']).read_bytes()
        need(sha(raw)==row['sha256'] and raw==profile['raws'][row['version_ref']], 'actual original record bytes or captured originals changed')
    need(sha((RETAINED/profile['kind']/'workflow-run.json').read_bytes())==spec['run_sha256']
         and sha((RETAINED/'RESULT.json').read_bytes())==RESULT_SHA,'actual retained original producer changed')
    need(sha(profile['original_run_raw'])==spec['run_sha256'] and json.loads(profile['original_run_raw'])==profile['original_run']
         and sha(profile['original_result_raw'])==RESULT_SHA,'captured original producer bytes changed')
    return True
