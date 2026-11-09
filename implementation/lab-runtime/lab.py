#!/usr/bin/env python3
"""Current workspace runtime; native Project protocol remains an explicit versioned route."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=="workspace":
    sys.path.insert(0,str(HERE.parent/"lab-workspaces/v2"))
    from workspaces import main
    raise SystemExit(main(sys.argv[2:]))
if "--native-project-protocol" in sys.argv[1:]:
    args=sys.argv[1:];args.remove("--native-project-protocol")
    sys.path.insert(0,str(HERE/"v2"))
    from lab_runtime.cli import main
    raise SystemExit(main(args))
if len(sys.argv)==1 or sys.argv[1] in {"--help","-h"}:
    print("Usage: lab.py workspace {list,inspect,resolve,verify,dispatch} ...")
    print("Use --native-project-protocol only for the explicit low-level native v2 protocol.")
    raise SystemExit(0)
print(json.dumps({"result":"REFUSED","reason":"workspace-context-required",
                  "authority_effect":"none"}),file=sys.stderr)
raise SystemExit(2)
