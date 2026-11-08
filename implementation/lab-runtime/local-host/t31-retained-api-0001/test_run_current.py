"""One bounded preflight-selection guard test; no synthetic native claim."""
import ast
import copy
from pathlib import Path
import unittest
import run_current as R

class RunnerConfig(unittest.TestCase):
 def test_multistage_preflight_refuses_before_evidence_creation(self):
  stage={'transition_ref':'transition:synthetic:first','input_refs':{},'output_refs':[]}
  config={'schema_version':'lab-actual-retained-workflow-run/v1','kind':'synthetic','selections':[],'typed_productions':[],
          'stages':[stage,copy.deepcopy(stage)],'final_state':'synthetic'}
  with self.assertRaisesRegex(ValueError,'exactly one'):R.validate_config(config,True)
  self.assertIs(R.validate_config(config,False),config)
  config['stages']=config['stages'][:1];self.assertIs(R.validate_config(config,True),config)
  tree=ast.parse(Path(R.__file__).read_bytes());run=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run')
  validation=next(n.lineno for n in ast.walk(run)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='validate_config')
  effects=[n.lineno for n in ast.walk(run)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ('mkdir','replay_source')]
  self.assertLess(validation,min(effects))

if __name__=='__main__':unittest.main()
