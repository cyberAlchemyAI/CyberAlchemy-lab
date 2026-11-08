"""Generated operational wrapper; do not weaken the retained proof recipe."""
from ..p03.qualification import *
def qualify_checked(request,context):
    request=copy.deepcopy(request);build=None;stage='request-validation'
    try:
        context.assert_current();C.validate('request',request)
        require(context.resource_policy==request['resource_policy'],'request/context resource policy mismatch')
        context.verify_supervision()
        build=context.allocate(request);write(build/'request.json',request)
        stage='normalization-projection';info=context.boundary(request['proposal'])
        write(build/'typed-input.json',info)
        stage='dependency-preparation';context.prepare(build,info,request['build_mode'])
        stage='projection-instance'
        name='ProjectionWitness_'+C.identity(request)[:20];path=build/(name+'.lean');path.write_text(info['projection_source'])
        projection=context.stage_compiler(build,[(name,path)])
        stage='reference-evaluator';evaluation=context.evaluate(info['normal_form'])
        stem='ActualRecursive_'+C.identity(request['proposal'])[:20]
        combined_path=build/(stem+'.lean');combined_path.write_text(L.render(info['before_normal_form'],info['normal_form'],evaluation,'combined',stem)[0][2])
        generated=L.render(info['before_normal_form'],info['normal_form'],evaluation,request['layout'],stem)
        files=[]
        for role,name,text in generated:
            p=build/(name+'.lean');p.write_text(text);files.append((name,p))
        actual=[]
        for name,path in files:
            stage='actual-instance-'+name;actual+=context.stage_compiler(build,[(name,path)])
            write(build/(name+'.compile-record.json'),actual[-1])
        stage='general-submission';submission=build/'Submitted.lean';submission.write_text(GENERAL_SOURCE)
        general_modules=context.stage_compiler(build,[('Submitted',submission)])
        stage='fresh-general-replay'
        replay=context.run_tool([str(context.lean),'--run',str(build/'RuntimeVerifier.lean'),'RuntimeCatalog','Successor.Runtime.Catalog.RequiredGeneralBundle','definition-value','V2Submission.required'],cwd=build,env=context.environment(build),capture_output=True,text=True,timeout=context.resource_policy['stage_seconds'])
        require(replay.returncode==0,'Fresh trusted theorem replay rejected '+replay.stdout+replay.stderr)
        audit=C.decode(replay.stdout.encode());require(audit['accepted'] and audit['fresh_kernel_replay'],'incomplete fresh replay')
        general={'audit':audit,'modules':general_modules,'stderr':replay.stderr,'claim_ceiling':'Fresh replay by the same pinned Lean kernel; not an independent second kernel.','submission_source':binding(submission)}
        proof={'actual':actual,'general':general,'projection':projection,'dependencies':binding(build/'dependencies.json')}
        proof_binding=write(build/(stem+'_evidence.json'),proof)
        before=request['proposal']['before'];after=request['proposal']['after']
        obligations=[{'id':o['id'],'method':o['method'],'target':o['target'],'status':'discharged','proposal_identity':C.identity(request['proposal']),'baseline_identity':C.identity(before),'profile_identity':before['profile_identity'],'catalog_identity':before['catalog_identity'],'evidence':[proof_binding]} for o in C.required_inventory('rule-only')]
        payload={'schema':'relational.recursive-result/v2','status':'qualified-candidate','proposal_identity':C.identity(request['proposal']),'before_identity':C.identity(before),'after_identity':C.identity(after),'profile_identity':before['profile_identity'],'catalog_identity':before['catalog_identity'],'obligations':obligations,'closure':evaluation['closure'],'certificates':evaluation['steps'],'observations':info['observations'],'supports':info['supports'],'normal_form':info['normal_form'],'before_normal_form':info['before_normal_form'],'evidence':proof,'counters':evaluation['counters'],'bounds':info['bounds'],'closure_scope':CLOSURE_SCOPE,'model_class':MODEL_CLASS,'human_review':'pending','readiness':'candidate-shadow-only; fresh application replay required','authority_effect':'none'}
        if request['layout']=='staged':
            payload['witness_layout']='split-independent-stages-v2'
            proof['layout']={'combined_source':binding(combined_path),'parts':[{'module':name,'source':binding(build/(name+'.lean'))} for _,name,_ in generated],'generator':binding(BASE/'p02/proof_layout.py'),'policy':'Structured declaration sections; exact original required values and proof bodies.'}
        payload_ref=write(build/'payload.json',payload)
        manifest={'schema':'relational.proof-manifest/v3','identity':expected_identity(request),'change_class':'rule-only','witness':{'layout':request['layout'],'modules':[{'role':generated[n][0],'module':m['module'],'source':{'kind':'repo',**m['source']},'olean':{'kind':'repo',**m['olean']}} for n,m in enumerate(actual)]},'obligations':[o['id'] for o in C.required_inventory('rule-only')],'general':{'kind':'repo',**general['submission_source']},'projection':{'kind':'repo',**projection[0]['source']},'dependencies':{'kind':'repo',**proof['dependencies']},'bound_result':{'kind':'repo',**payload_ref},'generator':tagged(BASE/'p02/proof_layout.py'),'authority_effect':'none'}
        result={'schema':'relational.qualification-result/v3','status':'qualified-candidate','request_identity':C.identity(request),'run_id':build.name,'manifest':manifest,'claims':[{'kind':k,'model_class':MODEL_CLASS,'query_scope':CLOSURE_SCOPE,'change_class':'rule-only','source_profile':request['source_profile'],'truth_assumptions':TRUTH_ASSUMPTIONS,'evidence_mode':'fresh-invocation-at-creation'} for k in ['complete-closure','model-expansion']],'resource_report':context.report(request),'payload':{'kind':'repo',**payload_ref},'complete_closure':True,'application_authorized':False,'authority_effect':'none'}
        stage='exact-saved-evidence-inspection';context.inspect(request,result)
        context.assert_current();write(build/'prepared-result.json',{'schema':'relational.unissued-candidate/v3','state':'unissued','proposed_result':result})
        return result
    except (ResourceExhausted,subprocess.TimeoutExpired) as e:result=failure(request,build.name if build else 'refused-before-run','unknown-resource',e,stage)
    except UnsupportedPolicy as e:result=failure(request,build.name if build else 'refused-before-run','unsupported-policy',e,stage)
    except UnsupportedProfile as e:result=failure(request,build.name if build else 'refused-before-run','unsupported',e,stage)
    except KeyboardInterrupt:result=failure(request,build.name if build else 'refused-before-run','cancelled','User cancellation',stage)
    except Exception as e:result=failure(request,build.name if build else 'refused-before-run','invalid',e,stage)
    if build is not None:write(build/'failure.json',result)
    return result

