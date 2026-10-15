from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import C
from v3.p03.qualification import evaluate
try:
    wire=C.decode(sys.stdin.buffer.read());out={'ok':True,'value':evaluate(wire['normal'],wire['policy'])}
except Exception as e:out={'ok':False,'error':str(e).splitlines()[0]}
print(json.dumps(out))
sys.exit(0 if out['ok'] else 2)
