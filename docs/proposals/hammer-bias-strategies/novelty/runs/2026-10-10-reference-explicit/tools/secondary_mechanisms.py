import importlib.util,json,itertools
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('ten',R/'tools/ten_runtime.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
rt=m.Runtime(R);rt.integrity();report=json.loads((R/'reports/report.json').read_text())
result={'classification':'prospectively_declared_secondary_mechanism_diagnostic','criteria_sha256':m.sha(R/'SECONDARY-MECHANISM-CRITERIA.json'),'report_sha256':m.sha(R/'reports/report.json'),'hard_protocol_failure':report['hard_protocol_failure'],'cases':{},'claim_ceiling':'Local complementary probe specifications only; no global originality or observed benefit.'}
for cid in m.CASES:
 if report['hard_protocol_failure']:
  result['cases'][cid]=None;continue
 case=report['case_reports'][cid];qualified=set(case['qualified_cards'])
 reviews=[rt.join_body(cid+'-review'+str(i)) for i in (1,2)]
 pairs=[{tuple(sorted((p['left'],p['right']))):p['relation'] for p in v['candidate_pairs']} for v in reviews]
 proven={pair for pair in pairs[0] if pairs[0][pair]=='distinct' and pairs[1][pair]=='distinct'}
 packet,bindings=rt.review_packet(rt.job(cid+'-review1'))
 controls={k:[card for card in qualified if bindings[card]['condition']==k] for k in ('O','G')}
 assessable=all(controls.values());allcontrols=controls['O']+controls['G'];rows={}
 for condition in m.CONDITIONS:
  if condition in ('O','G'):continue
  own=[card for card in qualified if bindings[card]['condition']==condition]
  additions=[card for card in own if all(tuple(sorted((card,c))) in proven for c in allcontrols)] if assessable else None
  rows[condition]={'qualified_cards':own,'distinct_from_all_qualified_controls':additions,'conservative_complementary_families':m.max_clique(additions,proven) if assessable else None}
 result['cases'][cid]={'controls':controls,'assessable':assessable,'conditions':rows,'reason':'Both control repertoires represented' if assessable else 'At least one control has no qualified representative; no vacuous pairbased credit'}
m.exclusive(R/'reports/secondary-mechanisms.json',result)
print(json.dumps({'output':str(R/'reports/secondary-mechanisms.json'),'sha256':m.sha(R/'reports/secondary-mechanisms.json'),'hard_protocol_failure':result['hard_protocol_failure']}))
