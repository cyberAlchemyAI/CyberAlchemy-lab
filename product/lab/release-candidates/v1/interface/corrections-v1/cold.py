"""Independent original-byte signature replay without a key or warm state."""
from episode import *


def run(directory,expected_binding,pins):
    directory=Path(directory).resolve();require(directory.is_relative_to(EXAMPLES),'selected correction evidence required')
    expected_path=directory/('cold-expected-replay.json' if (directory/'cold-expected-replay.json').exists() else 'expected-replay.json')
    raw=expected_path.read_bytes();require(sha(raw)==expected_binding,'independent expected replay pin differs')
    expected=parse(raw);require(expected['engine_pins']==asdict(pins),'independent expected executable differs')
    archive_path=directory/'branch.snapshot';archive_sha=expected['archive_sha256'] if 'archive_sha256' in expected else None
    require(archive_sha is not None,'independent original archive pin required')
    with tempfile.TemporaryDirectory(prefix='cal-R03-correction-cold-') as temporary:
        owned=Path(temporary);data=restore(archive_path,archive_sha,owned/'store',pins)
        with engine(pins) as handle:
            require(handle.common.digest(data['projection'])==expected['projection_sha256'],'cold projection differs')
            require([handle.common.digest(t) for t in data['transactions']]==expected['transaction_sha256s'],'cold transaction replay differs')
            rows=verify_result(handle,data,data,data['transactions'][-1]['proposal'])
            require(rows==expected['applied_corrections'],'cold exact correction/core/Decision postimages differ')
        require(not any(p.name.endswith('.pem') for p in owned.rglob('*')),'cold replay restored a private key')
    require(not owned.exists(),'cold owned store remains')
    result={'result':'PASS','corrections':len(rows),'projection_parity':True,'signed_transaction_replay':True,
        'original_archive_sha256':archive_sha,'expected_replay_sha256':expected_binding,
        'original_domain_effects_reexecuted':0,'keys_restored':False,'Session_memory_restored':False,
        'owned_store_removed':True,'authority_effect':'none','actual_owner_outcome':None}
    print(json.dumps(result,sort_keys=True));return result


if __name__=='__main__':
    require(len(sys.argv)==4,'usage: cold.py selected-evidence expected-replay-sha256 pins-json')
    run(sys.argv[1],sys.argv[2],EnginePins(**parse(Path(sys.argv[3]).read_bytes())))
