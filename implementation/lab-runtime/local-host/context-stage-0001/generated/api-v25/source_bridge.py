"""Construction-only Context API.Schemas bridge to the loaded same-family Reader."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
NAME='_cal_legacy_context_dev_20261020_0003_legacy_fixture_context_mapper_0257.build'
mapper=sys.modules.get(NAME)
if mapper is None: raise RuntimeError('selected Mapper must load before Context API')
if mapper.HERE != HERE.parent/'docker-mapped-20261020-0001': raise RuntimeError('Mapper sibling differs')
if mapper.reader.HERE != HERE.parent/'docker-source-20261020-0001': raise RuntimeError('Source sibling differs')
if mapper.reader.adapter.HERE != HERE.parent/'docker-reader-20261020-0001': raise RuntimeError('Reader sibling differs')
source=mapper.reader.adapter.source
ROOT=source.ROOT
if ROOT != HERE.parents[5]: raise RuntimeError('family root differs')
sha=source.sha
parse=source.parse
original=source.original
require=source.require
