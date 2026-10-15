"""Read declared carrier identity without altering its original body.

The header's repository scope and immutable revision are host-selected witnesses.
They are not a Product's domain scope or its inline model-version field.
"""
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
FIELDS={'scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'}


class IdentityRefusal(ValueError):
    pass


def require(value, reason):
    if not value:raise IdentityRefusal(reason)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def parse(raw):
    require(type(raw) is bytes,'original carrier bytes required')
    def unique(pairs):
        value={}
        for key,item in pairs:
            require(key not in value,'duplicate JSON member in original carrier')
            value[key]=item
        return value
    def invalid(token):raise IdentityRefusal('nonfinite JSON token in original carrier')
    def finite(token):
        value=float(token);require(math.isfinite(value),'nonfinite JSON number in original carrier')
        return value
    try:value=json.loads(raw,object_pairs_hook=unique,parse_constant=invalid,parse_float=finite)
    except (UnicodeDecodeError,json.JSONDecodeError) as error:raise IdentityRefusal('invalid original carrier JSON') from error
    require(type(value) is dict,'original carrier object required')
    return value


def selected_file(binding):
    require(type(binding) is dict and set(binding)=={'path','sha256'},'closed carrier source binding required')
    relative=Path(binding['path'])
    require(not relative.is_absolute() and '..' not in relative.parts
            and relative.as_posix()==binding['path'],'canonical repository carrier path required')
    path=ROOT/binding['path']
    require(path.is_relative_to(ROOT) and not path.is_symlink()
            and not any(p.is_symlink() for p in path.parents),'foreign or symbolic carrier source refused')
    raw=path.read_bytes();require(sha(raw)==binding['sha256'],'declared carrier source bytes changed')
    return path,raw


@dataclass(frozen=True)
class TypedRecord:
    version_ref: str
    raw: bytes
    byte_sha256: str
    header: dict

    def selected(self):
        require(type(self.header) is dict and set(self.header)==FIELDS,'closed five-axis carrier header required')
        require(all(type(value) is str and bool(value) for value in self.header.values()),'carrier header strings required')
        require(self.header['version_ref']==self.version_ref
                and self.header['byte_sha256']==self.byte_sha256==sha(self.raw),
                'carrier header, revision or original bytes differ')
        manifest=parse((HERE/'source-manifest.json').read_bytes())
        table=parse((HERE/'carrier-contracts.json').read_bytes())
        table_binding={'path':str((HERE/'carrier-contracts.json').relative_to(ROOT)),
                       'sha256':sha((HERE/'carrier-contracts.json').read_bytes())}
        require(table_binding in manifest['files'],'carrier table is outside frozen rule inputs')
        carrier=self.header['carrier_ref']
        require(carrier in table['contracts'],'carrier has no explicitly selected identity contract')
        contract=table['contracts'][carrier]
        require(contract['artifact_binding'] in manifest['files'] and contract['schema_binding'] in manifest['files'],
                'carrier contract/schema outside selected rule source')
        _,artifact_raw=selected_file(contract['artifact_binding']);artifact=parse(artifact_raw)
        field=artifact['instance_contract']['identity_field']
        require(field==contract['identity_field']
                and artifact['classification']['semantic_kind']==contract['semantic_kind'],
                'carrier identity or semantic kind differs from original contract')
        require(artifact['schema_digest']==contract['schema_binding']['sha256'],
                'carrier schema selection differs from original descriptor')
        schema_path,schema_raw=selected_file(contract['schema_binding'])
        schemas=[]
        for row in table['schemas']:
            require(row in manifest['files'],'registry schema outside selected inputs')
            path,raw=selected_file(row);schema=parse(raw)
            schemas.append((schema.get('$id',path.as_uri()),schema))
            if schema.get('$id')!=path.as_uri():schemas.append((path.as_uri(),schema))
        registry=Registry().with_resources((identifier,Resource.from_contents(schema,default_specification=DRAFT202012))
                                          for identifier,schema in schemas)
        body=parse(self.raw);schema=parse(schema_raw)
        try:
            valid=Draft202012Validator(schema,registry=registry,format_checker=FormatChecker()).is_valid(body)
        except Exception as error:
            raise IdentityRefusal('selected carrier schema/reference closure unavailable') from error
        require(valid,'original carrier schema refused record')
        require(type(body.get(field)) is str and bool(body[field]),'declared carrier identity field absent')
        identity=body[field]
        if contract['semantic_kind']=='artifact-type' and field=='artifact_type_ref':
            require(identity==self.version_ref and '/' in identity,'artifact type revision differs')
            identity=identity.rsplit('/',1)[0]
        else:
            require(self.version_ref.startswith(identity+'@') and len(self.version_ref)>len(identity)+1,
                    'carrier revision does not qualify its declared identity')
        require(identity==self.header['identity_ref'],'declared carrier identity differs from exact header')
        if 'scope_ref' in body:
            require(body['scope_ref']==self.header['scope_ref'],'carrier authority scope differs')
        # Domain scope and inline version stay untouched. Header provenance and
        # complete current-cut selection must be established by the actual host.
        return body,identity,contract['semantic_kind']

    def body(self):return self.selected()[0]
    def identity(self):return self.selected()[1]
    def semantic_kind(self):return self.selected()[2]
    def selection_scope(self):
        self.selected()
        return self.header['scope_ref']
