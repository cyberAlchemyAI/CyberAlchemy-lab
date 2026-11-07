import importlib.metadata as m,json,platform,sys
from pathlib import Path
info={'python':sys.version,'executable':sys.executable,'prefix':sys.prefix,'platform':platform.platform(),'machine':platform.machine(),
      'dependencies':[{'name':name,'version':m.version(name),'license':m.metadata(name).get('License-Expression') or m.metadata(name).get('License')}
        for name in ['cyberalchemy-define','jsonschema','attrs','jsonschema-specifications','referencing','rpds-py']]+([
        {'name':'typing_extensions','version':m.version('typing_extensions'),'license':m.metadata('typing_extensions').get('License-Expression') or m.metadata('typing_extensions').get('License')}]
        if sys.version_info<(3,13) else [])}
print(json.dumps(info,indent=2))
