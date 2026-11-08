"""Component tests for using, never minting, the trusted launcher's selection."""
import importlib.util,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H))
spec=importlib.util.spec_from_file_location('_construction_boundary_test',H/'construction_child.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
class Boundary(unittest.TestCase):
 def provider(self,**changes):
  state=types.SimpleNamespace(receipt_pin='a'*64,phase='construct-context',purpose='construct-context')
  for key,value in changes.items():setattr(state,key,value)
  return types.SimpleNamespace(current=lambda:state,root=lambda:C.ROOT,guard=lambda:True)
 def test_missing_bootstrap_refuses(self):
  with patch.dict(sys.modules,{},clear=False):
   sys.modules.pop('cal_installed_runtime_selection_v1',None)
   with self.assertRaises(Exception):C.selected_provider('a'*64)
 def test_exact_construct_selection_is_reused_without_activation(self):
  provider=self.provider()
  with patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':provider}):self.assertIs(C.selected_provider('a'*64),provider)
 def test_wrong_receipt_phase_or_purpose_refuses(self):
  for changes in ({'receipt_pin':'b'*64},{'phase':'ready'},{'purpose':'runtime'}):
   with self.subTest(changes=changes),patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':self.provider(**changes)}):
    with self.assertRaises(Exception):C.selected_provider('a'*64)
 def test_foreign_root_refuses(self):
  provider=self.provider();provider.root=lambda:Path('/different-repository')
  with patch.dict(sys.modules,{'cal_installed_runtime_selection_v1':provider}):
   with self.assertRaises(Exception):C.selected_provider('a'*64)
if __name__=='__main__':unittest.main()
