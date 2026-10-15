"""Add versioned, byte-selected resources without replacing original URI meanings."""
import copy
import hashlib
import json
from pathlib import Path
from referencing import Resource

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def require(value,reason):
    if not value:raise ValueError(reason)
def original(binding):
    path=ROOT/binding['path']
    require(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'unsafe protocol resource')
    raw=path.read_bytes();require(hashlib.sha256(raw).hexdigest()==binding['sha256'],'protocol selected bytes changed')
    return raw
def configure(registry,selection_binding):
    require(selection_binding['path']==str((HERE/'selection.json').relative_to(ROOT)),'unselected protocol closure')
    selection=json.loads(original(selection_binding))
    require(selection['schema_version']=='lab-source8-protocol-selection/v1-candidate'
            and selection['exact_added_carriers']==['cal.artifact-type.typed-relation/v4']
            and selection['authority_effect']=='none' and selection['actual_owner_outcome'] is None,'closed candidate eligibility required')
    mapping=selection['uri_mapping'];require(len(mapping)==len(set(mapping.values())),'ambiguous protocol resource IDs')
    for row in selection['resources']:
        original(row['source_binding']);document=json.loads(original(row['selected_binding']))
        require(document['$id']==row['selected_uri']==mapping[row['original_uri']]
                and row['selected_uri']!=row['original_uri'],'original resource identity cannot be overwritten')
        registry=registry.with_resource(document['$id'],Resource.from_contents(document))
    binding=selection['additional_domain_binding'];document=json.loads(original(binding))
    uri='urn:cyberalchemy-lab:bound-schema:'+binding['sha256']
    registry=registry.with_resource(uri,Resource.from_contents(document))
    original(selection['catalog_declaration_binding']);original(selection['source_binding']);original(selection['package_binding'])
    return registry.crawl(),copy.deepcopy(mapping)
