"""Accept P11 only after a real chat reply is separately captured and validated."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.execution import support as s
from jsonschema import Draft202012Validator

def main():
    feedback_path=HERE/'human-feedback.json'
    s.require(feedback_path.is_file(),'actual packet-specific human reply has not been recorded')
    feedback=s.read(feedback_path)
    Draft202012Validator(s.read(HERE/'feedback-record.schema.json')).validate(feedback)
    pending=s.read(HERE/'pending-question.json')
    s.require(pending['status']=='asked-awaiting-actual-reply','question must have actually been issued')
    s.require(feedback['packet']==pending['packet']==s.binding(HERE/'review-packet.md'),'answer/issued/current packet mismatch')
    s.require(feedback['question']==pending['question'],'actual question mismatch')
    s.require(all(v=='fits' for v in feedback['assessment'].values()),'requested changes must be resolved before accepting P11')
    # A schema validates the record shape; the human origin is supplied by the
    # actual trusted chat reply captured outside this script, never synthesized.
    audit=s.read(HERE/'completion-audit.json')
    for entry in audit['accepted_predecessors']:
        receipt=s.read(s.check(entry['receipt']))
        for bound in receipt['artifacts']+receipt['inputs']:s.check(bound)
    review=s.read(HERE/'review-controls.json')
    for bound in review['checked_worked_bindings']+review['new_kernel_run_artifacts']:s.check(bound)
    s.require(audit['machine_complete'] and audit['author_complete'],'machine and author review must be complete')
    s.require(s.task('P11')['status']=='in-progress','P11 is not awaiting assessment')
    s.write(HERE/'completion-audit-before-feedback.json',audit)
    completed={**audit,'result':'machine-author-and-actual-human-complete','human_assessment':'fits',
        'human_feedback':s.binding(feedback_path),'p11_accepted':True,'accepted_count':12,
        'remaining_selected':['E'+str(n).zfill(2) for n in range(7)],'goal_complete':False}
    s.write(HERE/'completion-audit.json',completed)
    extra=[p for p in HERE.rglob('*') if p.is_file() and p.name!='task-acceptance.json']
    extra += [s.check(bound) for bound in review['new_kernel_run_artifacts']]
    try:
        s.accept('P11',[
            'The worked packet explains exact conformance/scope and seeded positive recursion, quantified model expansion versus complete derivability, potential/active/conflict origins, concrete public diagnostics, measured success/refusal envelope and remaining truth/host/parser/kernel limits. Sixteen actual worked controls include one newly completed full twenty-obligation wrong-scope qualification.',
            'Fifteen review checks bind eleven current accepted predecessors, exact worked input/output evidence and 114 retained new-run artifacts. Author review and machine completion were recorded before the human assessment; original v1 R06/G4 remain separately pending. All seven extensions remain selected and outstanding.',
            'The actual direct user reply is bound to the exact issued v3 packet and question, passes the closed feedback record contract, and assesses meanings, diagnostics and measured bounded local shadow use as fitting. Prior v2 feedback and synthetic schema fixtures do not stand in for this assessment.'
        ],review['controls']+s.read(HERE/'worked-examples.json')['controls'],extra=extra)
    except Exception:
        s.write(HERE/'completion-audit.json',audit)
        raise
    print('P11 accepted with actual exact-packet feedback. All seven selected extensions remain required.')

if __name__=='__main__':main()
