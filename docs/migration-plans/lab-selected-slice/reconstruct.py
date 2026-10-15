"""Fresh read-only inventory reconstruction against independent selected bytes."""
from build_inventory import *
from check_inventory import validate_selection


if __name__=='__main__':
    path=Path(sys.argv[1]);expected=sys.argv[2]
    require(path==TARGET and sha(path.read_bytes())==expected,'independently pinned source selection differs')
    selected=parse(path.read_bytes());validate_selection(selected,True)
    rebuilt=build();validate_selection(rebuilt,True)
    require(rebuilt==selected,'fresh inventory reconstruction differs from exact selected source/ref observations')
    require(sha(path.read_bytes())==expected,'selected source inventory changed during reconstruction')
    print(json.dumps({'result':'PASS','authority_effect':'none','actual_owner_outcome':None,
        'selection_sha256':expected,'items_reconstructed':len(rebuilt['items']),
        'counts':rebuilt['counts'],'dispositions':rebuilt['disposition_counts'],
        'blocked_dependencies':sum(i['disposition']=='block' for i in rebuilt['items']),
        'original_source_schema_checks':len(rebuilt['source_schema_checks']),
        'raw_source_bodies_exported':0,'source_effects_applied':0,'domain_instances_conformed':0,
        'claim_ceiling':'Fresh exact metadata and original source/schema observation parity; no source execution, import/admission or Lab domain conformance.'},sort_keys=True))
