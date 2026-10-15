"""Source-bound scalar reconciliation; never supplies parent semantic judgments."""
from pathlib import Path
import json, hashlib
import generation_runtime_v2 as g
import generation_review_validation_v2 as validation

R=Path(__file__).resolve().parents[1]
FAMILY={('archive_pairs','relation'),('candidate_pairs','relation'),('raw_rows','novelty'),('raw_rows','family_confirmed')}
def read(p):return json.loads(p.read_text())
def ident(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def opaque(value):return 'S-'+hashlib.sha256(value.encode()).hexdigest()[:20]
def ready():
    g.frozen()
    expected={'tools/generation_disputes_v2.py','generation-adjudication-contract.v2.json','reports/generation-disputes-v2-code-check.json','reports/generation-lock-independent-verification.json'}
    manifest=read(R/'freeze-generation-adjudication-v2.json');files=manifest['files']
    assert isinstance(files,list) and len(files)==len(expected) and {x['path'] for x in files}==expected,'exact adjudication source freeze'
    assert all(g.sha(R/x['path'])==x['sha256'] for x in files),'adjudication source drift'
    assert read(R/'reports/generation-lock-independent-verification.json')['classification']=='pass','independent lock verification required'
def indexed(packet,review,table):
    cols=packet['contract']['columns'][table]
    identity_fields=next(iter(packet['expected_matrix'][table]),{}).get('identity',{})
    return {ident({k:dict(zip(cols,row))[k] for k in identity_fields}):dict(zip(cols,row)) for row in review[table]}
def compare(packet,a,b):
    rows=[];disputes=[];families=[]
    for table,expected in packet['expected_matrix'].items():
        left,right=indexed(packet,a,table),indexed(packet,b,table)
        for ob in expected:
            key=ident(ob['identity']);x,y=left[key],right[key]
            scalars=[f for f in packet['contract']['columns'][table] if f not in ob['identity'] and f not in ob['fixed_values'] and f!='evidence']
            row={'table':table,'row_id':ob['row_id'],'identity':ob['identity'],'values':x,'field_status':{}}
            for field in scalars:
                if x[field]==y[field]:row['field_status'][field]='agreed';continue
                item={'dispute_id':opaque(packet['packet_id']+'|'+table+'|'+ob['row_id']+'|'+field),'table':table,'row_id':ob['row_id'],'identity':ob['identity'],'field':field,'reviewer_values':[x[field],y[field]],'evidence':[x['evidence'],y['evidence']]}
                if (table,field) in FAMILY:
                    families.append(item);row['field_status'][field]='family_unresolved'
                else:disputes.append(item);row['field_status'][field]='scalar_unresolved'
                row['values'][field]=None
            rows.append(row)
    return {'case_packet_id':packet['packet_id'],'rows':rows,'disputes':disputes,'family_disagreements':families,'rule':'Agreed fields exact; family disputes stay unresolved; only scalar differences eligible for at most one native adjudication.'}
def prepare(study,case):
    ready()
    jobs=[j for j in read(R/'generation-review-schedule.v2.json')['jobs'] if j['study_id']==study and j['case_id']==case]
    assert len(jobs)==2
    refs=[j['output_ref'] for j in jobs];packetref=jobs[0]['input_refs'][0];packet=read(R/packetref)
    terminals={e['job_id']:e for e in g.events() if e['event_kind']=='native_terminal_join'}
    assert all(j['job_id'] in terminals for j in jobs),'native review terminal witness required'
    complete=all(terminals[j['job_id']]['validation']['valid'] for j in jobs)
    bindings=[{'path':packetref,'sha256':g.sha(R/packetref)}]
    for j in jobs:
        prepared=next(e for e in reversed(g.events()) if e['event_kind']=='job_prepared' and e.get('job_id')==j['job_id'])
        assert all(g.sha(R/x['path'])==x['sha256'] for x in prepared['input_bindings']),'review packet/source drift'
        p=R/j['output_ref']
        if p.exists():
            assert terminals[j['job_id']]['validation'].get('output_sha256')==g.sha(p),'review source drift'
            bindings.append({'path':j['output_ref'],'sha256':g.sha(p)})
        if complete:assert validation.validate_paths(R/packetref,p)['valid']
    report=compare(packet,*[read(R/ref) for ref in refs]) if complete else {'case_packet_id':packet['packet_id'],'rows':[],'disputes':[],'family_disagreements':[],'status':'gated_incomplete_independent_review','null_semantic_assessments':True}
    report.update(study_id=study,case_id=case,source_bindings=bindings,independent_review_complete=complete)
    p=R/'reports/generation-disputes'/f'{study}-{case}.json';p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n')
    return str(p.relative_to(R))
def allowed_value(field,value):
    if field in validation.BOOLS:return type(value) is bool
    if field in ['usefulness','observability']:return type(value) is int and value in [0,1,2]
    if field in validation.ENUMS:return value in validation.ENUMS[field]
    return False

def adjudication_valid(report,body):
    errors=[]
    if not isinstance(body,dict):return {'valid':False,'errors':['body must be object']}
    if body.get('case_packet_id')!=report['case_packet_id']:errors.append('packet ID')
    resolutions=body.get('resolutions');expected={x['dispute_id']:x for x in report['disputes']}
    if not isinstance(resolutions,list):return {'valid':False,'errors':['resolutions list']}
    seen=[]
    for row in resolutions:
        if not isinstance(row,dict):errors.append('typed resolution');continue
        k=row.get('dispute_id');seen.append(k)
        if not isinstance(k,str) or k not in expected:errors.append('undeclared dispute');continue
        if row.get('status') not in ['resolved','unresolved']:errors.append('status')
        if row.get('status')=='resolved' and not allowed_value(expected[k]['field'],row.get('value')):errors.append('typed scalar')
        if row.get('status')=='unresolved' and row.get('value') is not None:errors.append('unresolved requires null')
        if not isinstance(row.get('evidence'),str) or not row['evidence'].strip():errors.append('evidence')
    if len(seen)!=len(set(str(x) for x in seen)) or set(str(x) for x in seen)!=set(expected):errors.append('exact unique dispute coverage')
    return {'valid':not errors,'errors':errors}

def lock(study,case,adjudication_ref=None):
    ready();p=R/'reports/generation-disputes'/f'{study}-{case}.json';report=read(p)
    assert all(g.sha(R/x['path'])==x['sha256'] for x in report['source_bindings']),'locked input drift'
    resolutions={};adju={'status':'not_needed' if not report['disputes'] else 'not_available'}
    if adjudication_ref:
        witnesses=[e for e in g.events() if e['event_kind']=='native_terminal_join' and e.get('output_ref')==adjudication_ref]
        assert len(witnesses)==1 and witnesses[0].get('terminal_observed') is True,'actual native adjudication terminal required'
        path=R/adjudication_ref
        try:body=read(path);result=adjudication_valid(report,body)
        except (OSError,ValueError,UnicodeError) as error:result={'valid':False,'errors':['missing/malformed adjudication: '+str(error)]}
        adju={**result,'output_ref':adjudication_ref}
        if path.exists():
            adju['sha256']=g.sha(path)
            assert witnesses[0]['validation'].get('output_sha256')==adju['sha256'],'native adjudication source drift'
        if result['valid'] and witnesses[0]['validation']['valid']:resolutions={x['dispute_id']:x for x in body['resolutions']}
    for dispute in report['disputes']:
        decision=resolutions.get(dispute['dispute_id'])
        if decision and decision['status']=='resolved':
            row=next(x for x in report['rows'] if x['table']==dispute['table'] and x['row_id']==dispute['row_id'])
            row['values'][dispute['field']]=decision['value'];row['field_status'][dispute['field']]='adjudicated'
    report.update(adjudication=adju,unresolved_scalar_count=sum(s=='scalar_unresolved' for row in report['rows'] for s in row['field_status'].values()),family_unresolved_count=len(report['family_disagreements']),agreed_values_preserved=True,meaning_status='locked_source_bound_model_judgments' if report['independent_review_complete'] else 'gated_incomplete_review')
    out=R/'reports/generation-locked'/f'{study}-{case}.json';out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');return str(out.relative_to(R))
