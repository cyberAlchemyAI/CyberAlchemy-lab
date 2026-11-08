"""Closed exact carrier/fragment selection over the accepted protected reader.

Proof declarations are never promoted into domain instances. Reference-slot
coverage does not create relations; selected dispositions create dependencies.
Original Typed Relation and descriptor roles constrain connections separately.
"""
from dataclasses import dataclass
from contextlib import contextmanager
import copy
from urllib.parse import urljoin, urlparse, unquote
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from lab_contracts.codec import Refusal, need, sha as digest
from environment.body_json import parse_original as parse
from .reader import RoleReader, binding, source_cut
import json

from types import MappingProxyType

# Finite literal catalogue; never stringify arbitrary exceptions or values.
REFUSAL_CODES = MappingProxyType({'ELIGIBILITY_FULL_BINDING': 'SEMANTIC_F071A4957C89', 'JSON pointer required': 'SEMANTIC_1D47E39B98BE', 'POLICY_FULL_BINDING': 'SEMANTIC_28E8FB3044E6', 'SEMANTIC_CLOSED_FIELDS': 'SEMANTIC_CE58DB7F62A6', 'SEMANTIC_SCHEMA_ORIGIN': 'SEMANTIC_AA97C81D15F3', 'SEMANTIC_SELECTION_TYPE': 'SEMANTIC_F99D2922CE3B', 'SEMANTIC_SELECTOR_UNRESOLVED': 'SEMANTIC_75FFF1B92CE5', 'SEMANTIC_STATES': 'SEMANTIC_0C63A8A8F3C4', 'Typed Relation contract omitted': 'SEMANTIC_232341430741', 'actual original schema refused': 'SEMANTIC_3382342FBEF1', 'actual protected reader/independent graph anchor required': 'SEMANTIC_1E2DEBD2D896', 'actual qualifier contract refused': 'SEMANTIC_D52F39E117FA', 'actual semantic dependency cycle': 'SEMANTIC_4053CD4B5F06', 'captured fragment/type/schema binding differs': 'SEMANTIC_0D0C8BDD5BC9', 'carrier discriminator differs': 'SEMANTIC_1EF43F7B0C46', 'carrier is not exact original current lookup': 'SEMANTIC_A512037DE979', 'closed context selection required': 'SEMANTIC_3965BF28015E', 'current-context reference omitted': 'SEMANTIC_A4EA647ECCEA', 'declared identity absent': 'SEMANTIC_2B3A7B252184', 'declared nested/reference/items slot omitted or added': 'SEMANTIC_6EB9C3B518B5', 'declared reference location/disposition differs': 'SEMANTIC_D8A6777C7E53', 'declared wildcard on scalar': 'SEMANTIC_28FD381DE58C', 'descriptor discriminator differs': 'SEMANTIC_4DCF1A17C768', 'descriptor instance schema digest differs': 'SEMANTIC_988C0B197084', 'descriptor kind differs': 'SEMANTIC_A7CB2F009822', 'duplicate carrier profile': 'SEMANTIC_179480CF84B6', 'duplicate reference disposition': 'SEMANTIC_B1DEDC2A0A78', 'duplicate relation contract': 'SEMANTIC_F224E155853E', 'duplicate schema document path': 'SEMANTIC_7AA02B159FC9', 'duplicate semantic identity': 'SEMANTIC_EF7FD7F7E726', 'eligibility contains omitted/additional subjects': 'SEMANTIC_72B95D958BB0', 'eligibility source/profile/cut differs': 'SEMANTIC_BF5F349959A8', 'eligible version omitted': 'SEMANTIC_CB77ECEC2AC3', 'embedded declaration contract differs': 'SEMANTIC_44DAA609B1D1', 'exact captured declaration required': 'SEMANTIC_A3A5DCB22666', 'exact current Relation Kind proof differs': 'SEMANTIC_E2DB1C3AD720', 'exact descriptor role/pair differs': 'SEMANTIC_C8B433ACD8A3', 'exact native subject body/carrier/version/kind provenance differs': 'SEMANTIC_E4C76D07BC33', 'exact original declaration fragment omitted/substituted/duplicated': 'SEMANTIC_21F53133DD48', 'exact proof reference omitted': 'SEMANTIC_109ABE5011EA', 'external schema retrieval forbidden': 'SEMANTIC_7563CDDC5C64', 'graph source/profile/cut differs': 'SEMANTIC_D90520981D8A', 'graph version/effect differs': 'SEMANTIC_4C39BFB25462', 'historical/withdrawn carrier not eligible': 'SEMANTIC_4C37FE4031BD', 'independent eligibility pin differs': 'SEMANTIC_6111E30653EE', 'independent graph anchor mutated': 'SEMANTIC_16A8C94A490A', 'independent graph policy pin differs': 'SEMANTIC_B623CC50487F', 'invalid schema node': 'SEMANTIC_479D22BD4174', 'native category/carrier semantic kind mismatch': 'SEMANTIC_9587B0C2FDE6', 'native registered fragment/category differs': 'SEMANTIC_705844C34112', 'native registered version identity differs': 'SEMANTIC_7A7DD313128E', 'native supported identity absent': 'SEMANTIC_DB2E81B7DDE5', 'native version must qualify exact identity': 'SEMANTIC_6BB3E4E5D6CE', 'non-object relation_refs requires explicit original carrier contract': 'SEMANTIC_563570281209', 'original Relation Kind omitted': 'SEMANTIC_F051108927D0', 'original closed role lists required': 'SEMANTIC_6D9F97FC8F63', 'original declaration body provenance differs': 'SEMANTIC_F5A5BDB05199', 'original declaration proof omitted': 'SEMANTIC_EBFACFC3659B', 'original declaration schema selector differs': 'SEMANTIC_4A7B59205105', 'original descriptor digest differs': 'SEMANTIC_50E2D7B76F28', 'original global endpoint pair differs': 'SEMANTIC_ACA8075B9F5F', 'original kernel identity origin required': 'SEMANTIC_FD20A17E079A', 'original native identity fallback semantics differ': 'SEMANTIC_4FC94845EA00', 'original native identity function semantics differ': 'SEMANTIC_C860ECE00B56', 'original native registered-fragment/identity operation source differs': 'SEMANTIC_89D14DE71BB1', 'original qualifier reference omitted/added': 'SEMANTIC_91191692FEE4', 'original schema bytes differ': 'SEMANTIC_456223C7058A', 'pattern reference coverage requires explicit original key selector': 'SEMANTIC_21F7BF92BB2C', 'proof duplicate/kind spoof': 'SEMANTIC_27F9215EBABE', 'qualifier original selector/disposition differs': 'SEMANTIC_09242D9522E0', 'recursive reference coverage requires explicit bounded contract': 'SEMANTIC_A80E90C8A6D6', 'reference path incompatible with validated instance': 'SEMANTIC_44DDF5233871', 'reference scalar required': 'SEMANTIC_5A311BAB6980', 'registry selector is not exact admitted contract': 'SEMANTIC_4C8C0943D8C5', 'schema dependency outside closed documents': 'SEMANTIC_CAFE88924C04', 'schema path escape': 'SEMANTIC_8052BFB14FB9', 'self identity differs': 'SEMANTIC_0EE6341DC86A', 'semantic dependency omitted': 'SEMANTIC_687AB8328A4A', 'semantic edges duplicated/omitted/substituted': 'SEMANTIC_AE9ED3EB0F87', 'semantic node disconnected from selected roots': 'SEMANTIC_BA10063ADABF', 'semantic node omitted/kind spoofed': 'SEMANTIC_C145E01967B6', 'semantic relation endpoint absent/kind differs': 'SEMANTIC_1C86C050B85E', 'subject is not selected eligible-current version': 'SEMANTIC_C4294C0040E1', 'typed endpoint current version/kind differs': 'SEMANTIC_021891B9B460', 'typed endpoint omitted': 'SEMANTIC_53CAD01618DC', 'typed endpoint pair differs': 'SEMANTIC_5BCBFAD9834A', 'unique selected graph roots required': 'SEMANTIC_923CCCB1E9A9', 'unknown native category': 'SEMANTIC_A640F767BB8E', 'unselected carrier type': 'SEMANTIC_D1BB8ABD9A54', 'unselected native instance fragment': 'SEMANTIC_4E90BA2E96E6', 'unselected original schema': 'SEMANTIC_BE2DB8663E65'})

POLICY_SCHEMA_SHA = '6c21294529c01bc86014aa400f230d718e9ddc69e45f1e937e00cbd44ae7db8e'

def closed(value, fields, _label):
    need(type(value) is dict and set(value) == set(fields), 'SEMANTIC_CLOSED_FIELDS')

def canonical(value):
    # Original fragment structural identity; not the signed-control i64 codec.
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',', ':'),allow_nan=False).encode('utf-8')



def pointer(value, path):
    if path is None: return value
    if path.startswith('#'): path = path[1:]
    need(type(path) is str and (path == '' or path.startswith('/')), 'JSON pointer required')
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        try: value = value[int(part)] if type(value) is list else value[part]
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise Refusal('SEMANTIC_SELECTOR_UNRESOLVED') from None
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


@contextmanager
def _semantic_boundary(reader):
    # Preserve semantic reason codes across the reader's own safe-error boundary.
    # The reader still checks the original source/currentness after every body.
    # A failed post-check wins; no semantic result escapes a failed reader guard.
    failure = None
    with reader.boundary():
        try:
            yield
        except Exception as error:
            failure = error
    if failure is not None:
        raise failure


def _verify_graph(reader, policy_file_id, declared_edges, root_refs, anchor, policy_schema_raw):
    need(type(reader) is RoleReader and type(anchor) is GraphAnchor, 'actual protected reader/independent graph anchor required')
    sealed = canonical(anchor.__dict__)
    with _semantic_boundary(reader):
        need(anchor.source_binding == reader.selection['source_binding'] and anchor.profile_binding == reader.selection['profile_binding']
             and anchor.source_cut == reader.selection['source_cut'], 'graph source/profile/cut differs')
        raw = reader.read(policy_file_id,'semantic-policy'); need(digest(raw)==anchor.policy_binding['sha256'], 'independent graph policy pin differs')
        need(reader.files[policy_file_id]['binding'] == anchor.policy_binding, 'POLICY_FULL_BINDING')
        policy = parse(raw)
        Draft202012Validator(parse(policy_schema_raw)).validate(policy)
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
        need(reader.files[policy['eligibility_file_id']]['binding'] == anchor.eligibility_binding, 'ELIGIBILITY_FULL_BINDING')
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


def verify_graph(reader, policy_file_id, declared_edges, root_refs, anchor, *, policy_schema_raw):
    """Verify exact original semantic rules over the reviewed selected reader.

    This result is a bounded fixture/public-input consistency observation, never
    actual admission, current protected custody or original-engine execution.
    """
    try:
        need(type(reader) is RoleReader and type(anchor) is GraphAnchor, 'SEMANTIC_SELECTION_TYPE')
        need(type(policy_schema_raw) is bytes and len(policy_schema_raw) <= 64*1024*1024
             and digest(policy_schema_raw) == POLICY_SCHEMA_SHA, 'SEMANTIC_SCHEMA_ORIGIN')
        for name in ('policy_binding','eligibility_binding','source_binding','profile_binding'):
            binding(getattr(anchor,name))
        source_cut(anchor.source_cut)
        need(type(anchor.allowed_states) is tuple and anchor.allowed_states
             and len(set(anchor.allowed_states)) == len(anchor.allowed_states)
             and all(type(s) is str and 0 < len(s) <= 4096 for s in anchor.allowed_states), 'SEMANTIC_STATES')
        return _verify_graph(reader,policy_file_id,declared_edges,root_refs,anchor,policy_schema_raw)
    except Exception as error:
        code = 'SEMANTIC_UNEXPECTED_REFUSAL'
        if type(error) is Refusal and len(error.args) == 1 and type(error.args[0]) is str:
            code = REFUSAL_CODES.get(error.args[0], 'SEMANTIC_DEPENDENCY_REFUSED')
        raise Refusal(code) from None
