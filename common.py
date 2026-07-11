"""
common.py — shared IO helpers.

Input files expected in INPUT_DIR (default ./inputs):
    evidence.csv   columns: transcript_id, guest_name, gender, passage_id, passage, passage_words
    codes_A.csv    pipeline coding, Framework A (DeRue & Ashford)  — one row per interview
    codes_B.csv    pipeline coding, Framework B (Ibarra)
    codes_C.csv    pipeline coding, Framework C (Epitropaki & Martin)
    immigrant_outsider_coded.csv   researcher-coded immigrant/outsider table (input to 02)

Outputs are written to OUTPUT_DIR (default ./outputs).
"""
import os, pandas as pd

INPUT_DIR  = os.environ.get("IFL_INPUT",  os.path.join(os.path.dirname(__file__), "inputs"))
OUTPUT_DIR = os.environ.get("IFL_OUTPUT", os.path.join(os.path.dirname(__file__), "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def inp(name):  return os.path.join(INPUT_DIR, name)
def out(name):  return os.path.join(OUTPUT_DIR, name)

def load_evidence():
    """Return (ev, epi): raw passage rows and a per-interview frame with a lower-cased 'text'."""
    ev = pd.read_csv(inp("evidence.csv"))
    ev["transcript_id"] = ev["transcript_id"].astype(str).str.strip()
    epi = ev.groupby("transcript_id").agg(
        guest_name=("guest_name", "first"),
        gender=("gender", "first"),
        text=("passage", lambda s: " ".join(str(x) for x in s)),
    )
    epi["t"] = epi["text"].str.lower()
    epi["nwords"] = epi["text"].str.split().apply(len)
    epi["group"] = [i[:3] for i in epi.index]  # IFF (female) / IFM (male)
    return ev, epi

def load_pipeline():
    """Return dict of the three pipeline codings, indexed by transcript_id (stripped)."""
    out_ = {}
    for k in ("A", "B", "C"):
        d = pd.read_csv(inp(f"codes_{k}.csv"))
        d["transcript_id"] = d["transcript_id"].astype(str).str.strip()
        out_[k] = d.set_index("transcript_id")
    return out_
