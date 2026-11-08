#!/usr/bin/env python3
"""Exact Core-owned stage API mirror; no runtime loading. Open Questions: ../../docs/COMMERCE-CONTRACTS.md."""
from pathlib import Path
import argparse,json
CORE=Path(__file__).resolve().parents[2];REPO=CORE.parents[4]
a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');args=a.parse_args()
source=CORE/'src/commerce/commerce-stages-v1.ts';target=REPO/'language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/commerce-stages-v1.ts'
expected='// GENERATED Alch API mirror; canonical owner is Core; interfaces implement no owner.\n'+source.read_text()
if args.write:target.write_text(expected)
else:assert target.read_text()==expected,'Commerce stage mirror drift'
native=CORE/'src/commerce/commerce-native-v1.ts';native_target=target.with_name('commerce-native-v1.ts');native_expected='// GENERATED Alch native API mirror; canonical owner is Core; interfaces implement no native support.\n'+native.read_text()
if args.write:native_target.write_text(native_expected)
else:assert native_target.read_text()==native_expected,'Commerce native API mirror drift'
print(json.dumps({'status':'materialized' if args.write else 'pass-exact','source':str(source),'mirror':str(target),'scope':'data/interface mirror only','open_questions_ref':'../../docs/COMMERCE-CONTRACTS.md'}))
