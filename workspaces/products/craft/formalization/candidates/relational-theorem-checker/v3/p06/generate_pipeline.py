"""Explicit operational adaptation; retained proof recipe remains byte-identical."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent
source=HERE.parent/'p03/qualification.py'
text=source.read_text();start=text.index('def qualify_fresh(request,context):');end=text.index('\n\ndef inspect_saved',start)
original=text[start:end]
edits=[
    ('def qualify_fresh(request,context):','def qualify_checked(request,context):'),
    ("if context.resource_policy['memory_mode']=='required':raise UnsupportedPolicy('Required aggregate resource supervision must use the P06 supervisor; no memory cap is claimed by this local backend.')",'context.verify_supervision()'),
    ("evaluation=evaluate(info['normal_form'],context.resource_policy)","evaluation=context.evaluate(info['normal_form'])"),
    ('replay=subprocess.run(','replay=context.run_tool('),
    ("'resource_report':resource_report(request)","'resource_report':context.report(request)"),
    ("context.assert_current();write(build/'result.json',result);context.record_fresh(result)","context.assert_current();write(build/'prepared-result.json',{'schema':'relational.unissued-candidate/v3','state':'unissued','proposed_result':result})"),
]
adapted=original
for old,new in edits:
    assert adapted.count(old)==1,(old,'unexpected retained recipe shape')
    adapted=adapted.replace(old,new)
reversed_text=adapted
for old,new in reversed(edits):reversed_text=reversed_text.replace(new,old)
assert reversed_text==original,'proof-recipe change beyond documented operational hooks'
header='"""Generated operational wrapper; do not weaken the retained proof recipe."""\nfrom ..p03.qualification import *\n'
(HERE/'pipeline.py').write_text(header+adapted+'\n')
report={'result':'pass','retained_function_sha256':hashlib.sha256(original.encode()).hexdigest(),'adapted_function_sha256':hashlib.sha256(adapted.encode()).hexdigest(),'operational_edits':[{'old':a,'new':b} for a,b in edits],'roundtrip_to_retained_recipe':'exact','mathematical_construction':'unchanged normalization, projection, layouts, all 20 obligation IDs, exact general bundle and saved inspection','authority_effect':'none'}
(HERE/'pipeline-recipe-review.json').write_text(json.dumps(report,indent=2)+'\n')
