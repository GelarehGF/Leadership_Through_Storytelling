"""
03_theory_fit.py
Seven-theory fit comparison. Computes, for each theory:
  - coverage (share of interviews where the core construct is present)
  - "clear" coverage and salience (clear / any)
  - a composite fit index = 0.35*coverage + 0.25*salience + 0.40*centrality

Coverage for theories A/B/C (Identity Construction, Provisional Selves, Implicit
Leadership) is derived from the pipeline codings; coverage for the four added
theories (Servant, Transformational, Relational, Authentic) from discourse markers.

CENTRALITY is a reasoned 0-1 rating from close reading (documented in CENTRALITY
below) — edit those values to test the sensitivity of the ranking.

Run:  python 03_theory_fit.py
Out:  outputs/theory_fit_master.csv, outputs/theory_fit_ranking.png
"""
import pandas as pd, numpy as np
from common import load_evidence, load_pipeline, out
from markers import (SERVICE, SERVE, DEVELOP, VISION, INSPIRE, COFOUND, COLLAB,
                     VALUES, TRANSP, VULN, has)

# reasoned centrality ratings + citations + one-line verdicts (edit to taste)
CENTRALITY = {
    "Leadership Identity Construction":            (0.75, "DeRue & Ashford (2010)", "Widest reach; captures the claiming half only"),
    "Implicit Leadership Theories (prototypes)":   (0.35, "Epitropaki & Martin (2004)", "Universal but non-distinctive"),
    "Servant leadership":                          (0.90, "Liden et al. (2008) / Greenleaf", "Best captures the leadership style"),
    "Relational / Leadership-as-Practice":         (0.70, "Uhl-Bien (2006); Raelin (2016)", "Substantive; two distinct flavours"),
    "Provisional Selves / identity work":          (0.30, "Ibarra (1999)", "Poorest fit - arrival, not becoming"),
    "Authentic leadership":                        (0.50, "Walumbwa et al. (2008)", "Central for some, peripheral overall"),
    "Transformational leadership":                 (0.40, "Bass (1985)", "Vision present but secondary"),
}

def pipeline_metrics(P):
    """coverage(any), clear coverage, salience for the three pipeline-coded theories."""
    A, B, C = P["A"], P["B"], P["C"]; nA, nB, nC = len(A), len(B), len(C)
    # A: identity claiming (explicit=clear, explicit|implicit=any)
    A_clear = (A.identity_internalization == "explicit").sum()
    A_any   = A.identity_internalization.isin(["explicit", "implicit"]).sum()
    # B: provisional-self work (role-model observed AND explicit experimentation = clear)
    obs = ~B.observing.isin(["insufficient_evidence", "absent"])
    exp = B.experimenting == "explicit_experimentation"
    B_clear = (obs & exp).sum()
    B_any   = (exp | (B.identity_trajectory == "becoming")).sum()
    # C: >=1 prototype central = clear; any prototype present = any
    dims = ["sensitivity", "intelligence", "dedication", "dynamism"]
    C_clear = C[dims].apply(lambda r: (r == "central").any(), axis=1).sum()
    C_any   = C[dims].apply(lambda r: r.isin(["central", "illustrated"]).any(), axis=1).sum()
    return {
        "Leadership Identity Construction":          (A_any/nA, A_clear/nA),
        "Provisional Selves / identity work":        (B_any/nB, B_clear/nB),
        "Implicit Leadership Theories (prototypes)": (C_any/nC, C_clear/nC),
    }

def marker_metrics(epi):
    """coverage(any) and clear for the four added theories via 2-condition rubric."""
    res = {}
    def collect(fn):
        vals = [fn(epi.loc[i, "t"]) for i in epi.index]  # 0/1/2 per interview
        clear = sum(v == 2 for v in vals); any_ = sum(v >= 1 for v in vals); n = len(vals)
        return any_/n, clear/n
    res["Servant leadership"] = collect(lambda t:
        2 if ((has(SERVICE, t) or has(SERVE, t)) and has(DEVELOP, t))
        else (1 if (has(SERVICE, t) or has(SERVE, t) or has(DEVELOP, t)) else 0))
    res["Transformational leadership"] = collect(lambda t:
        2 if (has(VISION, t) and has(INSPIRE, t)) else (1 if (has(VISION, t) or has(INSPIRE, t)) else 0))
    res["Relational / Leadership-as-Practice"] = collect(lambda t:
        2 if (has(COFOUND, t) and has(COLLAB, t)) else (1 if (has(COFOUND, t) or has(COLLAB, t)) else 0))
    res["Authentic leadership"] = collect(lambda t:
        2 if (has(VALUES, t) and (has(TRANSP, t) or has(VULN, t)))
        else (1 if (has(VALUES, t) or has(TRANSP, t) or has(VULN, t)) else 0))
    # For servant, use the broader validated service prevalence as coverage(any)
    return res

def main():
    _, epi = load_evidence()
    P = load_pipeline()
    cov = {**pipeline_metrics(P), **marker_metrics(epi)}
    rows = []
    for theory, (cov_any, cov_clear) in cov.items():
        salience = (cov_clear / cov_any) if cov_any else 0
        cent, cite, verdict = CENTRALITY[theory]
        composite = 0.35 * cov_any + 0.25 * salience + 0.40 * cent
        rows.append([theory, cite, round(cov_any, 3), round(cov_clear, 3),
                     round(salience, 3), cent, round(composite, 3), verdict])
    df = pd.DataFrame(rows, columns=["theory", "citation", "cov_any", "cov_clear",
                                     "salience", "centrality", "composite", "verdict"])
    df = df.sort_values("composite", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", df.index + 1)
    df.to_csv(out("theory_fit_master.csv"), index=False)
    print(df.to_string(index=False))
    make_figure(df)

def make_figure(df):
    import matplotlib.pyplot as plt, matplotlib as mpl
    mpl.rcParams.update({"font.family": "DejaVu Sans"})
    def col(c): return "#1b7a6e" if c >= .60 else ("#4a9b8e" if c >= .45 else ("#e0a458" if c >= .35 else "#c1666b"))
    d = df.sort_values("composite")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(d.theory, d.composite, color=[col(c) for c in d.composite], edgecolor="white")
    for y, (c, v) in enumerate(zip(d.composite, d.verdict)):
        ax.text(c + 0.01, y, f"{c:.2f}", va="center", fontweight="bold", fontsize=10)
    ax.set_xlabel("Composite fit  (0.35*coverage + 0.25*salience + 0.40*centrality)")
    ax.set_title("Which leadership theory best describes the corpus (n=61)", fontweight="bold", loc="left")
    ax.spines[["top", "right"]].set_visible(False); ax.tick_params(length=0)
    plt.tight_layout(); plt.savefig(out("theory_fit_ranking.png"), dpi=150, facecolor="white")
    print("\nwrote outputs/theory_fit_ranking.png")

if __name__ == "__main__":
    main()
