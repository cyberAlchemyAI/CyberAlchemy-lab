"""Complete candidate evidence and declared connections; preserve frozen failures."""
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v62';API=BASE/'api-v63'
def replace(p,a,b):
    value=p.read_text();assert value.count(a)==1,(p,a);p.write_text(value.replace(a,b,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v13').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v12',BASE/'lesson-host-composition-v13',ignore=ignore)
    replace(BASE/'lesson-host-composition-v13/host.py','api-v62/service.py','api-v63/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v12','lesson-host-composition-v13')
    p=API/'challenge-routing.schema.json';schema=json.loads(p.read_bytes())
    schema['properties']['evidence_project']=schema['properties']['challenger'].copy()
    schema['required'].append('evidence_project');p.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    p=API/'challenge_fixture.py'
    replace(p,"    challenger=pick(view,'principal','principal:repository-owner');subject=pick(view,'work')",
        "    challenger=pick(view,'principal','principal:repository-owner');subject=pick(view,'work');project=pick(view,'project')\n    project_header=M.artifact_ref(view,project)")
    replace(p,"owner_ref=challenger['identity'],evidence_refs=[binding['ref'],receipt_binding['ref']],relation_refs=[],successor_refs=[],",
        "owner_ref=challenger['identity'],evidence_refs=[binding['ref'],receipt_binding['ref']],\n        relation_refs=[{'relation_kind_ref':'relation.member-of','counterpart_kind':'project',\n            'counterpart_ref':project_header['version_ref'],'direction':'source'}],successor_refs=[],")
    replace(p,"'candidate_scope_ref':view.data['config']['scope_ref'],'challenge_contract':contract_header,'challenger':challenger_header,",
        "'candidate_scope_ref':view.data['config']['scope_ref'],'challenge_contract':contract_header,'challenger':challenger_header,\n        'evidence_project':project_header,")
    replace(p,"evidence_refs=[r['binding']['ref'] for r in accepted],relation_refs=[],successor_refs=[],",
        "evidence_refs=[r['binding']['ref'] for r in accepted],\n        relation_refs=[{'relation_kind_ref':'relation.challenges','counterpart_kind':view.handle.operations.endpoint_kind(subject,view.data['projection']),\n            'counterpart_ref':subject_header['version_ref'],'direction':'source'}],successor_refs=[],")
    p=API/'challenge_submission.py'
    replace(p,"        self.view.handle.operations.validate_record(body,header['carrier_ref'],self.view.data['projection'])\n        return raw", """        self.view.handle.operations.validate_record(body,header['carrier_ref'],self.view.data['projection'])
        project=self.routing()['evidence_project'];self.source_record(project)
        require(self.view.handle.operations.endpoint_kind(self.view.subjects[project['version_ref']],self.view.data['projection'])=='project',
            'independently selected evidence container is not a Project')
        require(body['scope_ref']==self.view.data['config']['scope_ref'] and body['successor_refs']==[]
            and body['relation_refs']==[{'relation_kind_ref':'relation.member-of','counterpart_kind':'project',
                'counterpart_ref':project['version_ref'],'direction':'source'}],
            'candidate Evidence Set scope or declared exact Project membership differs')
        require(not any(s['identity']==body['node_id'] for s in self.view.subjects.values()),'candidate Evidence Set identity already exists')
        return raw""")
    replace(p,"        selected=[];originals=[]", "        selected=[];originals=[];candidates=[]")
    replace(p,"                raw=self.candidate_evidence(row)", "                raw=self.candidate_evidence(row);candidates.append((row['artifact'],raw))")
    replace(p,"and body['relation_refs']==[] and body['successor_refs']==[],'candidate ownership/scope/routes or undeclared graph effects differ')", """and body['relation_refs']==[{'relation_kind_ref':'relation.challenges',
                'counterpart_kind':self.view.handle.operations.endpoint_kind(subject,self.view.data['projection'],allow_historical=True),
                'counterpart_ref':message['subject']['version_ref'],'direction':'source'}]
            and body['successor_refs']==[],'candidate ownership/scope/routes or undeclared graph effects differ')""")
    start=p.read_text().index("        version=body['node_id']+'@challenge.candidate.1'")
    end=p.read_text().index('    def preflight(',start)
    value=p.read_text();p.write_text(value[:start]+'''        version=body['node_id']+'@challenge.candidate.1'
        records=[(h['version_ref'],h['carrier_ref'],P.frame_parse(r),r,'artifact-instance') for h,r in candidates]
        records.append((version,carrier,body,raw,'artifact-instance'))
        # Bodies declare roles; each actual connection is a separate typed target.
        # No graph inference or canonical admission occurs during pure preparation.
        def header(v,c,b,r):
            return {'scope_ref':routing['candidate_scope_ref'],'identity_ref':b['node_id'],
                'version_ref':v,'carrier_ref':c,'byte_sha256':sha(r)}
        event_header=header(version,carrier,body,raw);connections=[]
        specs=[('relation.member-of',h,'evidence-set',routing['evidence_project'],'project',
            {'membership_role':'challenge-evidence-collection'}) for h,r in candidates]
        specs.append(('relation.challenges',event_header,'challenge-event',message['subject'],
            self.view.handle.operations.endpoint_kind(subject,self.view.data['projection'],allow_historical=True),
            {'challenge_contract_ref':routing['challenge_contract']['version_ref'],'challenge_mode':routing['response_mode'],
                'challenged_version_ref':message['subject']['version_ref']}))
        typed=[ref for ref,c in self.view.data['projection']['contracts'].items()
            if c['semantic_kind']=='typed-relation' and c['lifecycle_state'] in ('admitted-current','local-admitted-current')]
        require(len(typed)==1,'exact current Typed Relation carrier ambiguous');typed_carrier=typed[0]
        template_path='authority/relation-kinds/candidates/0006-definition-complete-instances/instances/typed-relations/challenges.json'
        template=copy.deepcopy(self.view.data['projection']['documents'][template_path])
        for i,(predicate,source_header,source_kind,target_header,target_kind,qualifiers) in enumerate(specs):
            signature,signature_binding=M.signature(self.view,predicate)
            connection={'relation_kind_ref':predicate,'signature_sha256':signature_binding['sha256'],
                'axis_ref':signature['payload']['axis_id'],
                'source':{'artifact':copy.deepcopy(source_header),'semantic_kind':source_kind},
                'target':{'artifact':copy.deepcopy(target_header),'semantic_kind':target_kind},'qualifiers':qualifiers}
            require(self.schemas.protocol_valid(URI+'typed-connection:v1-candidate',connection),'connection outside declared original signature')
            relation=copy.deepcopy(template)
            relation.update(node_id='typed-relation:R03-challenge:'+sha(raw)+':'+str(i),name='Exact candidate '+predicate,
                schema_version=self.view.data['projection']['contracts'][typed_carrier]['instance_discriminator']['value'],
                scope_ref=routing['candidate_scope_ref'],owner_ref=contract['owner_ref'],lifecycle_state='candidate',
                evidence_refs=body['evidence_refs'],relation_refs=[],successor_refs=[],challenge_route=routes['owner_route'],claim_ceiling=CLAIM)
            relation['payload']={'relation_kind_ref':predicate,
                'source':{'kind':source_kind,'ref':source_header['identity_ref'],'version_ref':source_header['version_ref']},
                'target':{'kind':target_kind,'ref':target_header['identity_ref'],'version_ref':target_header['version_ref']},
                'qualifiers':qualifiers,'relation_lifecycle_state':'candidate','relation_evidence_refs':body['evidence_refs']}
            relation_raw=P.source.encoded(relation);relation_version=relation['node_id']+'@challenge.candidate.1'
            records.append((relation_version,typed_carrier,relation,relation_raw,'typed-relation'));connections.append(connection)
        targets=[];planned=[]
        for v,c,b,r,category in records:
            decision='decision:R03-challenge-submit:'+sha(r)
            native={'category':category,'operation':'admit','version_ref':v,'carrier_ref':c,'record':b,
                'predecessor_ref':None,'decision_ref':decision,'contract':None,'content':self.view.handle.custody.content_entry(r)}
            core={'decision_ref':decision,'category':category,'operation':'admit','version_ref':v,
                'target_digest':self.view.handle.common.digest(native)}
            c_row=self.view.data['projection']['contracts'][c]
            planned.append({'raw':r,'body':b,'carrier':c,'version':v,'category':category,'core':core,
                'schema_binding':{'ref':c_row['schema_path'],'sha256':c_row['schema_sha256']}});targets.append(native)
        runtime={'schema_version':'lab-runtime-proposal/v1','proposal_id':message['request_ref']+':challenge-candidate',
            'expected_head':self.view.data['head']['transaction_digest'],'source_snapshot_digest':self.view.data['config']['source_snapshot_digest'],
            'scope_ref':routing['candidate_scope_ref'],'policy_ref':self.view.data['config']['policy_ref'],
            'challenge_route':self.view.data['config']['challenge_route'],'schemas':{},'targets':targets}
        runtime=self.view.handle.custody.with_originals(runtime,{v:r for v,c,b,r,category in records},{},exact_schema_bytes=True)
        before=self.view.handle.common.digest(self.view.data['projection'])
        _,computed=self.view.handle.operations.prepare(self.view.data['projection'],runtime,self.view.data['head']['transaction_digest'],self.view.data['config'])
        require(computed==[p['core'] for p in planned] and before==self.view.handle.common.digest(self.view.data['projection']),
            'native challenge closure cores differ or pure preparation changed source')
        return {'targets':planned,'connections':connections,'eligibility':eligibility,'routes':routes,'routing':routing,
            'originals':[contract_raw,challenger_raw,subject_raw,*originals]}
''' +value[end:])
    start=p.read_text().index("            plan=self._plan(message,outer,key);content=")
    end=p.read_text().index("            require(self.schemas.protocol_valid(URI+'change-proposal:v1-candidate',domain)",start)
    value=p.read_text();p.write_text(value[:start]+'''            plan=self._plan(message,outer,key);targets=[]
            for item in plan['targets']:
                content=writer.object(item['raw']);core=writer.object(self.view.handle.common.encoded(item['core']))
                metadata=writer.object(P.source.encoded({'schema_version':'lab-candidate-target-metadata/v1-candidate',
                    'category':item['category'],'decision_ref':item['core']['decision_ref'],'contract':None}))
                targets.append({'operation':'admit','artifact':{
                    'scope_ref':plan['routing']['candidate_scope_ref'],'identity_ref':item['body']['node_id'],
                    'version_ref':item['version'],'carrier_ref':item['carrier'],'byte_sha256':sha(item['raw']),
                    'candidate_contract_binding':item['schema_binding']},'predecessor':None,
                    'content':{'content_ref':content['ref'],'byte_sha256':content['sha256'],'size_bytes':len(item['raw']),'media_type':'application/json'},
                    'candidate_binding':metadata,'requested_effect':'Propose exact challenge, evidence or declared connection; owner admission remains pending.',
                    'decision_core_binding':core})
            eligibility=writer.object(plan['eligibility']);evidence=[eligibility,writer.object(original),writer.object(P.compact(plan['routing']))]
            evidence.extend(writer.object(raw) for raw in plan['originals'])
            domain={'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':message['request_ref']+':challenge-candidate',
                'actor':copy.deepcopy(message['actor']),'scope_ref':plan['routing']['candidate_scope_ref'],'base_cut':copy.deepcopy(outer),
                'source_profile_binding':{'ref':self.view.handle.manifest['profile_binding']['path'],'sha256':self.view.handle.manifest['profile_binding']['sha256']},
                'workspace_binding':self.vault.control_binding,'targets':targets,'schema_bindings':[],
                'connection_proposals':plan['connections'],'evidence_bindings':evidence,'idempotency_key':key,
                'challenge_route':self.view.data['config']['challenge_route'],'authority_effect':'none'}
''' +value[end:])
    p=API/'test_challenge_api.py'
    replace(p,"proposal=reply['message'];self.assertEqual(len(proposal['targets']),1)\n        target=proposal['targets'][0];", "proposal=reply['message'];self.assertEqual(len(proposal['targets']),4)\n        target=next(t for t in proposal['targets'] if t['artifact']['carrier_ref']=='cal.artifact-type.challenge-event/v1');")
    replace(p,"        self.assertEqual(proposal['connection_proposals'],[]);self.assertEqual(P.compact(self.view.data['projection']),self.projection)", """        connections=proposal['connection_proposals'];self.assertEqual(len(connections),2)
        self.assertEqual({c['relation_kind_ref'] for c in connections},{'relation.member-of','relation.challenges'})
        evidence=next(t for t in proposal['targets'] if t['artifact']['carrier_ref']=='cal.artifact-type.evidence-set/v1')
        evidence_raw=service.vault.material({'ref':evidence['content']['content_ref'],'sha256':evidence['content']['byte_sha256']})
        evidence_body=P.frame_parse(evidence_raw);self.assertEqual(evidence_body['lifecycle_state'],'candidate')
        self.assertEqual(evidence_body['relation_refs'][0]['counterpart_ref'],witness['routing']['evidence_project']['version_ref'])
        relations=[t for t in proposal['targets'] if t['artifact']['carrier_ref'].startswith('cal.artifact-type.typed-relation/')]
        self.assertEqual(len(relations),2)
        for connection in connections:
            matching=[]
            for t in relations:
                r=P.frame_parse(service.vault.material({'ref':t['content']['content_ref'],'sha256':t['content']['byte_sha256']}))
                if r['payload']['relation_kind_ref']==connection['relation_kind_ref']:matching.append(r)
            self.assertEqual(len(matching),1);self.assertEqual(matching[0]['payload']['qualifiers'],connection['qualifiers'])
            for end in ('source','target'):
                self.assertEqual(matching[0]['payload'][end]['version_ref'],connection[end]['artifact']['version_ref'])
        self.assertEqual(P.compact(self.view.data['projection']),self.projection)""")
    print(json.dumps({'result':'AUTHORED','successor':'api-v63','reason':'actual original relation_refs requirement; complete evidence and explicit typed connections',
        'strengthened_tests':['test_01_actual_challenge_proposal_preserves_exact_revision_and_original_bytes'],'authority_effect':'none'}))
if __name__=='__main__':main()
