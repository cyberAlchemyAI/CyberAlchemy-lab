"""Freeze the one exact inert emitted-build AST adaptation."""
import json
from pathlib import Path

import emit_adapter


def main():
    raw, proof = emit_adapter.adapt()
    root = Path(__file__).resolve().parent
    with (root / 'adapted-build-inert.py').open('xb') as stream:
        stream.write(raw)
    with (root / 'emit-ast-proof.json').open('xb') as stream:
        stream.write((json.dumps(proof, sort_keys=True, separators=(',', ':')) + '\n').encode())
    print(json.dumps({'status': 'FROZEN_INERT_EMIT_PROBE', 'adapted_sha256': proof['adapted_sha256'],
                      'full_ast_inverse_equal': proof['full_ast_inverse_equal'],
                      'effect': 'NOT_RUN'}, sort_keys=True))


if __name__ == '__main__':
    main()
