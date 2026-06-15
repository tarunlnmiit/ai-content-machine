"""Pytest path setup so `import lib.*` resolves the scripts package."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
