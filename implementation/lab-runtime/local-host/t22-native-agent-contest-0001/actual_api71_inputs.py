import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def selected_inputs():
 p=Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics/91755e756e7543e6a42e664fafa744b2'
 return (json.loads((HERE/'LIVE-NATIVE-AGENT-COLD-API71-0001.json').read_bytes()),json.loads((HERE/'NATIVE-AGENT-COLD-CALL-API71-0002.json').read_bytes()),(p/'candidate.json').read_bytes(),json.loads((p/'request.json').read_bytes()))
