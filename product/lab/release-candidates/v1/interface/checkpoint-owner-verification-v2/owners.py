"""Independent owner selection; signatures do not create ownership or authority.

The API adapter resolves original current records. The pure join is also exposed
for isolated verification, with an explicit synthetic-fact claim ceiling.
This package does not interpret conversation text, admit artifacts, write owner
outcomes, or establish that a provisioned key belongs to a legal person.
"""
import base64
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat

from jsonschema import Draft202012Validator, FormatChecker

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
API=HERE.parent/'api-v59'
API_PIN='186837d9d16fc3369aff32862fb98f42d189b33e314e427798dcb5556449783a'
HEADER={'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'}
KINDS=('principal','role-assignment','authority-claim','authority-boundary','decision-scope')
class OwnerFault(ValueError): pass
def require(value,message):
    if not value: raise OwnerFault(message)
def encoded(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(raw): return hashlib.sha256(raw).hexdigest()
def binding(ref,raw): return {'ref':ref,'sha256':sha(raw)}
def source_guard():
    raw=(HERE/'source-manifest.json').read_bytes();value=parse(raw)
    rows=value['files']+value['input_bindings']
    require(len({r['path'] for r in rows})==len(rows),'duplicate original source binding')
    for row in rows:
        p=ROOT/row['path']
        require(p.is_relative_to(ROOT) and p.resolve()==p and p.is_file()
            and all(not a.is_symlink() for a in p.parents),'unsafe selected source')
        require(sha(p.read_bytes())==row['sha256'],'selected source changed: '+row['path'])
    require(sha(encoded(rows))==value['source_sha256'],'source selection digest differs')
    return value['source_sha256']
def parse(raw):
    require(type(raw) is bytes and 0<len(raw)<=1024*1024,'bounded original bytes required')
    def pairs(items):
        value={}
        for key,item in items:
            require(key not in value,'duplicate JSON key');value[key]=item
        return value
    def bad(_): raise OwnerFault('nonfinite JSON')
    try: return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=bad)
    except (UnicodeError,ValueError,RecursionError) as e: raise OwnerFault('invalid original JSON') from e
def instant(value):
    require(type(value) is str,'explicit timestamp required')
    try:
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        require(result.tzinfo is not None and result.utcoffset() is not None,'timezone required')
        return result.astimezone(timezone.utc)
    except (ValueError,OverflowError) as e: raise OwnerFault('invalid timestamp') from e
def private_original(path,pin):
    """Read the selected private file through anchored, no-follow descriptors."""
    path=Path(path)
    require(path.is_absolute() and path.as_posix()==str(path) and '..' not in path.parts
        and path.is_relative_to('/tmp') and not path.is_relative_to(ROOT),'external private selection required')
    handles=[]
    def ident(s): return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(fd)
        edges=[]
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
            value=os.fstat(child);edges.append((fd,part,(value.st_dev,value.st_ino)));handles.append(child);fd=child
        parent=os.fstat(fd)
        require(parent.st_uid==os.getuid() and stat.S_IMODE(parent.st_mode)==0o700,'private selection directory owner/mode differs')
        original=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=fd);handles.append(original)
        before=os.fstat(original)
        require(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid()
            and stat.S_IMODE(before.st_mode)==0o600 and before.st_nlink==1
            and 0<before.st_size<=1024*1024,'private selection file custody differs')
        chunks=[];size=0
        while True:
            raw=os.read(original,65536)
            if not raw: break
            chunks.append(raw);size+=len(raw);require(size<=1024*1024,'selection byte budget exceeded')
        raw=b''.join(chunks)
        require(ident(before)==ident(os.fstat(original))==ident(os.stat(path.name,dir_fd=fd,follow_symlinks=False))
            and size==before.st_size and sha(raw)==pin,'private selection changed or revoked')
        for parent_fd,name,stamp in reversed(edges):
            value=os.stat(name,dir_fd=parent_fd,follow_symlinks=False)
            require(stat.S_ISDIR(value.st_mode) and (value.st_dev,value.st_ino)==stamp,'selection directory attachment changed')
        return raw
    except OSError as e: raise OwnerFault('private selection unavailable or unsafe') from e
    finally:
        for fd in reversed(handles): os.close(fd)

@dataclass(frozen=True)
class Record:
    header:dict
    original:bytes
    source_state:str

def checked_record(record,kind,scope):
    require(type(record) is Record and type(record.header) is dict and set(record.header)==HEADER,'exact current record required')
    require(record.source_state in ('admitted-current','local-admitted-current'),'historical or unadmitted source refused')
    h=record.header;body=parse(record.original)
    require(h['scope_ref']==scope and h['identity_ref']==body['node_id'] and h['byte_sha256']==sha(record.original)
        and h['carrier_ref']=='cal.artifact-type.'+kind+'/v1','source header/body/carrier differs')
    schema=parse((ROOT/f'authority/artifact-types/{kind}/v1/schema.json').read_bytes())
    try: Draft202012Validator(schema,format_checker=FormatChecker()).validate(body)
    except Exception as e: raise OwnerFault('invalid original '+kind+' contract') from e
    require(body['kind']==kind and body['scope_ref']==scope,'source kind or domain scope differs')
    return body

def verify_join(records,*,principal_ref,role_ref,scope_ref,evaluated_at,permission,targets):
    """Check exact authority joins. Input source eligibility is an adapter duty.

    Permission strings are independently selected exact values; no free-text
    limitations, selected outcomes or period descriptions are interpreted here.
    Unknown period semantics fail closed. Claim limitations remain unresolved
    in the returned join and cannot authorize any live effect.
    """
    source_guard()
    require(type(records) is dict and set(records)==set(KINDS),'complete authority source join required')
    rows={k:checked_record(records[k],k,scope_ref) for k in KINDS}
    p,a,c,b,s=(rows[k] for k in KINDS);clock=instant(evaluated_at)
    require(p['node_id']==principal_ref and p['payload']['status']=='active','Principal not active or substituted')
    require(p['payload']['principal_kind']=='human','this adapter requires a human accountable owner')
    require(a['role_ref']==role_ref and a['assignee_kind']=='person-reference'
        and a['assignee_ref']==p['payload']['stable_subject_ref'],'Role Assignment does not bind this exact Principal subject')
    require(a['assignment_state']=='active' and instant(a['period']['start'])<=clock
        and (a['period']['end'] is None or clock<instant(a['period']['end'])),'Role Assignment inactive or outside its actual period')
    require(c['node_id'] in a['authority_claim_refs'],'Role Assignment does not select this Authority Claim')
    require(c['payload']['claimant_ref']==role_ref and c['payload']['decision_scope_ref']==s['node_id'],'Authority Claim role or Decision Scope differs')
    require(c['payload']['authority_basis_refs'],'claim basis requires an independent admitted semantic adapter')
    require(b['payload']['owner_role_ref']==role_ref and b['payload']['accountable_principal_ref']==principal_ref
        and b['payload']['authority_scope_ref']==s['node_id'],'Authority Boundary owner or scope differs')
    require(b['node_id'] in p['payload']['recognition_boundary_refs'],'Principal recognition boundary does not select this exact boundary')
    require(b['payload']['revocation_state']=='not-revoked'
        and b['payload']['effective_period']=='until-revoked-or-superseded','boundary revoked or period semantics unsupported')
    require(type(permission) is str and permission and permission in c['payload']['claimed_permissions']
        and permission in b['payload']['allowed_effect_kinds'] and permission not in b['payload']['excluded_effect_kinds'],
        'effect excluded or absent from independently selected claim/boundary')
    require(type(targets) is tuple and targets,'exact target selection required')
    seen=set()
    for target in targets:
        require(type(target) is dict and set(target)=={'version_ref','identity_ref','kind','operation'},'closed target selection required')
        require(target['version_ref'] not in seen,'duplicate target grant');seen.add(target['version_ref'])
        require(target['operation'] in s['payload']['permitted_effects'] and target['operation'] not in s['payload']['excluded_effects'],
            'operation outside Decision Scope')
        require(target['kind'] in s['payload']['subject_kind_refs'] and
            (target['version_ref'] in s['payload']['subject_refs'] or target['identity_ref'] in s['payload']['subject_refs']),
            'target identity or kind outside Decision Scope; no wildcard inferred')
    # A current Authority Claim body still needs its original basis Decisions
    # and the source's real authority overlay. This result cannot grant effects.
    source_guard()
    return {'schema_version':'lab-owner-authority-join/v1-candidate','principal_ref':principal_ref,
        'role_ref':role_ref,'scope_ref':scope_ref,'permission':permission,'evaluated_at':evaluated_at,
        'source_bindings':[binding(records[k].header['version_ref'],records[k].original) for k in KINDS],
        'authority_basis_refs':copy.deepcopy(c['payload']['authority_basis_refs']),
        'unresolved_semantic_limitations':copy.deepcopy(c['payload']['limitations']),
        'assignment_basis_ref':a['assignment_basis_ref'],'targets':copy.deepcopy(list(targets)),
        'join_consistent':True,'authority_basis_verified':False,'live_authority_verified':False,
        'canonical_admission_granted':False,'authority_effect':'none'}

class Selection:
    """Host construction input. Never constructed from a public request."""
    def __init__(self,path,pin):
        self.path=Path(path);self.pin=pin;self.initial=self.guard()
    def guard(self):
        source_guard();raw=private_original(self.path,self.pin);value=parse(raw)
        require(set(value)=={'schema_version','source_cut','accountable_principal_ref','scope_ref','not_before',
            'expires_at','revoked','owners','fixture_only','authority_effect'},'closed owner selection required')
        require(value['schema_version']=='lab-independent-checkpoint-owner-selection/v1-candidate'
            and value['revoked'] is False and type(value['fixture_only']) is bool and value['authority_effect']=='none','invalid owner selection posture')
        require(instant(value['not_before'])<=datetime.now(timezone.utc)<instant(value['expires_at']),'owner selection expired or not yet active')
        require(type(value['owners']) is list and 1<=len(value['owners'])<=256,'bounded complete owner selection required')
        require(type(value['accountable_principal_ref']) is str and value['accountable_principal_ref']
            and type(value['scope_ref']) is str and value['scope_ref'],'explicit caller and scope required')
        schema=parse((ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/artifact-package-manifest.schema.json').read_bytes())
        cut_schema={'$schema':schema['$schema'],**schema['properties']['source_cut']}
        try: Draft202012Validator(cut_schema,format_checker=FormatChecker()).validate(value['source_cut'])
        except Exception as e: raise OwnerFault('invalid selected original source cut') from e
        seen=set()
        for owner in value['owners']:
            require(set(owner)=={'principal_ref','role_ref','public_key','records','permission','targets','core_bindings'},'closed selected owner required')
            key=(owner['principal_ref'],owner['role_ref']);require(key not in seen,'ambiguous owner recognition');seen.add(key)
            require(set(owner['records'])==set(KINDS),'complete owner source headers required')
            for h in owner['records'].values():
                require(type(h) is dict and set(h)==HEADER and all(type(v) is str and v for v in h.values()),'closed owner header required')
                require(len(h['byte_sha256'])==64 and all(c in '0123456789abcdef' for c in h['byte_sha256']),'invalid selected original byte hash')
            try: public=base64.b64decode(owner['public_key'],validate=True)
            except Exception as e: raise OwnerFault('invalid selected signer key') from e
            require(len(public)==32 and base64.b64encode(public).decode()==owner['public_key'],'canonical selected Ed25519 key required')
            require(type(owner['core_bindings']) is list and owner['core_bindings'] and
                all(type(b) is dict and set(b)=={'ref','sha256'} for b in owner['core_bindings']), 'exact core grants required')
            for b in owner['core_bindings']:
                require(type(b['ref']) is str and b['ref'] and type(b['sha256']) is str and len(b['sha256'])==64
                    and all(c in '0123456789abcdef' for c in b['sha256']),'invalid exact core grant')
            require(len({(b['ref'],b['sha256']) for b in owner['core_bindings']})==len(owner['core_bindings']),'duplicate exact core grant')
            require(type(owner['permission']) is str and owner['permission'] and type(owner['targets']) is list and owner['targets'], 'exact effect and target selection required')
        source_guard();return copy.deepcopy(value)

class API59Sources:
    """Original authenticated API59 source resolver; no synthetic duck typing."""
    def __init__(self,host,selection):
        require(type(selection) is Selection,'independent selection object required')
        # Reuse the actual host package to preserve exact Service type identity.
        require(type(host).__name__=='Service','actual frozen Service required')
        service=importlib.import_module(type(host).__module__)
        require(type(host) is service.Service and Path(service.__file__).resolve()==API/'service.py','unselected API host refused')
        package=service.__package__;self.G=importlib.import_module(package+'.guard')
        self.H=importlib.import_module(package+'.handlers');self.M=importlib.import_module(package+'.artifact_model')
        self.W=importlib.import_module(package+'.workspace');self.A=importlib.import_module(package+'.auth')
        require(type(host.channel) is self.A.ReaderChannel and type(host.vault) is self.W.Vault,'owner source requires actual operator reader and workspace')
        self.host=host;self.selection=selection;self.guard()
    def guard(self):
        self.G.verify(API_PIN);self.host.schemas.guard();selected=self.selection.guard();context=self.host.channel.guard()
        self.host.vault.guard();require(self.host.handlers.current(),'owner source cut is stale')
        require(self.H.cut(self.host.handlers.view)==selected['source_cut'],'owner selection cut differs from current signed source')
        require(context['principal_ref']==selected['accountable_principal_ref']
            and context['scope_refs']==[selected['scope_ref']] and context['agent_instance_ref'] is None,
            'authenticated caller is not the independently selected accountable operator')
        return selected
    def resolve(self,header,kind):
        selected=self.guard();view=self.host.handlers.view;self.host.handlers.selected_view=view
        subject=self.host.handlers.resolve_exact(header)
        require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'owner source not current')
        require(view.data['projection']['contracts'][self.M.carrier(view,subject)]['semantic_kind']==kind,'source semantic carrier differs')
        raw=self.M.record_bytes(view,subject)[0]
        body=parse(raw);view.handle.operations.validate_record(body,header['carrier_ref'],view.data['projection']);self.W.privacy(body)
        result=Record(copy.deepcopy(header),raw,subject['effective_state'])
        checked_record(result,kind,selected['scope_ref']);self.guard();return result
    def joins(self):
        selected=self.guard();clock=datetime.now(timezone.utc).isoformat();results=[]
        for owner in selected['owners']:
            records={kind:self.resolve(owner['records'][kind],kind) for kind in KINDS}
            result=verify_join(records,principal_ref=owner['principal_ref'],role_ref=owner['role_ref'],
                scope_ref=selected['scope_ref'],evaluated_at=clock,permission=owner['permission'],targets=tuple(owner['targets']))
            result['independent_selection_binding']=binding('checkpoint-owner-selection:'+self.selection.pin,private_original(self.selection.path,self.selection.pin))
            result['source_cut']=copy.deepcopy(selected['source_cut']);result['fixture_only']=selected['fixture_only'];results.append(result)
        self.guard();return results
