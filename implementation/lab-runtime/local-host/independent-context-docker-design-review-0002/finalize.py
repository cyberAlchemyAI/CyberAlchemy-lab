import pathlib,json,hashlib
R=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab');L=R/'implementation/lab-runtime/local-host';E=L/'independent-context-docker-design-review-0002'
def b(p):
 raw=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
results={m:json.loads((E/(m+'.log')).read_bytes()) for m in ['normal','optimized']}
report={'schema_version':'independent-context-docker-next-unit-design-review/v2','reviewer':'evidence_review','verdict':'PASS_DESIGN_ONLY','design':b(L/'CONTEXT-DOCKER-NEXT-UNIT-DESIGN-20261020-0002.md'),'previous_hold':b(L/'independent-context-docker-design-review-0001/review.json'),'effect':'NOT_RUN','findings':[],
 'resolved':[{'id':'CDN1-R01','status':'CLOSED_AT_DESIGN_LEVEL','basis':'The final manifest-only _ctx_emit branch is now explicitly synchronous and sole FINISH entry. Original build.py:76 emit cannot return to line77 summary until durable manifest EMIT ACK, exactly one FINISH, mediator full original-profile validation/readback/writer close and private-root absence, exact FINISH ACK, then checked one-time client close. Lost/invalid/late ACK and close faults remain UNKNOWN/no retry. Parent teardown failure after a visible child summary overrides that line with enclosing UNKNOWN.'}],
 'verified_design_requirements':[
 'Original final manifest emit immediately precedes sole original summary in the selected build body; the new synchronous branch therefore supplies a concrete reachable completion path without changing original semantic generation or manifest bytes.',
 'FINISH validates original schema lab-actual-context-delivery-package/v1-candidate, original claim, eight fields,39 sorted exact prior leaf bindings and40 total leaves. No inert writer schema/body substitution is authorized.',
 'Mediator writer readback/close must precede FINISH ACK; existing inert send-before-close behavior cannot be silently reused. Bridge separately checks inventory digest without inventing fields in frozen ACK schema.',
 'Loss of manifest ACK forbids FINISH; loss of FINISH ACK cannot be recovered from manifest presence; repeated FINISH, late write, wrong peer/ordinal/hash, client interruption and late teardown poison the attempt. Selected tests require original summary suppressed or explicitly nonfinal under enclosing UNKNOWN.',
 'Full role_stage/hardener/path_contract and layout are selected before render; ROOT/HERE,module namespace,sibling imports,API/FactScope redirects and refusal sites are verified. Five predecessor hash substitutions occur only afterward, with complete inverse pipeline.',
 'Fresh context/implementation-binding.json selects actual Reader code/entrypoint/environment; selected development authorization path and AUTH_SHA are explicitly projected/pinned before final Context source manifest. Historical authority is not promoted by hash reuse.',
 'Source source -> Source package -> Reader adapter source -> Mapper source -> Mapper package -> Context source -> Context package remains acyclic. Fresh observed Mapper output is mandatory before final Context source pin; Reader has no package.',
 'The11 role preimages are distinguished from full non-role/API/schema/FactScope/runtime closure. Each historical1804-row dependency must have selected current bytes/permitted same-family output or explicit reviewed projection; unresolved rows yield HOLD.',
 'Inherited55-leaf Mapper native parity,25 scoped source/native subjects,15nodes10relations,30 carrier schemas,40/39 Context outputs, nonce/scope/period/budget and900second cap remain obligations. No stale native JSON or fabricated missing field is accepted.'
 ],
 'verification':{'normal':results['normal'],'optimized':results['optimized'],'meaning':'79 read-only checks per mode: frozen source/hash/size continuity, explicit design clauses and original final emit/print AST shape. Text-clause presence checks support the manual design review; they do not execute or validate an implemented bridge.31 binding reads include retained repeated source references.', 'predecessor_preserved':True,'private_archive_bodies_read':False,'generated_roles_imported':False},
 'remaining_work':[
 'Implement and independently freeze the effect-disabled constructor with exact inverse and refusal tests; prepare only provisional role/dependency maps until independently reviewed fresh Mapper package exists.',
 'Implement the new original-profile bridge and writer with exact source/import/ACK contracts. Execute synthetic fault tests and prove FINISH reachability and cleanup ordering; this design PASS does not stand in for that evidence.',
 'Before any later effect, prove selected package/policy read-only mount visibility, UID/mode/readback, current scope/period/capacity and complete native ELF/ABI selection; freeze one-shot controller and semantic/output validators.',
 'A future local run still needs external exit and post-close/container/private-root absence, exact unchanged inputs and independent post-effect review. Any consumed attempt is not retried.'
 ],
 'claim_ceiling':'PASS for corrected design only. No generated Context delivery, actual native byte parity, policy/nonce effect, Reader/Mapper/Context/Docker execution, private archive access, protected Source8/G01/G02 qualification, active Session, human outcome or original36-task ledger completion.',
 'evidence':[b(E/n) for n in ['checks.py','normal.log','optimized.log','bindings-normal.json','bindings-optimized.json','finalize.py']]}
(E/'review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(b(E/'review.json'),sort_keys=True))
