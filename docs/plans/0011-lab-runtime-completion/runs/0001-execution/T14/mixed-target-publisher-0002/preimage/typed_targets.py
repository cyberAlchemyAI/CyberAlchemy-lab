"""Selected original-schema target bytes; no admission or native-event wrapper."""
import copy,hashlib,json
from pathlib import PurePosixPath
from urllib.parse import unquote,urljoin,urlparse
from jsonschema import Draft202012Validator
from referencing import Registry,Resource
from referencing.jsonschema import DRAFT202012

class Refusal(ValueError):pass
def need(value,reason):
    if not value:raise Refusal(reason)
def closed(value,fields):need(type(value) is dict and set(value)==set(fields),'closed target fields required')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def parse(raw):
    need(type(raw) is bytes and len(raw)<=16*1024*1024,'bounded original bytes required')
    def pairs(rows):
        out={}
        for key,value in rows:need(key not in out,'duplicate JSON key');out[key]=value
        return out
    def invalid(value):raise Refusal('nonfinite JSON value')
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)
    except (ValueError,UnicodeError):raise Refusal('strict original JSON refused') from None
def relative(value):
    need(type(value) is str and bool(value) and '\\' not in value and '\0' not in value,'relative path required')
    path=PurePosixPath(value);need(not path.is_absolute() and path.as_posix()==value and '..' not in path.parts and value!='.','canonical relative path required');return value
def pointer(value,selector):
    need(selector is None or type(selector) is str,'explicit original selector required')
    if selector is None:return value
    selector=selector.removeprefix('#');need(selector=='' or selector.startswith('/'),'JSON pointer required')
    for part in selector.split('/')[1:]:
        part=part.replace('~1','/').replace('~0','~')
        try:value=value[int(part)] if type(value) is list else value[part]
        except (ValueError,KeyError,IndexError,TypeError):raise Refusal('original selector unresolved') from None
    return value
def privacy(value):
    if type(value) is dict:
        for key,child in value.items():
            need(key.lower() not in {'private_key','private_key_bytes','private_credentials','access_token','refresh_token','password','session_memory','short_memory'},'private body export forbidden')
            privacy(key);privacy(child)
    elif type(value) is list:
        for child in value:privacy(child)
    elif type(value) is str:
        need('PRIVATE KEY-----' not in value,'private key export forbidden')
        need(not any(part=='.local' or part=='.env' or part.startswith('.env.')
                     for part in value.replace('\\','/').split('/')),'private path export forbidden')

FAMILIES={'artifact-instance':'artifact-instance','typed-relation':'typed-relation',
          'definition':'definition','registry-descriptor':'artifact-type',
          'relation-kind':'relation-kind','state-carrier':'artifact-instance',
          'semantic-history-carrier':'artifact-instance','governance-history-carrier':'artifact-instance'}

class OriginalSchemas:
    """Whole pinned documents; fragment selection stays in the whole registry."""
    def __init__(self,bindings,raw_documents):
        need(type(bindings) is list and bindings,'independently selected original schema closure required')
        self.documents={};registry=Registry()
        for row in bindings:
            closed(row,('path','sha256'));path=relative(row['path'])
            need(path not in self.documents and path in raw_documents,'duplicate or missing schema document')
            raw=raw_documents[path];need(sha(raw)==row['sha256'],'original schema bytes changed')
            doc=parse(raw);Draft202012Validator.check_schema(doc);self.documents[path]=doc
            value=copy.deepcopy(doc)
            def clean(node):
                if type(node) is dict:
                    node.pop('$id',None)
                    for child in node.values():clean(child)
                elif type(node) is list:
                    for child in node:clean(child)
            clean(value);value['$id']='https://lab.invalid/'+path
            registry=registry.with_resource(value['$id'],Resource.from_contents(value,default_specification=DRAFT202012))
        need(set(raw_documents)==set(self.documents),'unselected schema input')
        def refs(node,path):
            if type(node) is dict:
                for keyword in ('$ref','$dynamicRef'):
                    if keyword in node:
                        uri=urlparse(urljoin('https://lab.invalid/'+path,node[keyword]))
                        need(uri.scheme=='https' and uri.netloc=='lab.invalid' and not uri.query,'remote schema retrieval forbidden')
                        other=relative(unquote(uri.path.lstrip('/')));need(other in self.documents,'original schema dependency missing')
                        pointer(self.documents[other],'#'+uri.fragment if uri.fragment else None)
                for child in node.values():refs(child,path)
            elif type(node) is list:
                for child in node:refs(child,path)
        for path,doc in self.documents.items():refs(doc,path)
        self.registry=registry
    def validate(self,value,path,selector):
        need(path in self.documents,'unselected original schema');pointer(self.documents[path],selector)
        try:Draft202012Validator({'$ref':'https://lab.invalid/'+path+(selector or '')},registry=self.registry).validate(value)
        except Exception:raise Refusal('actual original schema refused') from None

def adapt(raw,spec,schemas):
    """Retain bytes; structural fit does not resolve semantics/scope/authority."""
    closed(spec,('family','category','carrier_ref','schema_path','schema_selector','identity_selector','identity_ref','raw_sha256'))
    family=spec['family'];need(type(family) is str and family in FAMILIES,'unsupported target family; native intents require original materializer')
    need(spec['category']==FAMILIES[family],'target family/category mismatch')
    bases={'typed-relation':'typed-relation','definition':'definition','relation-kind':'relation-kind',
           'state-carrier':'project-state','semantic-history-carrier':'project-semantic-event-history',
           'governance-history-carrier':'project-governance-event-history'}
    need(type(spec['carrier_ref']) is str and bool(spec['carrier_ref']),'explicit original carrier required')
    if family in bases:need(spec['carrier_ref'].startswith('cal.artifact-type.'+bases[family]+'/'),'carrier/family mismatch')
    need(sha(raw)==spec['raw_sha256'],'selected target bytes changed');record=parse(raw);privacy(record)
    selector=spec['schema_selector']
    if family=='registry-descriptor':
        need(spec['carrier_ref']=='cal.artifact-type.artifact-type/v3'
             and selector=='#/properties/registered_types/items'
             and spec['identity_selector']=='/artifact_type_ref','original raw registry descriptor selector required')
    schemas.validate(record,spec['schema_path'],selector)
    identity=pointer(record,spec['identity_selector']);need(type(identity) is str and identity and identity==spec['identity_ref'],'exact selected target identity differs')
    kind=record.get('kind') if type(record) is dict else None
    required={'typed-relation':'typed-relation','relation-kind':'relation-kind','state-carrier':'project-state',
              'semantic-history-carrier':'project-semantic-event-history','governance-history-carrier':'project-governance-event-history'}
    if family in required:need(kind==required[family],'target kind/family mismatch')
    if family=='definition':
        need(kind=='definition' or record.get('classification',{}).get('semantic_kind')=='definition',
             'definition body/semantic classification differs')
    return {'original_bytes':raw,'metadata':{'family':family,'category':spec['category'],
            'carrier_ref':spec['carrier_ref'],'identity_ref':identity,'schema_path':spec['schema_path'],
            'schema_selector':selector,'sha256':sha(raw),'size_bytes':len(raw),
            'schema_shape_validated':True,'original_semantic_scope_native_validation':False,
            'owner_authority_resolved':False,'canonical_admission':False,'authority_effect':'none'}}

def prepare_byte_bundle(items,bundle_id,*,schema_binding_sha256):
    need(type(bundle_id) is str and bundle_id and all(c.isalnum() or c=='-' for c in bundle_id),'flat candidate bundle id required')
    need(type(items) is list and items,'complete selected technical target list required')
    files={};rows=[];identities=set();total=0
    for item in items:
        closed(item,('output_path','adapted'));name=relative(item['output_path']);value=item['adapted']
        need(name.startswith('targets/') and name.endswith('.json') and name not in files,'unique technical target output required')
        metadata=value['metadata'];need(metadata['canonical_admission'] is False and metadata['owner_authority_resolved'] is False,'structural evidence cannot claim admission')
        identity=metadata['identity_ref'];need(identity not in identities,'duplicate selected identity');identities.add(identity)
        need(sha(value['original_bytes'])==metadata['sha256'],'adapted bytes changed')
        total+=len(value['original_bytes']);need(total<=128*1024*1024,'technical selected byte budget exceeded')
        files[name]=value['original_bytes'];rows.append({'path':name,**metadata})
    manifest={'schema_version':'lab-owned-technical-target-byte-bundle/v1-candidate','bundle_id':bundle_id,
              'schema_binding_sha256':schema_binding_sha256,'targets':rows,'files':{p:sha(raw) for p,raw in sorted(files.items())},
              'coverage':'exact supplied target bytes only','native_decision_cores_materialized':False,
              'semantic_governance_events_generated':False,'canonical_admission':False,'actual_owner_outcome':None,
              'runtime_activations':0,'external_effects':0,'authority_effect':'none'}
    files['bundle.json']=encode(manifest)
    receipt={'schema_version':'lab-owned-technical-byte-publication-receipt/v1-candidate','bundle_id':bundle_id,
             'whole_bundle_manifest_sha256':sha(files['bundle.json']),'target_files':manifest['files'],
             'commit_point':'atomic-no-replace-owned-bundle-directory','authority_effect':'none',
             'native_admission_receipt':False,'actual_owner_outcome':None,'canonical_admission':False}
    files['technical-receipt.json']=encode(receipt)
    return {'files':files,'pins':{'bundle_sha256':sha(files['bundle.json']),'whole_receipt_sha256':sha(files['technical-receipt.json'])}}

def verify_byte_bundle(files,pins):
    closed(pins,('bundle_sha256','whole_receipt_sha256'))
    need(sha(files.get('bundle.json',b''))==pins['bundle_sha256'],'independent whole bundle pin differs')
    need(sha(files.get('technical-receipt.json',b''))==pins['whole_receipt_sha256'],'independent complete receipt pin differs')
    manifest=parse(files['bundle.json']);receipt=parse(files['technical-receipt.json'])
    closed(manifest,('schema_version','bundle_id','schema_binding_sha256','targets','files','coverage',
        'native_decision_cores_materialized','semantic_governance_events_generated','canonical_admission',
        'actual_owner_outcome','runtime_activations','external_effects','authority_effect'))
    need(manifest['schema_version']=='lab-owned-technical-target-byte-bundle/v1-candidate'
         and manifest['authority_effect']=='none' and manifest['canonical_admission'] is False
         and manifest['native_decision_cores_materialized'] is False
         and manifest['semantic_governance_events_generated'] is False
         and manifest['actual_owner_outcome'] is None and manifest['runtime_activations']==0
         and manifest['external_effects']==0,'technical bundle cannot be native admission')
    closed(receipt,('schema_version','bundle_id','whole_bundle_manifest_sha256','target_files','commit_point',
                    'authority_effect','native_admission_receipt','actual_owner_outcome','canonical_admission'))
    need(receipt['schema_version']=='lab-owned-technical-byte-publication-receipt/v1-candidate'
         and receipt['bundle_id']==manifest['bundle_id'] and receipt['whole_bundle_manifest_sha256']==pins['bundle_sha256']
         and receipt['target_files']==manifest['files'] and receipt['authority_effect']=='none'
         and receipt['commit_point']=='atomic-no-replace-owned-bundle-directory'
         and receipt['native_admission_receipt'] is False and receipt['actual_owner_outcome'] is None
         and receipt['canonical_admission'] is False,'complete technical receipt differs')
    need(set(files)==set(manifest['files'])|{'bundle.json','technical-receipt.json'},'byte bundle has foreign/missing file residue')
    need(all(sha(files[path])==digest for path,digest in manifest['files'].items()),'committed selected bytes changed')
    return {'technical_byte_closure_verified':True,'canonical_admission':False,'authority_effect':'none'}
