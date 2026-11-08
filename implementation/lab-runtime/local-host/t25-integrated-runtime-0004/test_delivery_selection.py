"""Causal selector tests; existing reader-origin guards are delegated unchanged."""
import ast,types,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
POST=HERE/'api75-delivery-selection-postimages-0001'
def require(value,reason):
 if not value:raise ValueError(reason)
def selected_function(name,scope):
 tree=ast.parse((POST/'source_bridge.py').read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[node],type_ignores=[]),str(POST/'source_bridge.py'),'exec'),scope);return scope[name]
class DeliverySelection(unittest.TestCase):
 def setUp(self):
  self.reader=object();self.producer=types.SimpleNamespace(reader=self.reader);self.old=object();self.calls=[]
  def factory(view):self.calls.append(('factory',view));return lambda:self.reader
  self.scope={'require':require,'legacy_session_view':lambda view:True,'source8_session_view':lambda view:True,'reader_factory':factory,'custody_delivery':lambda:self.old};self.select=selected_function('delivery_for_view',self.scope)
 def test_actual_selected_legacy_delegates_origin_guard_and_factory(self):
  view=types.SimpleNamespace(legacy_context_producer=self.producer);self.assertIs(self.select(view),self.producer);self.assertEqual(self.calls,[('factory',view)])
 def test_failed_legacy_origin_never_falls_back(self):
  self.scope['legacy_session_view']=lambda view:False
  with self.assertRaisesRegex(ValueError,'actual selected legacy'):self.select(types.SimpleNamespace(legacy_context_producer=self.producer))
  self.assertEqual(self.calls,[])
 def test_replaced_reader_factory_refuses(self):
  self.scope['reader_factory']=lambda view:lambda:object()
  with self.assertRaisesRegex(ValueError,'reader changed'):self.select(types.SimpleNamespace(legacy_context_producer=self.producer))
 def test_source8_origin_and_exact_factory_required(self):
  view=types.SimpleNamespace(source8_context_producer=self.producer);self.assertIs(self.select(view),self.producer);self.scope['source8_session_view']=lambda view:False
  with self.assertRaisesRegex(ValueError,'actual selected Source8'):self.select(view)
 def test_original_custody_fallback_retained(self):self.assertIs(self.select(types.SimpleNamespace()),self.old)
if __name__=='__main__':unittest.main()
