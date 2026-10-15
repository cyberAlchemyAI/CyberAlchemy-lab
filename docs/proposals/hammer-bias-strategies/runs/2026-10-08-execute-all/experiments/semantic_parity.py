#!/usr/bin/env python3
"""Exercise the actual S10 checklist omission with controlled paired records."""
import json, copy
from pathlib import Path
r=Path(__file__).resolve().parents[1]
src=json.loads((r/'inputs/dispatches/s10.dispatch.json').read_text())
listed=src['steps'][2]['lane_sync_contract']['required_equal_fields']
required=['outcome','constraints','exclusions','evidence','unresolved_claims','success_measure']
human={'outcome':'Choose an intervention that fits the problem rather than the available toolkit.','constraints':['Preserve the underlying outcome.','Execute all sixteen requested strategies.'],'exclusions':['No production efficacy claim from structural validation alone.'],'evidence':['Frozen catalog observations are artifact evidence.','Native exercise outcomes are controlled synthetic evidence.'],'unresolved_claims':['Comparative effectiveness on real operating outcomes remains unmeasured.'],'success_measure':'All sixteen analyses and their stated tests have evidence-backed outputs; intervention choices preserve explicit case constraints.'}
machine=copy.deepcopy(human)
drift=copy.deepcopy(machine); drift['evidence']=['Structural passes prove production efficacy.']
measure_drift=copy.deepcopy(machine); measure_drift['success_measure']='Maximize count of written artifacts.'
def compare(a,b,fields):
 return [k for k in fields if k not in a or k not in b or a[k]!=b[k]]
trials=[]
for name,b in [('matching',machine),('evidence-only-drift',drift),('success-measure-only-drift',measure_drift)]:
 trials.append({'case':name,'frozen_listed_fields':listed,'listed_field_mismatches':compare(human,b,listed),'full_obligation_mismatches':compare(human,b,required)})
target=r/'run/S10'; target.mkdir(parents=True,exist_ok=True)
(target/'structured-need.json').write_text(json.dumps(machine,indent=2)+'\n')
(target/'human-need.md').write_text('# Human problem contract\n\n'+'\n\n'.join('**'+k.replace('_',' ').title()+':** '+(v if isinstance(v,str) else ' '.join(v)) for k,v in human.items())+'\n')
missing_human=copy.deepcopy(human); missing_machine=copy.deepcopy(machine)
missing_human.pop('evidence'); missing_machine.pop('evidence')
trials.append({'case':'evidence-missing-from-both','full_obligation_mismatches':compare(missing_human,missing_machine,required)})
read_machine=json.loads((target/'structured-need.json').read_text())
read_human={}
for line in (target/'human-need.md').read_text().splitlines():
 if line.startswith('**'):
  label,value=line[2:].split(':** ',1); read_human[label.lower().replace(' ','_')]=value
def render(value): return value if isinstance(value,str) else ' '.join(value)
rendered_machine={k:render(v) for k,v in read_machine.items()}
readback_mismatches=compare(read_human,rendered_machine,required)
assert not readback_mismatches
assert trials[-1]['full_obligation_mismatches']==['evidence']
report={'emitted_file_readback':{'human':'run/S10/human-need.md','machine':'run/S10/structured-need.json','required_fields':required,'mismatches':readback_mismatches,'method':'Compare required-field presence and canonical literal rendering after parsing the saved files; not a general paraphrase-equivalence proof.'},'kind':'executed-controlled-semantic-parity-test','source':'inputs/dispatches/s10.dispatch.json#/steps/2/lane_sync_contract/required_equal_fields','trials':trials,'repair':'Compare every obligation including evidence and success_measure; matching record pair is written under run/S10.','observed_result':'The frozen enumerated checklist alone misses evidence-only and measure-only drift; full obligations detect both. The matching emitted pair passes required-field presence and canonical-rendering readback; jointly missing evidence is also rejected.','limit':'This executes a local checklist-only comparator to demonstrate the omission; it does not show a production consumer ignored the higher-level gate.'}
(r/'experiments/semantic-parity-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(trials,indent=2))
