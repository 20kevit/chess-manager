import os
import sys

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)

from run import app as application