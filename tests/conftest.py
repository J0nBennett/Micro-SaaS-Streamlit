import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SAAS_DIR = REPO_ROOT / "saas"

if str(SAAS_DIR) not in sys.path:
    sys.path.insert(0, str(SAAS_DIR))
