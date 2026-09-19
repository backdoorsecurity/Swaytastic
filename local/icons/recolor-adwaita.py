#!/usr/bin/env python3
"""Legacy icon rebuild. Use: python3 local/apply-pack.py <pack>"""
import os
import sys
from pathlib import Path

apply = Path(__file__).resolve().parent.parent / "apply-pack.py"
pack = sys.argv[1] if len(sys.argv) > 1 else "Pink_Techno_Syrup"
os.execv(sys.executable, [sys.executable, str(apply), pack])
