"""Fresh layout compilation/replay plus hostile shared saved-evidence controls."""
from pathlib import Path
import copy
import json
import os
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'execution'))
import support as s
import evidence as e
import proof_layout as layout

controls=[]
def positive(name,fn):
    value=fn();controls.append({'name':name,'result':'pass','expected':'accepted'});return value
def negative(name,fn):
    try:fn()
    except Exception as ex:
        controls.append({'name':name,'result':'pass','expected':'rejected','reason':str(ex).splitlines()[0]});return
    raise AssertionError('unexpected acceptance '+name)

simple=s.read(s.V2/'s06/recursive-proposal.json');combined=s.read(s.V2/'s06/recursive-result.json')
rich=s.read(s.V2/'s13/exact-contract-scope-kind-proposal.json');staged=s.read(s.V2/'s13/exact-contract-scope-kind-result.json')
positive('accepted-combined-through-shared-checker',lambda:e.validate_legacy(simple,combined))
positive('accepted-staged-through-shared-checker',lambda:e.validate_legacy(rich,staged))
for n in [0,3]:
    bad=copy.deepcopy(staged);bad['evidence']['actual']=bad['evidence']['actual'][:n]
    negative('truncated-staged-'+str(n),lambda bad=bad:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['evidence']['actual'][1]=copy.deepcopy(bad['evidence']['actual'][0])
negative('duplicate-staged-module',lambda:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['evidence']['actual'].reverse()
negative('reordered-staged-module',lambda:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['evidence']['actual'][0]['source']=copy.deepcopy(bad['evidence']['actual'][1]['source'])
negative('source-transplant',lambda:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['closure']=bad['closure'][:-1]
negative('genuine-proof-with-altered-closure',lambda:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['obligations'].pop()
negative('shrunken-hard-catalog',lambda:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['supports']=bad['supports'][:-1]
negative('missing-support-leaf',lambda:e.validate_legacy(rich,bad))
bad=copy.deepcopy(staged);bad['evidence']['general']['audit']['transitive_axioms'].append('CustomTruth')
negative('custom-axiom-in-replay-record',lambda:e.validate_legacy(rich,bad))
negative('proposal-receipt-transplant',lambda:e.validate_legacy(simple,staged))
info=e.boundary(simple,combined);evaluation={'closure':combined['closure'],'steps':combined['certificates']}
original=e.check(combined['evidence']['actual'][0]['source']).read_text()
positive('structured-generator-preserves-original-bytes',lambda:s.require(layout.render(info['before_normal_form'],info['normal_form'],evaluation,'combined',combined['evidence']['actual'][0]['module'])[0][2]==original,'changed required declarations/proofs'))
build=HERE/'fresh-build';build.mkdir(exist_ok=True)
imports,dep=s.predecessor_imports();records={}
for mode in ['combined','staged']:
    generated=layout.render(info['before_normal_form'],info['normal_form'],evaluation,mode,'ActualRecursive_V3Layout_'+mode)
    if '--resume-layouts' in sys.argv:
        retained=s.read(HERE/'layout-resume-evidence.json')['modules'][mode]
        s.require(len(retained)==len(generated),'retained layout count changed')
        for n,(_,name,text) in enumerate(generated):
            s.require(retained[n]['module']==name and s.check(retained[n]['source']).read_text()==text,'retained source/value/order mismatch')
            s.check(retained[n]['olean'])
        records[mode]=retained
        print(mode+' previously compiled layout revalidated; no reexecution/time claim',flush=True)
    else:
        files=[]
        for role,name,text in generated:
            path=build/(name+'.lean');path.write_text(text);files.append((name,path))
        records[mode]=s.compile_modules(build,files,imports=[imports])
        print(mode+' actual layout compiled',flush=True)
submission=build/'Submitted.lean'
submission.write_text('import RuntimeCatalog\nimport RuntimeProofs\nnamespace V2Submission\ntheorem required : Successor.Runtime.Catalog.RequiredGeneralBundle := Successor.Runtime.Proofs.general_bundle\nend V2Submission\n')
general=s.compile_modules(build,[('Submitted',submission)],imports=[imports])
lean=s.lean_path()
replay=subprocess.run([str(lean),'--run',str(imports/'RuntimeVerifier.lean'),'RuntimeCatalog','Successor.Runtime.Catalog.RequiredGeneralBundle','definition-value','V2Submission.required'],cwd=build,env={**os.environ,'LEAN_PATH':os.pathsep.join(map(str,[build,imports])),'PATH':str(lean.parent)+os.pathsep+os.environ.get('PATH','')},capture_output=True,text=True,timeout=60)
s.require(replay.returncode==0,'fresh exact general replay failed '+replay.stdout+replay.stderr)
audit=json.loads(replay.stdout)
s.require(audit['accepted'] and audit['fresh_kernel_replay'],'replay not accepted')
controls += [{'name':'fresh-'+mode+'-actual-layout','result':'pass','method':'actual-new-Lean-compilation'} for mode in records]
controls.append({'name':'fresh-exact-trusted-type-definition-axiom-replay','result':'pass','method':'same-pinned-kernel-runtime-verifier'})
s.write(HERE/'manifest-controls.json',{'result':'pass','controls':controls,'scope':'Shared combined/staged saved inspection plus fresh generated witness compilation and exact general replay; no application.'})
s.write(HERE/'layout-equivalence-report.json',{'result':'pass','before_normal_form_identity':s.identity(info['before_normal_form']),'normal_form_identity':s.identity(info['normal_form']),'closure_identity':s.identity(evaluation['closure']),'certificate_identity':s.identity(evaluation['steps']),'combined_and_staged':'Same structured declaration/value/proof bodies, linked through exact required imports; both compiled.','modules':records,'general_modules':general,'general_audit':audit,'inherited_dependency_binding':dep,'resumed_retained_compilations':'--resume-layouts' in sys.argv,'fresh_general_replay_now':True,'scope':'One actual nonempty-baseline recursive proposal plus current legacy combined/rich-staged fixtures and hostile evidence cases; full profile regression follows P09.','authority_effect':'none'})
s.accept('P02',[
    'One exact checker validates current legacy combined/staged layouts and v3 manifest correlation; structured rendering preserves original exact witness bodies without source marker splitting.',
    'Actual truncation, duplicate/reorder, source/proposal/closure/support transplant, shrunken catalog and custom-axiom controls reject; no result becomes application-authorized.',
    'Fresh combined and staged concrete witnesses compile from the same typed values/proofs and the complete trusted general statement is rechecked with its definition/axiom closure by the pinned verifier.'
],controls,extra=[HERE/'legacy_boundary.py',HERE/'run_p02.py']+([HERE/'layout-resume-evidence.json'] if '--resume-layouts' in sys.argv else []))
print('P02 accepted: shared exact evidence/layout checking')
