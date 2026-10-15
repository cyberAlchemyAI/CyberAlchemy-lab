#!/usr/bin/env python3
"""Review the exact L0 predecessors and retain their bounded claim ceiling."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'execution'))
import support as s
BASE=Path(__file__).resolve().parent


def main():
    s.context('G0',[(s.PLAN,'tasks[id=G0] and complete L0 predecessor requirements'),
        (s.FORMAL/'proofs/l0/formalization-review.json','independent semantics and theorem scope review'),
        (s.BASE/'input/schema-api-alignment.json','parser and projection boundary'),
        (s.BASE/'demonstrations/l0/demonstration-receipt.json','specific evaluated invariant and exact dependencies')],
        [{'classification':'non-blocking','choice':'accept the unchanged three-kind candidate slice under author self-review',
          'basis':'All predecessor requirements have current receipts; independent organizational admission is not claimed.'}])
    reviewed=[]
    for task_id in ['P01','P03','P04','P05','B00','P02','P06']:
        task=s.task(task_id);s.require(task['status']=='accepted','unaccepted L0 predecessor')
        b=task['validation']['acceptance_ref'];s.check_binding(b);r=s.read(s.ROOT/b['path'])
        for item in r['artifacts']+r['dependency_bindings']:s.check_binding(item)
        reviewed.append(b)
    proof=s.read(s.FORMAL/'proofs/l0/statement-and-axiom-audit.json')
    demonstration=s.read(s.BASE/'demonstrations/l0/demonstration-receipt.json')
    s.require(proof['result']=='pass' and demonstration['result']['accepted_result'],'missing valid proof or inhabited demonstration')
    s.write(BASE/'l0-review.json',{'result':'accepted','review_mode':'Codex author self-review',
        'authority_effect':'none','predecessors':reviewed,'supported_kinds':['relation.conforms-to','relation.declares-effect-on','relation.materializes-consequence'],
        'supported_ordered_pairs':28,'registry_semantics_complete':False,
        'specific_evaluation_kernel_checked':True,'general_soundness_current':True,
        'unresolved_normative_L0_semantics':[],
        'retained_assumptions':['source interpretation','JSON/host projection','hashing','compiler execution','external assessment sufficiency'],
        'claim_ceiling':'Current candidate three-kind typed graph semantics, sound reference checker and bound synthetic addition; no authority admission or real execution evidence.'})
    s.accept('G0',{'l0-review.json':BASE/'l0-review.json'},
        ['All seven L0 predecessors, their artifacts and dependency bindings were checked current; decoder/runtime/evidence assumptions remain recorded.',
         'The accepted slice is exactly the reviewed three kinds and 28 pairs, not all 41 registered relations.'],
        ['The gate explicitly requires the successful general proof audit and inhabited specific evaluation; no unresolved normative clause is hidden.'],
        reviewed and [s.ROOT/b['path'] for b in reviewed]+[Path(__file__)])
    print('PASS G0: candidate L0 gate accepted')


if __name__=='__main__':main()
