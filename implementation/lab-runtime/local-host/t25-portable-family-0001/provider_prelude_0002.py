"""Insert the required provider guard after the docstring and future imports."""
import ast
PRELUDE='import cal_installed_runtime_selection_v1 as _INSTALL_SELECTION\n_INSTALL_SELECTION.guard()\n'
def inject(text):
 if 'import cal_installed_runtime_selection_v1' in text:raise ValueError('provider prelude already present')
 tree=ast.parse(text);at=0;index=0
 if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):
  at=tree.body[0].end_lineno;index=1
 for node in tree.body[index:]:
  if isinstance(node,ast.ImportFrom) and node.module=='__future__':at=node.end_lineno
  else:break
 lines=text.splitlines(keepends=True);lines[at:at]=[PRELUDE];result=''.join(lines)
 compile(result,'<portable-provider-prelude>','exec',dont_inherit=True)
 return result
