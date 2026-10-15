"""Candidate represented-subject views. Never modifies raw Project State.

The exact C14 proposals select Project/Product endpoint kinds. A Method has a
separately bound candidate carrier. Compatibility with the frozen relation
validator does not establish transaction support or ontology-event admission.
"""
from contextlib import contextmanager
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile

from jsonschema import Draft202012Validator

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[3]
MAPPING = ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json'
MAPPING_SHA = 'c0f69674bd37802c669a29fff208232549a3bcfdd28673fc1999c074ad82396a'
ARCHIVE = ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot'
ARCHIVE_SHA = '03850c8aa4cf7a994f3ce66c25cb68d4567c170ed38e40dc24e115a3e900f944'
_CATALOG_FACTORY = object()


class RepresentationFault(ValueError):
    pass


def require(value, message):
    if not value:
        raise RepresentationFault(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(RepresentationFault('nonfinite JSON')))


def object_sha(value):
    return sha(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())


class VerifiedCatalog:
    """In-process handle produced by original-byte replay, never a caller flag."""
    def __init__(self, data, operations, factory):
        require(factory is _CATALOG_FACTORY, 'catalog must come from independently pinned replay')
        self.projection = copy.deepcopy(data['projection'])
        self.projection_sha256 = object_sha(self.projection)
        self.operations = operations
        self.validate_relation = operations.validate_relation
        self.closed = False

    def verify(self, operations):
        require(not self.closed and operations is self.operations
            and operations.validate_relation is self.validate_relation, 'closed or altered replay handle')
        require(object_sha(self.projection)==self.projection_sha256, 'replayed catalog was altered')
        require(sha(ARCHIVE.read_bytes())==ARCHIVE_SHA, 'original signed archive changed')


def bind(path):
    path = Path(path)
    return {'path':path.relative_to(ROOT).as_posix(), 'sha256':sha(path.read_bytes())}


def original(binding):
    require(type(binding) is dict and set(binding)=={'path','sha256'}, 'closed byte binding required')
    path = ROOT/binding['path']
    require(not Path(binding['path']).is_absolute() and path.resolve().is_relative_to(ROOT)
        and path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'unsafe selected path')
    raw = path.read_bytes()
    require(sha(raw)==binding['sha256'], 'original selected bytes changed')
    return raw


def pointer(value, selector):
    require(selector.startswith('/') and selector!='/', 'exact identity selector required')
    for part in selector[1:].split('/'):
        part = part.replace('~1','/').replace('~0','~')
        require(type(value) is dict and part in value, 'selector unresolved')
        value = value[part]
    return value


def identity(record):
    for field in ['node_id','method_id','goal_id','coordination_context_id','project_id','product_id']:
        if field in record:
            return record[field]
    raise RepresentationFault('no exact identity selector in this adapter scope')


@contextmanager
def signed_catalog():
    """Independent original-byte replay in a disposable directory; no writes back."""
    sys.path.insert(0,str(ROOT/'implementation/lab-continuity/candidates/v1'))
    import continuity
    from lab_runtime.replay import ReplayPins, legacy_runtime
    require(sha(ARCHIVE.read_bytes())==ARCHIVE_SHA, 'independent archive pin differs')
    with tempfile.TemporaryDirectory(prefix='cal-O02-catalog-') as temp:
        data = continuity.restore_archive(ARCHIVE,ARCHIVE_SHA,Path(temp)/'archive')
        name,_,stage = legacy_runtime(ROOT,ReplayPins(**parse(ARCHIVE.read_bytes())['project_pins']))
        handle = None
        try:
            operations = importlib.import_module(name+'.operations')
            handle = VerifiedCatalog(data,operations,_CATALOG_FACTORY)
            yield handle,operations
        finally:
            if handle:
                handle.closed = True
            stage.cleanup()
            for key in list(sys.modules):
                if key==name or key.startswith(name+'.'):
                    sys.modules.pop(key,None)


class CandidateRepresentationAdapter:
    """Pure candidate cut consumer, restricted to the exact proposed mapping."""
    def __init__(self, catalog, operations, mapping_binding=None):
        require(type(catalog) is VerifiedCatalog, 'caller catalog metadata is not replay evidence')
        catalog.verify(operations)
        selected = mapping_binding or {'path':MAPPING.relative_to(ROOT).as_posix(),'sha256':MAPPING_SHA}
        require(selected=={'path':MAPPING.relative_to(ROOT).as_posix(),'sha256':MAPPING_SHA}, 'unselected mapping proposal')
        self.mapping_binding = copy.deepcopy(selected)
        self.mapping = parse(original(selected))
        self.handle = catalog
        self.catalog = copy.deepcopy(catalog.projection)
        self.catalog_sha256 = object_sha(self.catalog)
        self.operations = operations
        self.proposals = {p['carrier_ref']:p for p in self.mapping['endpoint_proposals']}
        require(len(self.proposals)==3, 'closed C14 proposal set differs')
        self.carriers = {c['carrier_ref']:c for c in self.mapping['carriers']}

    def guard(self):
        self.handle.verify(self.operations)
        require(object_sha(self.catalog)==self.catalog_sha256, 'adapter catalog was altered')
        require(sha(original(self.mapping_binding))==MAPPING_SHA, 'selected mapping changed')
        require(self.mapping==parse(original(self.mapping_binding)), 'mapping proposal was altered')
        require(self.proposals=={p['carrier_ref']:p for p in self.mapping['endpoint_proposals']}
            and self.carriers=={c['carrier_ref']:c for c in self.mapping['carriers']}, 'selected mapping indexes were altered')

    def contract_for(self, record, carrier_kind):
        current = [(ref,c) for ref,c in self.catalog['contracts'].items()
            if c['semantic_kind']==carrier_kind and c['lifecycle_state'] in ('admitted-current','local-admitted-current')]
        if carrier_kind=='method':
            require(not current, 'candidate Method path cannot override a current signed carrier')
            proposal = self.proposals['cal.artifact-type.method/v1']
            schema_binding = {k:proposal['schema_binding'][k] for k in ['path','sha256']}
            return proposal['carrier_ref'],schema_binding,proposal['identity_selector'],'candidate-unadmitted'
        require(len(current)==1, 'signed current carrier ambiguous or absent')
        ref,c = current[0]
        require(c.get('schema_selector') is None, 'schema selector outside this adapter scope')
        declared = self.carriers.get(ref)
        require(declared is not None and declared['semantic_kind']==carrier_kind, 'carrier mapping not selected')
        require(c['schema_sha256']==declared['schema_sha256'] and c['schema_path']==declared['schema_path'], 'signed carrier/schema join differs')
        discriminator = c['instance_discriminator']
        require(pointer(record,discriminator['path'])==discriminator['value'], 'carrier discriminator mismatch')
        return ref,{'path':c['schema_path'],'sha256':c['schema_sha256']},declared['identity_selector'],c['lifecycle_state']

    def represent(self, row):
        self.guard()
        return self._represent(row)

    def _represent(self, row):
        require(type(row) is dict and set(row)=={'path','sha256','kind','version_ref'}, 'closed selected carrier row required')
        source = {'path':row['path'],'sha256':row['sha256']}
        record = parse(original(source))
        carrier_ref,schema_binding,selector,contract_posture = self.contract_for(record,row['kind'])
        schema = parse(original(schema_binding))
        require(not list(Draft202012Validator(schema).iter_errors(record)), 'carrier schema invalid')
        ident = pointer(record,selector)
        require(ident==identity(record) and row['version_ref'].startswith(ident+'@')
            and len(row['version_ref'])>len(ident)+1, 'exact carrier identity/revision differs')
        if 'version' in record:
            require(row['version_ref']==ident+'@'+record['version'], 'literal carrier version differs')
        proposal = self.proposals.get(carrier_ref)
        kind = row['kind']
        mapping = None
        if proposal:
            require(proposal['identity_selector']==selector, 'represented identity selector differs')
            selected_schema = {k:proposal['schema_binding'][k] for k in ['path','sha256']}
            require(selected_schema==schema_binding, 'represented schema mapping differs')
            kind = proposal['endpoint_kind']
            mapping = copy.deepcopy(proposal)
        committed = self.catalog['subjects'].get(row['version_ref'])
        posture = 'candidate-unadmitted'
        signed_source = None
        if committed:
            require(committed['record']==record and committed['kind']==row['kind']
                and committed['identity']==ident, 'prospective cut cannot overwrite committed subject')
            require(committed['effective_state'] in ('admitted-current','local-admitted-current'), 'historical or withdrawn source instance')
            require(committed['source']['sha256']==row['sha256'], 'signed input original byte digest differs')
            posture = committed['effective_state']
            signed_source = copy.deepcopy(committed['source'])
        return {'schema_version':'lab-represented-subject-view/v1-candidate','authority_effect':'none',
            'carrier':{'kind':row['kind'],'ref':carrier_ref,'contract_posture':contract_posture,
                'schema_binding':schema_binding,'identity_selector':selector,'source_binding':source},
            'represented_subject':{'kind':kind,'identity':ident,'version_ref':row['version_ref'],'carrier_bytes_sha256':row['sha256']},
            'mapping_binding':copy.deepcopy(self.mapping_binding),'mapping_proposal':mapping,
            'source_admission':posture,'signed_catalog_subject_binding':signed_source,'confirmed_global_edge_eligible':False,
            'ontology_event_authority':False,'signed_transaction_mapping_implemented':False,
            'record':copy.deepcopy(record)}

    def candidate_cut(self, cut):
        self.guard()
        require(type(cut) is dict and set(cut)=={'cut_id','authority_effect','actual_owner_outcome','records'}, 'closed candidate cut required')
        require(type(cut['cut_id']) is str and cut['cut_id'] and cut['authority_effect']=='none'
            and cut['actual_owner_outcome'] is None, 'candidate cut cannot supply admission authority')
        require(type(cut['records']) is list and cut['records'], 'empty candidate source cut')
        views = {}
        for row in cut['records']:
            view = self._represent(row);ref = view['represented_subject']['version_ref']
            require(ref not in views, 'duplicate exact revision within selected cut')
            views[ref] = view
        return {'cut_id':cut['cut_id'],'authority_effect':'none','actual_owner_outcome':None,'views':views,
            'source_archive_binding':bind(ARCHIVE),'mapping_binding':copy.deepcopy(self.mapping_binding),
            'global_merge_allowed':False,'confirmed_global_edge_eligible':False}

    def validate_candidate_relations(self, cut_view):
        self.guard()
        require(cut_view['authority_effect']=='none' and cut_view['actual_owner_outcome'] is None
            and cut_view['source_archive_binding']==bind(ARCHIVE)
            and cut_view['mapping_binding']==self.mapping_binding, 'cut source/mapping binding differs')
        # Re-resolve original carrier bytes. The caller cannot change a view kind,
        # posture or mapping flag to bypass the selected mapping.
        for ref,view in cut_view['views'].items():
            source = view['carrier']['source_binding']
            checked = self._represent({**source,'kind':view['carrier']['kind'],'version_ref':ref})
            require(checked==view, 'represented view was altered')
        projection = copy.deepcopy(self.catalog)
        for ref,view in cut_view['views'].items():
            subject = view['represented_subject']
            if ref in projection['subjects']:
                # Exact unchanged signed input retains its original posture.
                # It is not replaced by a prospective record or a kind alias.
                require(subject['kind']==projection['subjects'][ref]['kind'], 'signed kind mapping needs transaction integration')
                continue
            projection['subjects'][ref]={'identity':subject['identity'],'version_ref':ref,
                'kind':subject['kind'],'effective_state':'candidate-unadmitted','record':view['record']}
        checked = []
        for ref,view in cut_view['views'].items():
            if view['carrier']['kind']!='typed-relation':
                continue
            record = view['record']
            require(all(e['version_ref'] in cut_view['views'] for e in [record['payload']['source'],record['payload']['target']]), 'candidate endpoints must resolve inside this exact cut')
            self.operations.validate_relation(record,projection)
            checked.append({'relation_ref':ref,'result':'PASS','cut_id':cut_view['cut_id'],
                'source_binding':view['carrier']['source_binding'],'confirmed_global_edge_eligible':False,
                'transactions_applied':0,'actual_owner_outcome':None})
        return checked
