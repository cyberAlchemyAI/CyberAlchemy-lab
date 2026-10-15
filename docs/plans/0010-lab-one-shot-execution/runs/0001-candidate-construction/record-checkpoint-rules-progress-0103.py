"""Record full selected export qualification and pure checkpoint-rule evidence."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v59'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def terminal(name,session,initial,final,code,report):
    v=load(report);p=RUN/name
    emit(p,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':session,'initial_chunk_id':initial,
        'final_chunk_id':final,'actual_exit_code':code,'result':v['result'],'actual_cases':v['actual_cases'],
        'failures':v['failures'],'errors':v['errors'],'report_binding':bind(report),
        'source_guarded_exit_completed':v['source_guarded_exit_completed'],
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    return p
def main():
    parent_path=API/'receipts/R03-0102.json';parent=load(parent_path)
    export_path=BASE/'api59-export-checks-v1/receipts/package-export-full-0001.json';export=load(export_path)
    assert export['result']=='PASS' and export['actual_cases']==14 and export['actual_public_calls']==18
    assert export['errors']==export['failures']==0 and export['source_guarded_exit_completed'] and export['owned_fixture_cleanup_completed']
    pure=BASE/'checkpoint-resolution-rules-v2';pure_path=pure/'receipts/checks-0001.json';proof=load(pure_path)
    assert proof['result']=='PASS' and proof['actual_cases']==47 and proof['errors']==proof['failures']==0 and proof['source_guarded_exit_completed']
    assert proof['actual_public_API_calls']==0 and proof['fixtures_only'] and proof['actual_owner_outcome'] is None
    failed_path=BASE/'checkpoint-resolution-rules-v1/receipts/checks-0001.json';failed=load(failed_path)
    assert failed['result']=='FAIL' and failed['actual_cases']==45 and failed['errors']==44 and failed['failures']==0
    metadata_path=RUN/'API50-metadata86-terminal-0002.json';metadata=load(metadata_path)
    assert metadata['actual_exit_code']==0 and metadata['actual_cases']==86 and metadata['failures']==metadata['errors']==0
    et=terminal('API59-package-export-full14-terminal-0001.json',23170,'d2ca9c','3136c1',0,export_path)
    pt=terminal('checkpoint-resolution-rules47-terminal-0002.json',93460,'d1bbed','44c17d',0,pure_path)
    ft=terminal('checkpoint-resolution-rules45-failed-terminal-0001.json',28856,'064d59','0c5540',1,failed_path)
    rows={r['path']:r for r in parent['files']}
    source=load(pure/'source-manifest.json')
    for row in source['files']+source['input_bindings']+proof['files']+export['files']+failed['files']:
        rows[row['path']]=row
    for p in (parent_path,pure_path,failed_path,export_path,et,pt,ft,pure/'source-manifest.json',metadata_path,
        ROOT/metadata['report_binding']['path'],ROOT/metadata['log_binding']['path'],Path(__file__).resolve()):
        row=bind(p);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    value={**parent,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'package_export_full14_qualified':True,'package_export_full14_actual_cases':14,'package_export_full14_actual_public_calls':18,
        'package_export_full14_checks_binding':bind(export_path),'package_export_full14_terminal_binding':bind(et),
        'package_export_runtime_qualified':True,
        'package_export_runtime_qualification_scope':'All14 selected actual authenticated API59 Work-root JSON candidate/current-source, permission/privacy/dependency, exact read-only retry and lock/generation recovery cases. General carriers, foreign authority and non-JSON adapters remain unfinished.',
        'checkpoint_resolution_rule_source_binding':bind(pure/'source-manifest.json'),
        'checkpoint_resolution_rule_checks_binding':bind(pure_path),'checkpoint_resolution_rule_terminal_binding':bind(pt),
        'checkpoint_resolution_rule_failed_terminal_binding':bind(ft),'checkpoint_resolution_rule_cases':47,
        'checkpoint_resolution_pure_rules_qualified':True,'checkpoint_resolution_public_handler_qualified':False,
        'checkpoint_resolution_actual_owner_recognition_qualified':False,
        'checkpoint_resolution_qualification_scope':'Pure byte/core/member/signature/period/recognition consistency on independently supplied synthetic facts. No actual authenticated owner/channel provenance or live Role/Scope authority. All three channel shapes exercised; original45 methods unchanged plus two registry checks.',
        'historical_API50_metadata86_terminal_binding':bind(metadata_path),'historical_API50_metadata86_qualified':True,
        'API50_completed_selected_cases':432,'API50_completed_selected_cases_passed':428,
        'API50_completed_selected_cases_failed':3,'API50_completed_selected_cases_errors':1,'API50_remaining_selected_cases':20,
        'change':'API59 full14 export suite completed PASS with18 actual calls, original source exit and owned cleanup. Separately implemented pure checkpoint resolution rules: complete exact original package/core/target/owner-voice coupling, actual selected-key Ed25519 verification, explicit three channel shapes, computed all-required authorization and retained construction gaps. Forty-seven synthetic rule cases PASS; actual public checkpoint.resolve remains unimplemented. Initial45-case run hit a duplicate original schema identity before44 fixtures could run. Version2 accepts only byte-identical copied schema originals; all45 original tests remain unchanged, and two extra registry cases refuse identity collapse. Failed evidence retained. Historical API50 metadata86 completed PASS. Twenty handlers/fourteen missing operations/all46 tasks remain unchanged.',
        'remaining_obligations':[
            'Integrate checkpoint rules with actual authenticated Principal/channel and live Role/Scope recognition, original provenance adapters, source guards, durable recording, exact retry/recovery and Validation Report generation. Synthetic facts do not qualify checkpoint.resolve or supply R08 owner outcomes.',
            'Finish the same original API50 remaining20 scheduler/session67314, Machine14 then termination6, without changing original clocks or failed evidence. Verify every required inherited current API59 journey separately.',
            'Implement all14 remaining public operations; finish general foreign/admitted-source import, carrier/reference/authority adapters and non-JSON privacy/encoding. Selected full14 Work-root export proof does not close general export requirements.',
            'Complete nonempty Lesson/Context/Ontology sources, actual Machine write authority, genuine R05 participant evidence, R06/R07 and all-member S02. Sole actual R08 precedes separately authorized A01-A04.'],
        'claim_ceiling':'Full14 selected API59 Work-root export cases/18 actual calls and47 synthetic pure checkpoint rule cases only. No complete inherited current API, actual owner recognition/outcome, live authority, canonical admission, genuine pilot, activation or completed plan.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    p=API/'receipts/R03-0103.json';emit(p,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(p),'bound_files':len(rows),'export_actual_cases':14,
        'export_actual_public_calls':18,'checkpoint_pure_cases':47,'authored_handlers':20,'missing_operations':14,
        'task_complete':False,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
