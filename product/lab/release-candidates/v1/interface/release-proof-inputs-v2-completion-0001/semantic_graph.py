"""Closed exact carrier/fragment selection over the accepted protected reader.

Proof declarations are never promoted into domain instances. Reference-slot
coverage does not create relations; selected dispositions create dependencies.
Original Typed Relation and descriptor roles constrain connections separately.
"""
from dataclasses import dataclass
import copy
from urllib.parse import urljoin, urlparse, unquote
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from .protected_inputs import Refusal, ProtectedReader, need, closed, parse, digest, canonical


def pointer(value, path):
    if path is None: return value
    if path.startswith('#'): path = path[1:]
    need(type(path) is str and (path == '' or path.startswith('/')), 'JSON pointer required')
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        try: value = value[int(part)] if type(value) is list else value[part]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise Refusal('declared selector unresolved: '+path) from exc
    return value


def escape(key): return key.replace('~', '~0').replace('/', '~1')


class Schemas:
    """Exact selected local documents, matching original native URI namespace.

    No network retrieval, relative path substitution, alias graft, or narrowing
    fragment into an independently invented schema document.
    """
    def __init__(self, reader, rows):
        self.documents = {}; self.raw = {}; registry = Registry()
        for row in rows:
            closed(row, ('path', 'file_id'), 'schema document')
            need(row['path'] not in self.documents, 'duplicate schema document path')
            need(not row['path'].startswith('/') and '..' not in row['path'].split('/'), 'schema path escape')
            raw = reader.read(row['file_id'], 'governed-schema'); doc = parse(raw)
            Draft202012Validator.check_schema(doc)
            self.documents[row['path']] = doc; self.raw[row['path']] = raw
        for path, doc in self.documents.items():
            value = copy.deepcopy(doc)
            def clean(v):
                if type(v) is dict:
                    v.pop('$id', None)
                    for child in v.values(): clean(child)
                elif type(v) is list:
                    for child in v: clean(child)
            clean(value); value['$id'] = 'https://lab.invalid/'+path
            registry = registry.with_resource(value['$id'], Resource.from_contents(value, default_specification=DRAFT202012))
        self.registry = registry
        # Even unused declared dependencies must be closed and resolvable.
        def walk(node, path):
            if type(node) is dict:
                if '$ref' in node: self.resolve(path, node['$ref'])
                for v in node.values(): walk(v, path)
            elif type(node) is list:
                for v in node: walk(v, path)
        for path, doc in self.documents.items(): walk(doc, path)

    def resolve(self, path, ref):
        uri = urlparse(urljoin('https://lab.invalid/'+path, ref))
        need(uri.scheme == 'https' and uri.netloc == 'lab.invalid' and not uri.query,
             'external schema retrieval forbidden')
        other = unquote(uri.path.lstrip('/'))
        need(other in self.documents, 'schema dependency outside closed documents')
        selector = '#'+uri.fragment if uri.fragment else ''
        return other, selector, pointer(self.documents[other], selector)

    def validate(self, value, path, selector):
        need(path in self.documents, 'unselected original schema')
        pointer(self.documents[path], selector)
        try: Draft202012Validator({'$ref':'https://lab.invalid/'+path+(selector or '')}, registry=self.registry).validate(value)
        except Exception:
            # jsonschema diagnostics include the protected instance. Public
            # boundary evidence carries a bounded refusal code only.
            raise Refusal('actual original schema refused') from None

    def slots(self, path, selector, node=None):
        """Schema-resolved reference coverage including items and composition.

        Locations retain original document/fragment provenance. A recursive
        schema requires an explicit bounded successor policy; it is refused
        rather than silently truncated. relation_refs uses descriptor roles.
        """
        result = {}
        def visit(node, document, sp, ip, is_reference=False, stack=()):
            need(type(node) in (dict, bool), 'invalid schema node')
            if type(node) is bool: return
            token = (document, sp)
            need(token not in stack, 'recursive reference coverage requires explicit bounded contract')
            stack = stack+(token,)
            if '$ref' in node:
                other, target, resolved = self.resolve(document, node['$ref'])
                visit(resolved, other, target, ip, is_reference, stack)
            for keyword in ('allOf','anyOf','oneOf'):
                for index, child in enumerate(node.get(keyword, [])):
                    visit(child, document, sp+'/'+keyword+'/'+str(index), ip, is_reference, stack)
            for keyword in ('if','then','else'):
                if keyword in node:visit(node[keyword],document,sp+'/'+keyword,ip,is_reference,stack)
            for key,child in node.get('dependentSchemas',{}).items():
                visit(child,document,sp+'/dependentSchemas/'+escape(key),ip,is_reference,stack)
            need(not node.get('patternProperties'),
                 'pattern reference coverage requires explicit original key selector')
            types = node.get('type'); string = types == 'string' or (type(types) is list and 'string' in types)
            if is_reference and (string or type(node.get('const')) is str or
                                  ('enum' in node and all(type(x) is str for x in node['enum']))):
                result.setdefault(ip, set()).add((document, sp))
            for key, child in node.get('properties', {}).items():
                if key == 'relation_refs': continue
                visit(child, document, sp+'/properties/'+escape(key), ip+'/'+escape(key),
                      key in ('ref','refs') or key.endswith(('_ref','_refs')), stack)
            if 'items' in node:
                visit(node['items'], document, sp+'/items', ip+'/*', is_reference, stack)
            if 'contains' in node:
                visit(node['contains'],document,sp+'/contains',ip+'/*',is_reference,stack)
            for index, child in enumerate(node.get('prefixItems', [])):
                visit(child, document, sp+'/prefixItems/'+str(index), ip+'/'+str(index), is_reference, stack)
            if 'additionalProperties' in node and type(node['additionalProperties']) is dict:
                visit(node['additionalProperties'], document, sp+'/additionalProperties', ip+'/*', is_reference, stack)
        start = (selector or '').removeprefix('#')
        visit(pointer(self.documents[path], selector) if node is None else node, path, start, '')
        return {k: sorted(v) for k,v in result.items()}


def values(record, path):
    parts = path.split('/')[1:]
    def follow(v, index):
        if index == len(parts): return [v]
        key = parts[index].replace('~1','/').replace('~0','~')
        if key == '*':
            need(type(v) in (dict,list), 'declared wildcard on scalar')
            return [x for item in (v.values() if type(v) is dict else v) for x in follow(item,index+1)]
        if type(v) is dict:
            if key not in v: return []  # Original schema governs optional presence.
            return follow(v[key],index+1)
        if type(v) is list and key.isdigit() and int(key)<len(v): return follow(v[int(key)],index+1)
        raise Refusal('reference path incompatible with validated instance')
    return follow(record,0)


@dataclass(frozen=True)
class GraphAnchor:
    """Independent authenticated selector, never taken from public request."""
    policy_binding: dict
    eligibility_binding: dict
    source_binding: dict
    profile_binding: dict
    source_cut: dict
    allowed_states: tuple


def verify_graph(reader, policy_file_id, declared_edges, root_refs, anchor):
    need(type(reader) is ProtectedReader and type(anchor) is GraphAnchor, 'actual protected reader/independent graph anchor required')
    sealed = canonical(anchor.__dict__)
    with reader.boundary():
        need(anchor.source_binding == reader.anchor.source_binding and anchor.profile_binding == reader.anchor.profile_binding
             and anchor.source_cut == reader.anchor.source_cut, 'graph source/profile/cut differs')
        raw = reader.read(policy_file_id,'semantic-policy'); need(digest(raw)==anchor.policy_binding['sha256'], 'independent graph policy pin differs')
        policy = parse(raw)
        closed(policy, ('schema_version','registry_file_id','catalog_file_id','kernel_identity_file_id','kernel_operations_file_id','schemas','profiles','declarations','nodes','eligibility_file_id','proof_references','context_references','relation_contracts','authority_effect'), 'graph policy')
        need(policy['schema_version']=='lab-schema-declared-semantic-graph/v2-candidate' and policy['authority_effect']=='none', 'graph version/effect differs')
        schema = Schemas(reader,policy['schemas'])
        registry = parse(reader.read(policy['registry_file_id'],'history-proof'))
        catalog = parse(reader.read(policy['catalog_file_id'],'history-proof'))
        need(digest(reader.read(policy['kernel_operations_file_id'],'host-dependency'))=='94d294dc4752fc84df657254137fe69b0bdceebb1a8b692784bed6ba1942d86c','original native registered-fragment/identity operation source differs')
        native_identity = reader.read(policy['kernel_identity_file_id'],'host-dependency')
        # Rule origin must be the selected original function, not an arbitrary same-name helper.
        import ast
        tree = ast.parse(native_identity.decode()); identity_functions = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='identity']
        need(len(identity_functions)==1, 'original kernel identity origin required')
        function = identity_functions[0]
        import hashlib
        need(hashlib.sha256(ast.dump(function,include_attributes=False).encode()).hexdigest()=='7e888c05121c4acfed842e757766fd3e478ae4ad1205f7b09ff99e0bf9d3fcf9', 'original native identity function semantics differ')
        fallback = ('definition_id','artifact_type_ref','node_id','record_id','migration_manifest_id','product_id','project_id')
        # Extract tuple constants without executing original kernel or fake callbacks.
        tuples = [tuple(v.value for v in n.elts) for n in ast.walk(function) if isinstance(n,ast.Tuple) and all(isinstance(v,ast.Constant) and type(v.value) is str for v in n.elts)]
        need(fallback in tuples, 'original native identity fallback semantics differ')
        profiles = {}
        for p in policy['profiles']:
            closed(p,('profile_id','carrier_ref','instance_schema_selector','registry_pointer','descriptor_file_id','descriptor_pointer','fields'), 'carrier selection')
            carrier=p['carrier_ref'];pid=p['profile_id'];need(pid not in profiles,'duplicate carrier profile')
            contract=pointer(registry,p['registry_pointer'])
            need(contract in registry['admitted_contracts'] and contract['artifact_type_ref']==carrier,
                 'registry selector is not exact admitted contract')
            need(contract['lifecycle_state'] in ('admitted-current','local-admitted-current'), 'historical/withdrawn carrier not eligible')
            need(registry['current_by_identity'].get(carrier.rsplit('/',1)[0])==carrier,
                 'carrier is not exact original current lookup')
            descriptor_raw=reader.read(p['descriptor_file_id'],'governed-descriptor')
            need(digest(descriptor_raw)==contract['artifact_sha256'],'original descriptor digest differs')
            descriptor=pointer(parse(descriptor_raw),p['descriptor_pointer'])
            rows=[r for r in catalog['rows'] if r['represented_contract_ref']==carrier]
            need(len(rows)==1,'exact captured declaration required'); captured=rows[0]
            need(captured['selector']==p['descriptor_pointer'] and captured['source_binding']['sha256']==digest(descriptor_raw)
                 and captured['instance_schema_binding']=={'ref':contract['schema_path'],'sha256':contract['schema_sha256']}
                 and captured['instance_schema_selector']==contract['schema_selector'], 'captured fragment/type/schema binding differs')
            need(contract['schema_sha256']==digest(schema.raw[contract['schema_path']]),'original schema bytes differ')
            if p['descriptor_pointer']:
                need(captured['representation_kind']=='embedded-contract-declaration' and descriptor['artifact_type_ref']==carrier
                     and all(descriptor[k]==contract[k] for k in ('semantic_kind','schema_path','schema_sha256','schema_selector')),
                     'embedded declaration contract differs')
                identity_field=None; roles=[]; allowed=[]
                # Fragment remains proof declaration; instances use original native fallback.
            else:
                need(captured['representation_kind']=='source-file-descriptor', 'descriptor kind differs')
                identity_field=descriptor.get('instance_contract',{}).get('identity_field')
                roles=descriptor.get('relation_roles',[]);allowed=descriptor.get('allowed_relation_kinds',[])
                need(type(roles)is list and type(allowed)is list, 'original closed role lists required')
                if identity_field:
                    need(descriptor['instance_contract'].get('instance_discriminator')==contract['instance_discriminator'], 'descriptor discriminator differs')
                need(descriptor.get('schema_digest')==contract['schema_sha256'], 'descriptor instance schema digest differs')
            instance_selector=p['instance_schema_selector']
            registered=instance_selector=='#/properties/registered_types/items'
            need(instance_selector==contract['schema_selector'] or (registered and carrier=='cal.artifact-type.artifact-type/v3'), 'unselected native instance fragment')
            slots=schema.slots(contract['schema_path'],instance_selector)
            fields={}
            for f in p['fields']:
                closed(f,('instance_pointer','schema_locations','disposition'),'reference disposition')
                key=f['instance_pointer'];need(key not in fields,'duplicate reference disposition')
                locations=[tuple(x) for x in f['schema_locations']]
                need(locations==slots.get(key) and f['disposition'] in ('semantic-node','verified-proof','current-context','self-identity'), 'declared reference location/disposition differs')
                fields[key]=f
            need(set(fields)==set(slots),'declared nested/reference/items slot omitted or added')
            profiles[pid]=(contract,descriptor,identity_field,roles,allowed,fields,instance_selector,carrier)
        # Separately validate original declaration fragments. No instance node is synthesized.
        declaration_count=0; seen_declarations=set()
        expected_declarations={(r['source_binding']['sha256'],r['selector']):r
            for r in catalog['rows'] if r['representation_kind']=='embedded-contract-declaration'}
        for d in policy['declarations']:
            closed(d,('file_id','pointer','schema_path','schema_selector'),'declaration proof')
            declaration_raw=reader.read(d['file_id'],'governed-descriptor')
            token=(digest(declaration_raw),d['pointer'])
            need(token in expected_declarations and token not in seen_declarations,
                 'exact original declaration fragment omitted/substituted/duplicated')
            captured=expected_declarations[token]
            metas=[c for c in registry['admitted_contracts'] if c['artifact_type_ref']==captured['meta_carrier_ref']]
            need(len(metas)==1 and d['schema_path']==metas[0]['schema_path']
                 and digest(schema.raw[d['schema_path']])==metas[0]['schema_sha256']
                 and d['schema_selector']=='#/properties/registered_types/items',
                 'original declaration schema selector differs')
            body=pointer(parse(declaration_raw),d['pointer'])
            need(digest(canonical(body))==captured['body_structural_sha256']
                 and body['artifact_type_ref']==captured['represented_contract_ref'],
                 'original declaration body provenance differs')
            seen_declarations.add(token)
            schema.validate(body,d['schema_path'],d['schema_selector']);declaration_count+=1
        need(seen_declarations==set(expected_declarations),'original declaration proof omitted')
        eraw=reader.read(policy['eligibility_file_id'],'history-proof')
        need(digest(eraw)==anchor.eligibility_binding['sha256'],'independent eligibility pin differs')
        eligibility=parse(eraw)
        closed(eligibility,('schema_version','source_binding','profile_binding','source_cut','current_by_identity','subjects','authority_effect'), 'eligibility selection')
        need(eligibility['schema_version']=='lab-native-subject-selection/v1-candidate' and eligibility['authority_effect']=='none'
             and all(eligibility[k]==getattr(anchor,k) for k in ('source_binding','profile_binding','source_cut')), 'eligibility source/profile/cut differs')
        nodes={}; selected_ids=[]
        for n in policy['nodes']:
            closed(n,('file_id','profile_id','version_ref','category'),'semantic node selection')
            need(n['profile_id'] in profiles,'unselected carrier type')
            record_raw=reader.read(n['file_id'],'governed-record');record=parse(record_raw)
            contract,descriptor,field,roles,allowed,fields,instance_selector,carrier=profiles[n['profile_id']]
            need(n['category']in ('artifact-instance','definition','relation-kind','typed-relation','artifact-type'),'unknown native category')
            need(n['category']=={'definition':'definition','artifact-type':'artifact-type',
                 'relation-kind':'relation-kind','typed-relation':'typed-relation'}.get(contract['semantic_kind'],'artifact-instance'),
                 'native category/carrier semantic kind mismatch')
            registered=instance_selector=='#/properties/registered_types/items'
            need(registered==(n['category']=='artifact-type'),'native registered fragment/category differs')
            if not registered:need(pointer(record,contract['instance_discriminator']['path'])==contract['instance_discriminator']['value'],'carrier discriminator differs')
            schema.validate(record,contract['schema_path'],instance_selector)
            if registered:
                need(n['version_ref']==record['artifact_type_ref'],'native registered version identity differs')
                ident=record['artifact_type_ref'].rsplit('/',1)[0]
            elif field:
                need(field in record and type(record[field])is str,'declared identity absent');ident=record[field]
            else:
                hits=[record[k] for k in fallback if k in record];need(hits and type(hits[0])is str,'native supported identity absent');ident=hits[0]
            if not registered:
                need(n['version_ref'].startswith(ident+'@') and len(n['version_ref'])>len(ident)+1,
                     'native version must qualify exact identity')
            need(ident not in nodes,'duplicate semantic identity')
            subject=eligibility['subjects'].get(n['version_ref'])
            need(type(subject)is dict, 'eligible version omitted')
            closed(subject,('identity','version_ref','category','kind','effective_state','carrier_ref','source'),'native subject metadata')
            need(subject['identity']==ident and subject['version_ref']==n['version_ref'] and subject['kind']==contract['semantic_kind']
                 and subject['carrier_ref']==carrier and subject['category']==n['category'] and subject['source']=={'path':reader.files[n['file_id']]['logical_path'],'sha256':digest(record_raw)}, 'exact native subject body/carrier/version/kind provenance differs')
            need(subject['effective_state'] in anchor.allowed_states and eligibility['current_by_identity'].get(ident)==n['version_ref'], 'subject is not selected eligible-current version')
            nodes[ident]=(record,subject,n['profile_id']); selected_ids.append(n['file_id'])
        need(len(selected_ids)==len(set(selected_ids)) and set(selected_ids)=={i for i,r in reader.files.items() if r['kind']=='governed-record'},'semantic node omitted/kind spoofed')
        need(set(eligibility['subjects'])=={n['version_ref']for n in policy['nodes']} and set(eligibility['current_by_identity'])==set(nodes),'eligibility contains omitted/additional subjects')
        proofs={}
        for row in policy['proof_references']:
            closed(row,('reference','file_id'),'proof reference')
            need(row['reference']not in proofs and reader.files[row['file_id']]['kind']!='governed-record','proof duplicate/kind spoof')
            reader.read(row['file_id']);proofs[row['reference']]=row['file_id']
        contexts=policy['context_references'];need(type(contexts)is list and len(contexts)==len(set(contexts)),'closed context selection required')
        relations={}
        for r in policy['relation_contracts']:
            closed(r,('file_id','registry_file_id','registry_pointer','qualifier_fields'),'relation contract selection')
            entry=pointer(parse(reader.read(r['registry_file_id'],'history-proof')),r['registry_pointer'])
            rr=reader.read(r['file_id'],'governed-descriptor');record=parse(rr)
            need(entry['instance_sha256']==digest(rr) and entry['lifecycle_state']=='admitted-current'
                 and entry['relation_kind_ref']==record['payload']['relation_kind_id'],'exact current Relation Kind proof differs')
            need(entry['relation_kind_ref']not in relations,'duplicate relation contract');relations[entry['relation_kind_ref']]=(record['payload'],r['qualifier_fields'],entry['instance_path'])
        actual=set()
        def reference(ident,ref,disposition):
            if ref is None:return  # Original nullable schema is enforced separately.
            need(type(ref)is str,'reference scalar required')
            if disposition=='semantic-node':
                versions={v[1]['version_ref']:k for k,v in nodes.items()}
                target=ref if ref in nodes else versions.get(ref)
                need(target in nodes,'semantic dependency omitted');actual.add((ident,target))
            elif disposition=='verified-proof':need(ref in proofs,'exact proof reference omitted')
            elif disposition=='current-context':need(ref in contexts,'current-context reference omitted')
            else:need(ref==ident or ref.startswith(ident+'@'),'self identity differs')
        for ident,(record,subject,carrier) in nodes.items():
            c,d,f,roles,allowed,fields,instance_selector,original_carrier=profiles[carrier]
            for key,field in fields.items():
                for value in values(record,key):reference(ident,value,field['disposition'])
            for rel in record.get('relation_refs',[]):
                need(type(rel)is dict,'non-object relation_refs requires explicit original carrier contract')
                other=rel['counterpart_ref'];kind=rel['counterpart_kind'];direction=rel['direction'];rk=rel['relation_kind_ref']
                need(other in nodes and nodes[other][1]['kind']==kind,'semantic relation endpoint absent/kind differs')
                need(rk in allowed and len([x for x in roles if x['relation_kind_ref']==rk and x['direction']==direction and kind in x['counterpart_kinds']])==1,'exact descriptor role/pair differs')
                need(rk in relations,'original Relation Kind omitted')
                pair={'source_kind':c['semantic_kind'],'target_kind':kind} if direction=='source' else {'source_kind':kind,'target_kind':c['semantic_kind']}
                need(pair in relations[rk][0]['allowed_endpoint_pairs'],'original global endpoint pair differs')
                actual.add((ident,other) if direction=='source' else (other,ident))
            if c['semantic_kind']=='typed-relation':
                payload=record['payload'];rk=payload['relation_kind_ref'];need(rk in relations,'Typed Relation contract omitted')
                rc,qfields,qualifier_document=relations[rk]
                for endpoint in (payload['source'],payload['target']):
                    need(endpoint['ref']in nodes,'typed endpoint omitted');other=nodes[endpoint['ref']][1]
                    need(other['version_ref']==endpoint['version_ref'] and other['kind']==endpoint['kind'],'typed endpoint current version/kind differs')
                need({'source_kind':payload['source']['kind'],'target_kind':payload['target']['kind']}in rc['allowed_endpoint_pairs'],'typed endpoint pair differs')
                qc=rc['qualifier_contract']; qschema={'type':'object','additionalProperties':False,'required':qc['required_axes'],'properties':qc['properties']}
                try:Draft202012Validator(qschema).validate(payload['qualifiers'])
                except Exception:raise Refusal('actual qualifier contract refused')from None
                # Original Relation Kind qualifier schema is the native derived
                # closed protocol. Its dispositions are independently selected;
                # exact version refs must not be presumed proof or role authority.
                # Traverse the actual derived qualifier protocol with the same
                # nested/items/composition rules as carrier instance fields.
                # Provenance locations remain inside the original Relation Kind.
                qualifier_slots=schema.slots(qualifier_document,'#/payload/qualifier_contract',qschema)
                qmap={}
                for field in qfields:
                    closed(field,('instance_pointer','schema_locations','disposition'),'qualifier reference disposition')
                    key=field['instance_pointer'];need(key not in qmap
                        and [tuple(x) for x in field['schema_locations']]==qualifier_slots.get(key)
                        and field['disposition']in ('semantic-node','verified-proof','current-context','self-identity'),'qualifier original selector/disposition differs')
                    qmap[key]=field
                need(set(qmap)==set(qualifier_slots),'original qualifier reference omitted/added')
                for key,field in qmap.items():
                    for value in values(payload['qualifiers'],key):reference(ident,value,field['disposition'])
        need(type(root_refs)is list and root_refs and len(root_refs)==len(set(root_refs))and set(root_refs)<=set(nodes),'unique selected graph roots required')
        declared=[]
        for edge in declared_edges:
            closed(edge,('source','dependency'),'semantic edge');declared.append((edge['source'],edge['dependency']))
        need(len(declared)==len(set(declared)) and set(declared)==actual,'semantic edges duplicated/omitted/substituted')
        adjacency={k:[]for k in nodes}
        for left,right in actual:adjacency[left].append(right)
        active=set();done=set()
        def visit(key):
            need(key not in active,'actual semantic dependency cycle')
            if key in done:return
            active.add(key)
            for child in adjacency[key]:visit(child)
            active.remove(key);done.add(key)
        for key in nodes:visit(key)
        reached=set()
        def reach(key):
            if key in reached:return
            reached.add(key)
            for child in adjacency[key]:reach(child)
        for key in root_refs:reach(key)
        need(reached==set(nodes),'semantic node disconnected from selected roots')
        need(canonical(anchor.__dict__)==sealed,'independent graph anchor mutated')
        result={'policy_sha256':digest(raw),'nodes':len(nodes),'edges':len(actual),'declarations':declaration_count,'profiles':len(profiles),'proof_references':len(proofs),'authority_effect':'none','admission_or_owner_authority':False,'original_engine_execution_claim':False}
    return result
