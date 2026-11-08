"""Optional optimization remains disabled. Use the qualified reference profile."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s06'))
import runtime

def ground(normal,optimized=False):
 if optimized:raise runtime.ext.Unsupported('No optimized evaluator is qualified; use the bounded reference')
 return runtime.evaluate(normal)['instances']
if __name__=='__main__':
 print('Optimization is disabled; qualified reference selected. No optimized speedup claimed.')
 sys.exit(4)
