from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.core.registry import Dispatcher

if TYPE_CHECKING:
  from calcora.core.expression import Expr

def callback_dispatcher(expression: Expr) -> Expr:
  # TODO: This function will handle calling the correct callbacks
  return expression

setattr(Dispatcher, '_callback_fxn', callback_dispatcher)