"""The exact signed local contract declaration is catalog metadata, not an instance."""
import copy
from pathlib import Path
from .protocol import source,ROOT,binding

HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent/'source8-protocol-v1'
def selection(view,subject):
    if subject['category']!='artifact-type' or subject['version_ref']!='cal.artifact-type.typed-relation/v4':return None
    from .integrated_guard import is_view,guard_view
    source.require(is_view(view),'local declaration requires independently selected Source8')
    guard_view(view)
    path=PACKAGE/'catalog-declaration.json';record=source.parse(path.read_bytes())
    source.require(record['schema_version']=='lab-source8-signed-catalog-declaration/v1-candidate'
        and record['authority_effect']=='none' and record['actual_owner_outcome'] is None,'closed signed declaration selection required')
    source.require(view.selected['archive_binding']==record['source_snapshot_binding']
        and view.data['config']['store_id']==record['source_cut']['store_ref']
        and view.data['config']['scope_ref']==record['scope_ref'],
        'declaration outside selected signed source')
    source.require(subject['record']==record['body'],'current declaration body differs')
    contract=view.data['projection']['contracts'][subject['version_ref']]
    source.require({'ref':contract['schema_path'],'sha256':contract['schema_sha256']}==record['instance_schema_binding'],
        'signed declaration instance schema differs')
    return record
def raw(view,subject,record):
    model=source.integrated_reader().adapter.model
    original,locator,encoding,file_sha=model.record_bytes(view,subject)
    selected=record['declaration_binding'];path=ROOT/selected['path']
    source.require(source.sha(original)==selected['sha256'] and path.read_bytes()==original,
        'original signed declaration bytes differ from independently selected representation')
    source.require(source.parse(original)==record['body'] and file_sha==record['transaction_binding']['sha256'],
        'signed original declaration parse/transaction differs')
    return original,locator,encoding,file_sha
def header(view,subject,record):
    original,_,_,_=raw(view,subject,record)
    return {'scope_ref':view.data['config']['scope_ref'],'identity_ref':record['identity_ref'],
        'version_ref':record['represented_contract_ref'],'carrier_ref':record['meta_carrier_ref'],'byte_sha256':source.sha(original)}
def envelope(view,subject,cut,basis,record):
    original,locator,encoding,file_sha=raw(view,subject,record)
    selection_path=PACKAGE/'catalog-declaration.json'
    return {'schema_version':'lab-catalog-representation-envelope/v1-candidate','artifact':header(view,subject,record),
        'source_cut':cut,'represented_contract_ref':record['represented_contract_ref'],
        'representation_kind':'signed-local-contract-declaration','body':copy.deepcopy(record['body']),
        'content':{'content_ref':locator,'byte_sha256':source.sha(original),'size_bytes':len(original),'media_type':'application/json'},
        'source_locator':locator,'enclosing_source_binding':{'ref':record['transaction_binding']['ref'],'sha256':file_sha},
        'representation_profile_binding':binding(str(selection_path.relative_to(ROOT)),selection_path.read_bytes()),
        'effective_admission_basis':basis,'claim_ceiling':source.CLAIM+' Exact signed local contract declaration; no domain instance or canonical admission inferred.',
        'authority_effect':'none'}
