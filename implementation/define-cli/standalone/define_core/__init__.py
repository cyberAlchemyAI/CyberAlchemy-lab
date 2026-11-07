"""Standalone Define public entrypoints. The interpreter and bootstrap are trusted."""
VERSION = "0.3.0rc2"


def call(document):
    from .integrity import verify
    try:
        verify()
    except (ValueError, OSError, KeyError, TypeError):
        return {"api_version": "define.api/v1", "id": None, "operation": None, "outcome": "blocked",
                "diagnostics": [{"code": "runtime-source-drift", "message": "Package consistency refused; values withheld."}],
                "data": None, "authority_effect": "none"}
    try:
        from .api import invoke
        return invoke(document)
    except Exception:
        return {"api_version": "define.api/v1", "id": None, "operation": None, "outcome": "blocked",
                "diagnostics": [{"code": "runtime-import-unavailable", "message": "Package import refused; values withheld."}],
                "data": None, "authority_effect": "none"}


def main():
    from .integrity import verify
    try:
        verify()
    except (ValueError, OSError, KeyError, TypeError):
        import json
        print(json.dumps({"outcome": "blocked", "diagnostics": [{"code": "runtime-source-drift"}], "authority_effect": "none"}))
        return 3
    from .cli import main as cli_main
    return cli_main()


def api_main():
    from .entrypoint import main as transport_main
    return transport_main()
