import bootstrap
from bootstrap import R,S,E,checked
import copy,json,os,stat
from pathlib import Path
from lab_contracts.codec import canonical,sha
from lab_selectors.anchors import RootAnchor,AnchoredReader,identity
from lab_packaging.selection import Payload,row,prepare,installed_rows
from environment.requirements import ORIGINAL_SELECTION_SHA,PRIOR_PATH,ORIGINAL_BINDINGS

ORIGINAL=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
ORIGINAL_RAW=checked(ORIGINAL,ORIGINAL_SELECTION_SHA)
PRIOR_RAW=checked(R/PRIOR_PATH,ORIGINAL_BINDINGS[PRIOR_PATH])
INSTALLED=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
PUBLIC_POLICY=S/'packaging/public-export-policy.json'
PUBLIC_POLICY_SHA='df3bf40c3be6e50c697c318673948321722568df75b244957a0471c214fd87a1'

def tiny():
    files={'bin/tool':b'fixture public bytes\n','deps/module.py':b'value = 7\n'}
    return Payload(files,{'schema_version':'lab-owned-installer-fixture/v1','authority_effect':'none',
        'members':{k:row(v,0o755 if k.startswith('bin/') else 0o644) for k,v in files.items()}},lambda:None)

def public_selection():
    policy=json.loads(checked(PUBLIC_POLICY,PUBLIC_POLICY_SHA));reads=policy['reads']
    reader=AnchoredReader([RootAnchor('repository',str(R),identity(R.stat()))],[r['binding'] for r in reads])
    return reader,policy

def full_payload():
    reader,policy=public_selection();raw=checked(PUBLIC_POLICY,PUBLIC_POLICY_SHA)
    return prepare(reader,raw,PUBLIC_POLICY_SHA,ORIGINAL_RAW,PRIOR_RAW,repository=str(R))

def anchor(path):return RootAnchor('fixture-install-parent',str(path),identity(path.stat()))

def terminal(result,owned):
    clean=not any(p.exists() for p in owned)
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() and clean else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    return 0 if result.wasSuccessful() and clean else 1
