"""Before-effect inherited-class relocation successor; original frozen attempt retained."""
from base import *
SUCCESSOR=Path(__file__).resolve().parent
def guard_successor(pin):
 require(binding(SUCCESSOR/'selection.json')['sha256']==pin,'independent successor selection differs')
 selection=load(SUCCESSOR/'selection.json');require(selection['authority_effect']=='none' and selection['actual_owner_outcome'] is None,'candidate successor required')
 source_guard(selection['predecessor_manifest_binding']['sha256'])
 actual={binding(p)['path'] for p in SUCCESSOR.glob('*.py')}
 require(actual=={b['path'] for b in selection['files']},'successor control closure differs')
 for b in selection['files']+selection['failure_evidence_bindings']:bound(b)
 return selection
