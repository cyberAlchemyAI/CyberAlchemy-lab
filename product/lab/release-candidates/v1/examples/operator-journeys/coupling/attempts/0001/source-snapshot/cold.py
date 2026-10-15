"""Fresh process original signed transaction replay; no fixture reexecution."""
from episode import *


if __name__=='__main__':
    if len(sys.argv)!=4:
        raise SystemExit('usage: cold.py selected-episode-path expected-replay-sha256 pins-json')
    directory=Path(sys.argv[1]);expected_path=directory/'expected-replay.json'
    require(sha(expected_path.read_bytes())==sys.argv[2],'independent expected result pin differs')
    expected=parse(expected_path.read_bytes());pins=EnginePins(**parse(Path(sys.argv[3]).read_bytes()))
    require(expected['engine_pins']==asdict(pins),'independent replay engine pins differ')
    with tempfile.TemporaryDirectory(prefix='cal-R03-cold-signed-') as temp:
        data=restore_archive(directory/'branch.snapshot',expected['source_binding']['sha256'],Path(temp)/'store',pins)
        with engine(pins) as handle:
            require(handle.common.digest(data['projection'])==expected['projection_sha256']
                and [handle.common.digest(tx) for tx in data['transactions']]==expected['transaction_sha256s'],
                'cold exact source/postimage/consequence replay differs')
            relation=data['projection']['subjects'][expected['relation_ref']]
            handle.operations.validate_relation(relation['record'],data['projection'])
            for row in expected['actual_targets']:
                actual=data['projection']['subjects'][row['version_ref']]
                require(actual['kind']==row['carrier_kind'] and actual['source']==row['source_binding']
                    and handle.common.digest(actual['record'])==row['record_structural_sha256'],
                    'cold raw carrier tuple or original signed source differs')
    print(json.dumps({'result':'PASS','authority_effect':'none','actual_owner_outcome':None,
        'signed_transaction_replay':True,'projection_parity':True,'raw_carrier_kinds_preserved':True,
        'original_domain_effects_reexecuted':0,'keys_restored':False,'Session_memory_restored':False},sort_keys=True))
