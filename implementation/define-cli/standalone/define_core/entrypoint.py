"""Console entrypoint: one bounded request on stdin, one JSON result on stdout."""
import json
import sys


def main():
    from .integrity import verify, IntegrityError
    try:
        verify()
        from .api import MAX_FRAME, invoke
        from .exact import decode, encode
        raw = sys.stdin.buffer.read(MAX_FRAME + 1)
        document = decode(raw, maximum=MAX_FRAME)
        result = invoke(document)
        sys.stdout.buffer.write(encode(result))
        return {"invalid-input": 2, "blocked": 3, "unsupported": 4}.get(result["outcome"], 0)
    except IntegrityError as exc:
        outcome, code, status = "blocked", exc.code, 3
    except KeyboardInterrupt:
        outcome, code, status = "interrupted", "interrupted", 130
    except Exception:
        # Bootstrap/transport failures cannot expose arbitrary source or paths.
        outcome, code, status = "invalid-input", "invalid-transport-or-runtime", 2
    print(json.dumps({"api_version": "define.api/v1", "id": None, "operation": None, "outcome": outcome,
                      "diagnostics": [{"code": code, "message": "Input or package integrity refused; values withheld."}],
                      "data": None, "authority_effect": "none"}))
    return status
