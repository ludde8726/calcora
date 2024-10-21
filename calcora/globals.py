from enum import Enum, auto
import os

class PrintOptions(Enum):
  Regular = auto()
  Class = auto()
  Latex = auto()

class Settings:
  DebugLevel = int(os.getenv('DEBUG', 0))
  Printing = PrintOptions.Regular
  Precision = 10