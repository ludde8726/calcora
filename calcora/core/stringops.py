from calcora.globals import BaseOps
from calcora.utils import dprint

dprint("Warning! When importing stringops all previously imported ops are overridden please use with caution!", 1, "bright_yellow")

for op in BaseOps: 
  if op != BaseOps.NoOp: globals()[op.name] = op.value