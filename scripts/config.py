"""Shared paths.

DATA_DIR: folder that holds the source materials (BKBSIN_Mandarin_A_Quiet/,
BKBSIN_Mandarin_B_Quiet/, BKBSIN_Mandarin_C/, msp_disyllables/, WIN/) and
receives the outputs (BKBSIN_Mandarin_SIN/, WIN_Mandarin/).
Set it with the SIN_DATA_DIR environment variable; by default it is the
folder that contains this repository.
"""
import os
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SIN_DATA_DIR", REPO_DIR.parent)).expanduser().resolve()
WORK_DIR = REPO_DIR / "intermediate"
WORK_DIR.mkdir(exist_ok=True)

R = str(DATA_DIR)
def work(name):
    return str(WORK_DIR / name)
