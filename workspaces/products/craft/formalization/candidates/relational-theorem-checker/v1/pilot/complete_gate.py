#!/usr/bin/env python3
"""Finish G4 after accepted R06 and the actual human bounded-use recommendation."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
BASE=next(p for p in Path(__file__).resolve().parents if (p/'workflow/cli/runtime.py').is_file())
sys.path.insert(0,str(BASE/'workflow/cli'))
import runtime as c
HERE=c.s.BASE/'pilot'
sys.path.insert(0,str(HERE))
import prepare_review as p
s=c.s


def main():
    s.require(s.task('R06')['status']=='accepted','R06 human review and acceptance still required')
    s.require(s.task('G4')['status']=='not-started','G4 already accepted; do not overwrite')
    human=s.read(HERE/'human-review.json')
    s.require(human.get('source')=='direct user response in this thread' and
        human.get('bounded_use_recommendation')=='recommended','actual human bounded-use recommendation missing')
    for binding in human['reviewed_artifacts']:c.v.safe_binding(binding,limit=64*1024*1024)
    output=s.ROOT/s.task('G4')['write_scope']
    s.context('G4',[(HERE/'shadow-pilot-report.json','complete observed pilot coverage and cost'),
        (HERE/'machine-validation-audit.json','current generated evidence and exact hard inventories'),
        (HERE/'supported-use-matrix.json','supported profiles and retained trust boundaries'),
        (HERE/'reviewer-feedback.md','actual human meaning and diagnostic assessment'),
        (HERE/'human-review.json','direct human bounded-use recommendation'),
        (s.BASE/'gates/l3/l3-review.json','predecessor logic guarantees and semantic limits')],
        ['Retain every predecessor guarantee; current criterion/output evidence is audited against the full plan.',
         'Use the same actual human review only for its expressly stated meanings, diagnostics and bounded recommendation.',
         'No deployment, authority publication or actual admission is authorized by this candidate gate.'])
    audit=p.audit_plan()
    s.require(audit['counts']=={'tasks':35,'working_units':40,'edges':56,'accepted':34},'full plan predecessor audit incomplete')
    layers={
        'L0':{'retained':['Independent three-kind meanings','Exact ordered pairs and references','General checker/addition soundness','Inhabited and coexistence models'],
              'gate':s.task('G0')['validation']['acceptance_ref']},
        'L1':{'retained':['Exact selected registry/source bindings','Explicit companion carrier','Full structural coverage separate from inherited meanings','Full before/after currentness'],
              'gate':s.task('G1')['validation']['acceptance_ref']},
        'L2':{'retained':['Computed change classes','Independently complete hard obligations','Selected data versus universal preservation','Every old model expands in supported profiles'],
              'gate':s.task('G2')['validation']['acceptance_ref']},
        'L3':{'retained':['Finite typed positive Horn discipline','Generic derivation soundness','Exact checked least closure and absence boundary','Complete protected tuple lineage','Actual exact countermodels','Fresh-head model conservativity'],
              'gate':s.task('G3')['validation']['acceptance_ref']},
        'L4':{'retained':['Exact isolated statement/proof dependency replay','Independent bundle truth and full hard set','Meaningful CLI/CI failure states','Application recapture and fresh checking','Measured candidate-only pilot','Actual human meaning/usefulness/use review'],
              'predecessors':[s.task(t)['validation']['acceptance_ref'] for t in ['R01','R02','R03','R04','R05','R06']]}}
    audit.update(schema='relational.final-layer-alignment-audit/v1-candidate',layers=layers,
        result='predecessor evidence and layer guarantees current; G4 final recommendation follows',
        human_review=s.binding(HERE/'human-review.json'),goal_complete=False)
    s.write(output/'alignment-and-layering-audit.json',audit)
    review={'schema':'relational.l4-review/v1-candidate','result':'reviewed-for-bounded-candidate-use',
        'review_mode':'Actual direct human recommendation plus Codex current evidence/implementation audit',
        'human_review':s.binding(HERE/'human-review.json'),'pilot':s.binding(HERE/'shadow-pilot-report.json'),
        'supported_use_matrix':s.binding(HERE/'supported-use-matrix.json'),
        'alignment_audit':s.binding(output/'alignment-and-layering-audit.json'),
        'remaining_limits':['263 inherited source-semantic obligations outside the named profiles',
            'Lossy unary conformance projection and frozen candidate epoch 0',
            'Parser/hash/runtime/OS/kernel and externally supplied truth assumptions',
            'Cooperative local shadow application rather than distributed authority transactions',
            'Measured small captured examples, not throughput or scale guarantees'],
        'authority_effect':'none','deployment_or_admission_approved':False}
    s.write(output/'l4-review.json',review)
    recommendation='# Bounded-use recommendation\n\n'
    recommendation+='The human reviewer recommends the documented bounded candidate use and accepts the selected meanings and diagnostic usefulness. This is separate from mathematical proof validity and from organizational authority.\n\n'
    recommendation+='Use the local checker as a review aid only for the exact supported-use matrix, with current full source/toolchain bindings, fresh proof/model replay and every independently required hard obligation. Keep selected-data compatibility, invariant preservation and model conservativity distinct. Unsupported or unresolved evidence blocks readiness.\n\n'
    recommendation+='Keep actual meaning, external assessment/root truth and use decisions with their owners. The captured unary conformance abstraction and epoch 0 do not generalize to arbitrary targets, scopes or live authority epochs. The 41-kind structural registry does not establish its 263 unresolved inherited meanings.\n\n'
    recommendation+='The pilot measurements describe this host and captured graphs only. Full replay is deliberately expensive; optimization or broader evolution profiles require separately verified changes. Shadow application has a cooperative local lock and explicit source/epoch checks, and makes no distributed transaction guarantee.\n\n'
    recommendation+='No deployment, authority publication or actual admission is approved or performed by this gate.\n'
    (output/'bounded-use-recommendation.md').write_text(recommendation)
    (output/'review.py').write_bytes(Path(__file__).read_bytes())
    artifacts={name:output/name for name in ['l4-review.json','alignment-and-layering-audit.json',
        'bounded-use-recommendation.md','context-pack.json','review.py']}
    s.accept('G4',artifacts,
        ['All 35 task contracts, 40 working units and 56 dependencies are accounted for. Every accepted predecessor has current explicit deliverables and criterion evidence; the layer map retains semantic, structural, evolution, inference and workflow guarantees, with unsupported meanings excluded.',
         'The current supported-use matrix, exact proof/trust boundaries, owner decisions and remaining limits are recorded. Actual direct human feedback supplies the bounded-use recommendation; no author self-review is relabeled as human approval.'],
        ['The audit consumes current implementation, proof/witness and executed pilot evidence, not only DAG/plan receipts. The distinction between machine checking, source interpretation and human review remains explicit.',
         'The recommendation is candidate-only and has authority_effect none. Deployment, authority publication and admission remain separate authorized execution scopes.'],
        [HERE/'human-review.json',HERE/'machine-validation-audit.json',HERE/'supported-use-matrix.json'],
        human_review=s.binding(HERE/'human-review.json'))
    print('G4 accepted with actual human bounded-use recommendation; final whole-goal audit still required')


if __name__=='__main__':main()
