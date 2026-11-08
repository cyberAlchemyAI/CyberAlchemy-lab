"""Startup qualification is actual-period bounded without changing grant reads."""
import ast
from datetime import datetime,timedelta,timezone
from pathlib import Path
from types import SimpleNamespace
import unittest
SOURCE=Path(__file__).resolve().with_name('qualify_installed_api.py')
tree=ast.parse(SOURCE.read_bytes());guard=next(n for n in tree.body if isinstance(n,ast.If) and isinstance(n.test,ast.UnaryOp) and 'observed_at' in ast.unparse(n.test))
def utc(text):return datetime.fromisoformat(text)
class CurrentPeriod(unittest.TestCase):
 def execute(self,period,at):
  exec(compile(ast.Module(body=[guard],type_ignores=[]),str(SOURCE),'exec'),{'grant':SimpleNamespace(utc=utc),'period':period,'observed_at':at})
 def test_actual_current_period_accepts(self):
  now=datetime.now(timezone.utc);self.execute({'not_before':(now-timedelta(seconds=1)).isoformat(),'expires_at':(now+timedelta(seconds=1)).isoformat()},now)
 def test_expired_and_expiry_boundary_refuse(self):
  now=datetime.now(timezone.utc)
  for end in (now-timedelta(seconds=1),now):
   with self.assertRaisesRegex(ValueError,'Source period is not current'):self.execute({'not_before':(now-timedelta(minutes=1)).isoformat(),'expires_at':end.isoformat()},now)
 def test_future_period_refuses(self):
  now=datetime.now(timezone.utc)
  with self.assertRaisesRegex(ValueError,'Source period is not current'):self.execute({'not_before':(now+timedelta(seconds=1)).isoformat(),'expires_at':(now+timedelta(minutes=1)).isoformat()},now)
if __name__=='__main__':unittest.main()
