"""Find scalar disagreements without substituting parent judgments."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
FIELDS=['relation','discriminator','uncertainty','lineage_consistent','fit_preserved','complete_protected_fields']
def read(p):return json.loads(p.read_text())
phase=sys.argv[1]
for sh in ([int(sys.argv[2])] if len(sys.argv)>2 else [1,2]):
 names=[f'R{phase[0].upper()}{sh}{n}' for n in [1,2]]
 if not all((R/'reviews'/f'{n}.json').exists() for n in names):print(json.dumps({'phase':phase,'shard':sh,'status':'reviews_incomplete'}));continue
 a,b=[read(R/'reviews'/f'{n}.json') for n in names];ua={u['unit_id']:u for u in a['units']};ub={u['unit_id']:u for u in b['units']};diff=[];fixed=[]
 for uid,x in ua.items():
  y=ub[uid];ra={r['raw_id']:r for r in x['rows']};rb={r['raw_id']:r for r in y['rows']}
  for rid,r in ra.items():
   for f in FIELDS:
    if r[f]!=rb[rid][f]:diff.append({'unit_id':uid,'raw_id':rid,'field':f,'reviewer_values':[r[f],rb[rid][f]],'reasons':[r['evidence'],rb[rid]['evidence']]})
    else:fixed.append({'unit_id':uid,'raw_id':rid,'field':f,'value':r[f]})
  xa=x.get('unsupported_additions',[]);ya=y.get('unsupported_additions',[])
  # Reasons need not match. Exact post/field/category sets differ only as a declared scalar presence dispute.
  keys=lambda z:sorted(set((v.get('post_id'),v.get('field'),v.get('category')) for v in z))
  if keys(xa)!=keys(ya):diff.append({'unit_id':uid,'raw_id':None,'field':'unsupported_additions','reviewer_values':[xa,ya]})
  else:fixed.append({'unit_id':uid,'raw_id':None,'field':'unsupported_additions','value':xa})
 out={'phase':phase,'shard':sh,'reviewer_refs':[f'reviews/{n}.json' for n in names],'disputes':diff,'agreed_scalars':fixed,'adjudication_rule':'At most one native scalar-only turn per shard. Preserve agreed values; unresolved assessments remain uncertain and gate zero-extension/retention claims. No forced causal-family merge.'}
 p=R/'reports'/f'{phase}-shard{sh}-disputes.json';assert not p.exists(),'preserve first dispute report';p.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'phase':phase,'shard':sh,'status':'disputed' if diff else 'agreed','disputed_scalars':len(diff),'agreed_scalars':len(fixed)}))
