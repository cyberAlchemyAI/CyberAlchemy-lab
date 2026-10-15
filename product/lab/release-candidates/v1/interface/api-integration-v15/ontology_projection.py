"""Apply an exact selected native representation in an operator-owned store.

The selected mapper covers one complete, declared source closure. Caller JSON
cannot select a mapper, another ontology root or source authority. The native
events remain derived representations, with no Lab admission or global edge
authority. Other mapping scopes need their own qualified producer selection.
"""
import copy
import fcntl
import json
import os
from pathlib import Path
import secrets
import shutil

from . import protocol as P, artifact_model as M, workspace as W, handlers as H
from .auth import now,instant

ROOT=P.ROOT;HERE=P.HERE;SOURCE=P.source
MAPPER=HERE.parent/'current-mapped-context-v4'
MAPPER_PIN='38e24b3517ef1868c57fc21e58e300e578187303a888dd9b22ff20e086d3317b'
MAPPER_EXECUTION=HERE.parent/'current-mapped-context-v2-action-0148'
MAPPER_EXECUTION_PIN='a39fac194e95471f3311b870240c658114a75cd2f6a73162dc476d80e33cb72e'
PACKAGE_PIN='61eba56461293d8e056b71e2066d1ceec40aab633d8a4caf3ddaa550c57b981e'
CLAIM='Observed exact native representation in the separately granted owned candidate ontology store only. No Lab admission, global relation mutation, truth, active Agent or completed Work.'
def require(v,message):SOURCE.require(v,message)

def validate_control(policy,schemas):
    require(policy['schema_version']=='lab-local-ontology-projection-policy/v1-candidate','independent ontology policy required')
    control=policy['ontology_control']
    require(set(control)=={'routing_binding','method_binding'} and control['method_binding']==P.binding(
        str((HERE/'ontology_projection.py').relative_to(ROOT)),(HERE/'ontology_projection.py').read_bytes()),'ontology method selection differs')
    root,manifest=W.validate_scope(policy);b=control['routing_binding']
    rows=[r for r in manifest['materials'] if r['ref']==b['ref'] and r['sha256']==b['sha256']]
    require(len(rows)==1,'independent ontology routing missing')
    raw=W.read_private(root/rows[0]['path']);require(SOURCE.sha(raw)==b['sha256'],'ontology routing changed');route=P.frame_parse(raw)
    require(set(route)=={'schema_version','principal_ref','scope_ref','store_ref','branch_ref','root_identity',
        'mapping_binding','mapped_source_binding','mapped_package_binding','expected_lab_cut','authorization_basis',
        'not_before','expires_at','permitted_effects'},'closed ontology routing required')
    require(route['schema_version']=='lab-owned-ontology-routing/v1-candidate' and route['principal_ref']==policy['principal_ref']
        and route['scope_ref']==policy['scope_refs'][0] and route['permitted_effects']==['ontology-representation']
        and instant(route['not_before'])<=now()<min(instant(route['expires_at']),instant(policy['expires_at'])),
        'ontology routing actor/scope/period/effects differ')
    owned=W.safe(root/'ontology',0o700);st=owned.stat()
    require(route['root_identity']=={'device':st.st_dev,'inode':st.st_ino},'owned ontology root identity changed')
    require(route['mapping_binding']==P.binding(str((MAPPER/'policy.json').relative_to(ROOT)),(MAPPER/'policy.json').read_bytes())
        and route['mapped_source_binding']=={'ref':str((MAPPER/'source-manifest.json').relative_to(ROOT)),'sha256':MAPPER_PIN}
        and route['mapped_package_binding']=={'ref':str((MAPPER/'packages/0001/manifest.json').relative_to(ROOT)),'sha256':PACKAGE_PIN},
        'independently selected mapping/package differs')
    basis=route['authorization_basis']
    require(set(basis)=={'authority_scope','owner_principal_ref','evidence_bindings','policy_bindings','scope_refs','expires_at'}
        and basis['authority_scope']=='operator-local' and basis['owner_principal_ref']==policy['principal_ref']
        and basis['scope_refs']==[route['store_ref']] and basis['expires_at']==route['expires_at']
        and basis['evidence_bindings'] and basis['policy_bindings'],'ontology authority basis differs')
    for selected in basis['evidence_bindings']+basis['policy_bindings']:
        matches=[r for r in manifest['materials'] if r['ref']==selected['ref'] and r['sha256']==selected['sha256']]
        require(len(matches)==1,'independently selected ontology authority material missing')
        require(SOURCE.sha(W.read_private(root/matches[0]['path']))==selected['sha256'],'ontology authority material changed')
    return route

def rich_carriers(mapping,files,scope_ref,manifest_ref,owner):
    # Reuse the qualified producer's exact node/edge hydration calculation;
    # no Context eligibility, active Agent or Lesson application is inferred.
    D=SOURCE.custody_delivery()
    semantic={e['subject_identity']['subject_id']:e for name,raw in files.items() if name.startswith('semantic/') for e in [SOURCE.parse(raw)]}
    governance={g['semantic_ref']['semantic_event_id']:g for name,raw in files.items() if name.startswith('governance/') for g in [SOURCE.parse(raw)]}
    ontology_id=D.MAPPED.ONTOLOGY;scoped=scope_ref;bodies={};node_ids={};edge_ids={};correspondence=[]
    sha=SOURCE.sha;encoded=SOURCE.encoded
    def common(kind,identity,scope,basis):
        body=D.common(kind,identity,scope,basis)
        body.update(owner_ref=owner,claim_ceiling=CLAIM)
        return body
    for row in mapping['rows']:
        i=row['subject_identity'];e=semantic[i['subject_id']];state=e['complete_resulting_semantic_state']
        sr={'semantic_event_id':e['event_id'],'semantic_event_digest':e['event_digest'],'semantic_cursor':e['semantic_cursor']}
        g=governance[e['event_id']];require(g['semantic_ref']==sr and g['complete_resulting_governance_state']['semantic_ref']==sr,'native exact governance join differs')
        kind='ontology-node' if i['subject_kind']=='node' else 'ontology-edge'
        identity=kind+':'+i['subject_id'].split(':',1)[1];b=common(kind,identity,scoped,manifest_ref)
        correspondence.append({'native_identity':i,'carrier_identity':identity,'semantic_event_ref':sr,'governance_event_ref':g['event_id']})
        if kind=='ontology-node':
            node_ids[i['subject_id']]=identity
            a=row['artifact'];p=b['payload'];p.update(ontology_ref=ontology_id,ontology_manifest_ref=manifest_ref,
                node_type_ref=i['type_ref'],profile_ref=state['profile_ref'],branch='mixed',
                represented_subject={'kind':row['semantic_kind'],'ref':a['identity_ref'],'version_ref':a['version_ref'],'digest':a['byte_sha256']},
                semantic_state={'lifecycle':state['lifecycle'],'label':state['label'],'proposition':state['definition_or_claim'],
                    'semantic_components':[c['component_id'] for c in state['semantic_components']],
                    'semantic_definition_refs':[w['version_ref'] for w in row['definition_witnesses']],
                    'typed_properties':state['typed_properties']['values'],'use_obligations':[v['requirement'] for v in state['use_obligations']],
                    'forbidden_collapse':[v['context'] for v in state['forbidden_collapse']]},
                governance_binding={'authority_effect':'none','challenge_contract_ref':'protocol:R03-native-challenge-contract:'+sha(encoded(g['complete_resulting_governance_state']['challenge_contract'])),
                    'commitment_confidence_ref':g['complete_resulting_governance_state']['commitment_confidence']['scheme_ref'],
                    'evidence_confidence_ref':g['complete_resulting_governance_state']['evidence_confidence']['scheme_ref'],
                    'governance_event_refs':[g['event_id']],'semantic_event_ref':sr},provenance_refs=[row['origin']['source_locator']],replay_source=False)
        else:
            edge_ids[i['subject_id']]=identity;a=row['artifact'];p=b['payload'];p.update(ontology_ref=ontology_id,
                edge_mode='global-projection',relation_type_ref=row['closed_signature']['relation_kind_id'],
                source_node_ref=node_ids[state['source_node_id']],target_node_ref=node_ids[state['target_node_id']],
                direction=state['direction'],closed_qualifiers=row['qualifiers'],
                global_typed_relation_binding={'typed_relation_digest':a['byte_sha256'],'typed_relation_ref':a['identity_ref'],'typed_relation_version_ref':a['version_ref']},
                local_interpretation=None,lifecycle=state['lifecycle'],forbidden_collapse=[v['context'] for v in state['forbidden_collapse']],
                semantic_event_ref=sr,replay_source=False)
        bodies[identity]=b
    require(len(node_ids)==15 and len(edge_ids)==10,'actual carrier node/edge closure differs')
    return bodies,node_ids,edge_ids,correspondence

class OntologyProjection:
    def __init__(self,host,deadline):
        from .service import Service
        require(type(host) is Service,'actual selected Service required')
        self.host=host;self.policy=copy.deepcopy(host.channel.policy_guard());self.route=validate_control(self.policy,host.schemas)
        self.root=W.safe(host.vault.root/'ontology',0o700);self.mapper=SOURCE.custody_delivery().MAPPED
        require(Path(self.mapper.__file__).resolve()==MAPPER_EXECUTION/'build.py'
            and self.mapper.SELECTOR_ROOT==MAPPER_EXECUTION and self.mapper.HERE==MAPPER,
            'selected native mapping executable or original semantic/package root differs')
        self.before=None;self.plan=None;self.deadline=deadline
    def guard(self):
        from .auth import FACT_SCOPE
        FACT_SCOPE.require_outside_scope();self.host.channel.guard();self.host.schemas.guard()
        require(self.host.channel.policy_guard()==self.policy and validate_control(self.policy,self.host.schemas)==self.route,
            'ontology independent policy/route changed')
        require(self.host.handlers.current(),'ontology selected Lab source is not current')
        require(all(SOURCE.sha((HERE/p).read_bytes())==sha for p,sha in self.host.code_files.items()),'ontology selected API code changed')
        self.mapper.guard(MAPPER_EXECUTION_PIN)
    def check_deadline(self):
        if now()>=self.deadline:raise H.ApplicationError('deadline-exceeded','Strictest ontology effect deadline expired.')
    def head(self):
        raw=W.read_private(self.root/'HEAD.json');value=P.frame_parse(raw)
        require(set(value)=={'schema_version','sequence','store_ref','branch_ref','parent_head_sha256','generation','generation_sha256'}
            and value['schema_version']=='lab-owned-ontology-head/v1-candidate'
            and value['store_ref']==self.route['store_ref'] and value['branch_ref']==self.route['branch_ref']
            and type(value['sequence']) is int and value['sequence']>=0,'owned ontology head differs')
        if value['sequence']==0:require(value['generation'] is None and value['generation_sha256'] is None,'ontology genesis differs')
        else:
            require(type(value['generation']) is str and value['generation'].startswith('generation-')
                and '/' not in value['generation'] and '\\' not in value['generation'],'ontology generation path differs')
            generation=W.safe(self.root/value['generation'],0o700)
            mraw=W.read_private(generation/'manifest.json');require(SOURCE.sha(mraw)==value['generation_sha256'],'ontology committed generation changed')
            manifest=P.frame_parse(mraw);paths=set()
            for row in manifest['files']:
                relative=Path(row['path'])
                require(set(row)=={'path','sha256'} and not relative.is_absolute() and '..' not in relative.parts
                    and relative.as_posix()==row['path'] and row['path'] not in paths,'ontology generation file selector differs')
                paths.add(row['path']);require(SOURCE.sha(W.read_private(generation/relative))==row['sha256'],'ontology committed original bytes changed')
            actual={p.relative_to(generation).as_posix() for p in generation.rglob('*') if p.is_file()}
            require(actual==paths|{'manifest.json'} and not any(p.is_symlink() for p in generation.rglob('*')),'ontology committed file closure differs')
        return value,raw
    def cut(self,value,raw):
        return {'store_ref':value['store_ref'],'branch_ref':value['branch_ref'],'commit_sequence':value['sequence'],
            'commit_sha256':SOURCE.sha(raw),'source_profile_sha256':self.route['mapping_binding']['sha256'],'streams':[]}
    def preflight(self,message,outer,key):
        self.guard();require(message['idempotency_key']==key,'ontology envelope/key differs')
        require(message['authorization_basis']==self.route['authorization_basis'],'caller ontology authority differs from private selection')
        require(message['lab_source_cut']==outer==H.cut(self.host.handlers.view)==self.route['expected_lab_cut'],
            'ontology Lab source cut differs')
        require(message['mapping_binding']==self.route['mapping_binding'],'ontology caller mapping differs')
        self.before=self.head();require(message['ontology_expected_cut']==self.cut(*self.before),'independent ontology cut is stale')
        package=MAPPER/'packages/0001';manifest=SOURCE.parse((package/'manifest.json').read_bytes())
        require(SOURCE.sha((package/'manifest.json').read_bytes())==PACKAGE_PIN,'native mapped package pin differs')
        for row in manifest['files']:SOURCE.original(row)
        mapping=SOURCE.parse((package/'mapping.json').read_bytes());require(mapping['source_cut']==outer,'mapped source cut differs')
        selected=[r['artifact'] for r in mapping['rows']]
        require(len(selected)==25 and len({r['version_ref'] for r in selected})==25,'mapped exact source closure differs')
        requested=message['subject_refs'] or selected
        require(requested==selected,'selected atomic mapping requires its exact ordered source closure')
        view=self.host.handlers.view
        with M.model_read_batch(view):
            for header in selected:
                row=view.subjects.get(header['version_ref'])
                require(row is not None and row['effective_state'] in ('admitted-current','local-admitted-current')
                    and M.artifact_ref(view,row)==header and SOURCE.sha(M.record_bytes(view,row)[0])==header['byte_sha256'],
                    'ontology represented original source is changed, historical or unavailable')
        files={p.relative_to(package).as_posix():p.read_bytes() for family in ('semantic','governance') for p in sorted((package/family).glob('*.json'))}
        files['request.json']=(package/'request.json').read_bytes()
        expected=(package/'native-output.json').read_bytes();require(self.mapper.call([package/'semantic',package/'governance',package/'request.json'])==expected,
            'actual cold native mapped read differs')
        self.plan={'files':files,'represented_refs':selected,'native_expected':expected,'mapping':mapping,'fingerprint':SOURCE.sha(P.compact(message))}
        self.guard();return self.plan
    def apply(self,message,request,outer,key):
        self.guard();require(self.plan is not None and self.plan['fingerprint']==SOURCE.sha(P.compact(message)),'ontology plan changed')
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        lock=os.open('.selection.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            require(os.path.realpath('/proc/self/fd/'+str(fd))==str(self.root),'ontology root moved')
            require(self.head()==self.before,'ontology head changed before representation')
            self.check_deadline()
            generation='generation-'+SOURCE.sha(P.compact({'key':key,'request':self.plan['fingerprint']}))
            stage=self.root/('.stage-'+secrets.token_hex(16));stage.mkdir(mode=0o700)
            for name,raw in sorted(self.plan['files'].items()):
                path=stage/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);W.atomic(path,raw)
            actual=self.mapper.call([stage/'semantic',stage/'governance',stage/'request.json'])
            require(actual==self.plan['native_expected'],'actual staged native ontology replay differs')
            native=SOURCE.parse(actual);W.privacy(native)
            manifest={'schema_version':'lab-owned-ontology-generation/v1-candidate','mapping_binding':message['mapping_binding'],
                'lab_source_cut':outer,'ontology_preimage_cut':message['ontology_expected_cut'],'represented_refs':self.plan['represented_refs'],
                'files':[{'path':n,'sha256':SOURCE.sha(raw)} for n,raw in sorted(self.plan['files'].items())],
                'native_read_sha256':SOURCE.sha(actual),'request_binding':request,'authority_effect':'none','claim_ceiling':CLAIM}
            rich,nodes,edges,correspondence=rich_carriers(self.plan['mapping'],self.plan['files'],self.route['store_ref'],
                'owned-ontology-native-generation:'+generation,self.policy['principal_ref'])
            D=SOURCE.custody_delivery();ontology=D.common('ontology',self.mapper.ONTOLOGY,self.route['store_ref'],'owned-native-generation:'+generation)
            ontology.update(owner_ref=self.policy['principal_ref'],claim_ceiling=CLAIM,ontology_version='candidate-'+generation,
                purpose='Exact privately granted source representation',boundaries=['Owned candidate ontology only','No Lab admission or global edge mutation'],
                node_refs=list(nodes.values()),relation_refs=list(edges.values()),branch_refs=[outer['branch_ref']],role_assignment_refs=[],
                provenance_refs=[request['ref']],confidence_policy_ref='protocol:R03-original-byte-native-replay-confidence',promotion_state='draft',
                governance_rules=['Exact native tuples and source revisions','No source admission authority'])
            rich[self.mapper.ONTOLOGY]=ontology
            cut_identity='ontology-cut:owned-projection:'+SOURCE.sha(P.compact(native['cut']))
            cut_record=D.common('ontology-cut',cut_identity,self.route['store_ref'],'owned-native-generation:'+generation)
            cut_record.update(owner_ref=self.policy['principal_ref'],claim_ceiling=CLAIM)
            cut_record['payload'].update(ontology_ref=self.mapper.ONTOLOGY,node_refs=list(nodes.values()),edge_refs=list(edges.values()),
                semantic_cursor=native['cut']['semantic_cursor'],source_event_set_digest=native['cut']['source_event_set_digest'],
                calculated_digest=SOURCE.sha(P.compact(native['cut'])),integrity_result='pass',replay_source=False)
            rich[cut_identity]=cut_record
            for identity,record in rich.items():
                kind=record['kind'];version='v2' if kind=='ontology-node' else 'v1'
                selected_schema=SOURCE.parse((ROOT/'authority/artifact-types'/kind/version/'schema.json').read_bytes())
                P.Draft202012Validator(selected_schema,format_checker=self.host.schemas.checker).validate(record)
                name='carriers/'+identity.split(':',1)[0]+'-'+SOURCE.sha(identity.encode())+'.json'
                raw=P.compact(record);path=stage/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);W.atomic(path,raw)
                manifest['files'].append({'path':name,'sha256':SOURCE.sha(raw)})
            manifest['native_to_carrier_correspondence']=correspondence
            mraw=P.compact(manifest);W.atomic(stage/'manifest.json',mraw)
            self.guard();require(self.head()==self.before,'ontology head changed before publication')
            # Immutable generation publication uses Linux no-replace rename.
            import ctypes
            self.check_deadline()
            rename=ctypes.CDLL(None,use_errno=True).renameat2
            rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
            require(rename(fd,os.fsencode(stage.name),fd,os.fsencode(generation),1)==0,'ontology generation publication refused')
            os.fsync(fd);self.guard()
            head={'schema_version':'lab-owned-ontology-head/v1-candidate','sequence':self.before[0]['sequence']+1,
                'store_ref':self.route['store_ref'],'branch_ref':self.route['branch_ref'],'parent_head_sha256':SOURCE.sha(self.before[1]),
                'generation':generation,'generation_sha256':SOURCE.sha(mraw)}
            hraw=P.compact(head);temp='HEAD-'+secrets.token_hex(16)+'.json';W.atomic(self.root/temp,hraw)
            require(self.head()==self.before,'ontology head changed before commit')
            self.check_deadline()
            os.replace(temp,'HEAD.json',src_dir_fd=fd,dst_dir_fd=fd);os.fsync(fd)
            require(self.head()==(head,hraw),'ontology observed commit differs');self.guard()
            cut=self.cut(head,hraw);cutraw=P.compact(native['cut']);cutb=self.host.vault.object(cutraw)
            body=SOURCE.parse((ROOT/'authority/artifact-types/ontology-view/v1/fixtures/valid/record.json').read_bytes())
            identity='ontology-view:owned-projection:'+SOURCE.sha(hraw)
            body.update(node_id=identity,name='Observed owned native ontology projection',owner_ref=self.policy['principal_ref'],
                scope_ref=self.route['store_ref'],claim_ceiling=CLAIM,evidence_refs=[cutb['ref']],successor_refs=[])
            body['payload'].update(consumer_ref=self.policy['principal_ref'],cut_ref=cut_identity,cut_digest=SOURCE.sha(cutraw),
                source_event_set_digest=native['cut']['source_event_set_digest'],semantic_cursor=native['cut']['semantic_cursor'],
                ontology_ref=self.mapper.ONTOLOGY,selector_ref=native['context']['context_selector_ref'],
                intended_use='Represent the exact privately granted signed source closure',freshness_at=now().isoformat(),expires_at=self.route['expires_at'],
                selected_node_refs=list(nodes.values()),selected_edge_refs=list(edges.values()),
                exclusions=['Lab admission','global relation mutation','active Session memory'],replay_source=False)
            schema=SOURCE.parse((ROOT/'authority/artifact-types/ontology-view/v1/schema.json').read_bytes())
            P.Draft202012Validator(schema,format_checker=self.host.schemas.checker).validate(body)
            braw=P.compact(body);viewb=self.host.vault.object(braw);evidence=self.host.vault.object(mraw)
            ref={'scope_ref':self.route['store_ref'],'identity_ref':identity,'version_ref':identity+'@candidate.1',
                'carrier_ref':'cal.artifact-type.ontology-view/v1','byte_sha256':SOURCE.sha(braw)}
            result={'schema_version':'lab-ontology-projection-receipt/v1-candidate','request_binding':request,'lab_source_cut':outer,
                'ontology_applied_cut':cut,'mapping_binding':message['mapping_binding'],'represented_refs':self.plan['represented_refs'],
                'ontology_view':ref,'posture':'applied','gaps':[],'claim_ceiling':CLAIM,'authority_effect':'none','recovery_required':False}
            require(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:ontology-projection-receipt:v1-candidate',result),
                'actual ontology receipt violates the selected contract')
            self.guard();return result,[evidence,cutb,viewb]
        finally:os.close(lock);os.close(fd)
