"""
01_themes_and_pronouns.py
Theme prevalence (share of interviews containing each leadership theme) by gender,
and the individual-vs-collective framing measure ("I/my" vs "we/our/team").

Run:  python 01_themes_and_pronouns.py
Out:  outputs/theme_prevalence.csv, outputs/pronoun_framing.csv
"""
import re, pandas as pd
from common import load_evidence, out
from markers import THEME_PATTERNS, FIRST_SINGULAR, FIRST_PLURAL, count

def main():
    _, epi = load_evidence()

    # ---- theme prevalence: an interview counts once if the pattern fires anywhere ----
    rows = []
    for name, pat in THEME_PATTERNS.items():
        epi[name] = epi["t"].apply(lambda s: 1 if re.search(pat, s) else 0)
        allp = epi[name].mean()
        f = epi.loc[epi.group == "IFF", name].mean()
        m = epi.loc[epi.group == "IFM", name].mean()
        rows.append([name, round(allp, 3), round(f, 3), round(m, 3)])
    themes = pd.DataFrame(rows, columns=["theme", "all", "female", "male"]).sort_values("all", ascending=False)
    themes.to_csv(out("theme_prevalence.csv"), index=False)

    # ---- pronoun framing: per-interview we-share = we / (I + we) ----
    epi["I"]  = epi["t"].apply(lambda s: count(FIRST_SINGULAR, s))
    epi["WE"] = epi["t"].apply(lambda s: count(FIRST_PLURAL, s))
    epi["we_share"] = epi["WE"] / (epi["I"] + epi["WE"]).replace(0, 1)
    pron = epi.groupby("group").agg(
        interviews=("we_share", "size"),
        mean_we_share=("we_share", "mean"),
        total_I=("I", "sum"),
        total_WE=("WE", "sum"),
    ).round(3)
    pron.to_csv(out("pronoun_framing.csv"))

    print("Theme prevalence (share of interviews):")
    print(themes.to_string(index=False))
    print("\nPronoun framing by gender (IFF=female, IFM=male):")
    print(pron.to_string())

if __name__ == "__main__":
    main()
