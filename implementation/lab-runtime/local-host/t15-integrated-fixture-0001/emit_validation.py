"""Produce bounded T22 validation evidence from the actual integrated receipts."""
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PINS=HERE/'INTEGRATED-FAMILY-PINS-0001.json'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,reason):
    if not ok:raise ValueError(reason)
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def main():
    need(sha(PINS.read_bytes())=='5006cfb83997d0954fbbb0d76a88eaaa7bd975dbb62d94cb96399856d7dd4e3c','independent family seal differs')
    selected=json.loads(PINS.read_bytes());cold=ROOT/selected['receipts']['cold']['path'];audit=ROOT/selected['receipts']['independent_actual_closure']['path']
    need(binding(cold)==selected['receipts']['cold'] and binding(audit)==selected['receipts']['independent_actual_closure'],'actual cold/audit receipt changed')
    c=json.loads(cold.read_bytes());a=json.loads(audit.read_bytes());e=c['observation']
    need(c['result']=='PASS' and e['result']=='PASS-native-cold' and e['independent_cold_replays']==2 and e['original_byte_parity'] is True
         and e['owned_cold_roots_removed'] is True and a['result']=='PASS' and a['counts']==selected['counts'],'actual integrated validation differs')
    need(e['source_binding']==selected['roles']['source']['source'] and e['package_binding']==selected['roles']['source']['package'],'actual cold Source/package differs')
    result={'schema_version':'lab-T22-integrated-family-validation/v1-candidate','result':'PASS','observed_at':datetime.now(timezone.utc).isoformat(),
      'actual_cases':3,'actual_case_basis':['first independent native signed Source cold replay with every original target byte checked','second independent native signed Source cold replay with every original target byte checked','separate signed Source and complete Mapper/Context closure audit'],
      'family':selected['family'],'source_name':selected['source_name'],'source_cut':selected['source_cut'],'family_pins_binding':binding(PINS),
      'actual_cold_observation_binding':binding(cold),'actual_independent_audit_binding':binding(audit),
      'source_binding':selected['roles']['source']['source'],'package_binding':selected['roles']['source']['package'],
      'actual_checks':{'independent_native_cold_replays':2,'original_target_byte_parity':True,'owned_cold_roots_removed':True,
        'signed_source_subjects':619,'signed_baseline_materials':859,'actual_source_records':26,'signed_target_counts':[2,26],
        'actual_original_targets':28,'current_Lessons':1,'native_Mapper_nodes':18,'native_Mapper_relations':12,
        'native_semantic_governance_cursor':30,'actual_Context_carriers':35,'exact_three_API30_lookup_State_inputs_in_signed_baseline':True,
        'retained_operator_and_historical_Session_baseline_rows_unchanged':True},
      'source_guarded_exit_completed':True,'new_family_live_Agent_or_Session_observed':False,'challenge_submitted':False,'challenge_resolved':False,
      'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None,
      'claim_ceiling':'Actual integrated Source cold replay and closure audit only. Native Context construction is retained evidence, not a live Agent Session. No challenge, real owner decision, repository admission, Session permission, empirical margin or integrated API regression is established.'}
    p=HERE/'T22-INTEGRATED-SOURCE-VALIDATION-0002.json';raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode();fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'result':'PASS','binding':binding(p)},sort_keys=True),flush=True)
if __name__=='__main__':main()
