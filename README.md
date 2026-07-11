# IF-Leadership corpus analyses — reproducible code

Regenerates every number, table, figure, and the interactive network for the
leadership-podcast study, from four input CSVs. All operationalisations are
transparent and editable (see `markers.py`); re-run any script after changing a
marker or a rating to see how results move.

## Inputs (place in `./inputs/`)
- `evidence.csv` — extracted guest self-description passages
  (`transcript_id, guest_name, gender, passage_id, passage, passage_words`)
- `codes_A.csv`, `codes_B.csv`, `codes_C.csv` — the pipeline's per-interview codings
  for Framework A (DeRue & Ashford), B (Ibarra), C (Epitropaki & Martin)
- `immigrant_outsider_coded.csv` — the researcher-coded immigrant/outsider table
  (used by script 02; the coding itself is the data, the script derives the stats)

## Setup
```bash
python -m venv .venv && source .venv/bin/activate      # optional
pip install -r requirements.txt
```

## Run (order-independent; each writes to ./outputs/)
```bash
python 01_themes_and_pronouns.py     # theme prevalence + I/we framing by gender
python 02_immigrant_outsider.py      # immigrant/outsider summary + workbook + marker cross-check
python 03_theory_fit.py              # 7-theory fit scorecard + ranking figure
python 04_theory_network.py          # co-occurrence network: matrix, metrics, figure, HTML
```
Override paths with env vars: `IFL_INPUT=/path/to/inputs IFL_OUTPUT=/path/to/outputs python 03_theory_fit.py`

## What each script produces
| Script | Key outputs |
|---|---|
| 01 | `theme_prevalence.csv`, `pronoun_framing.csv` |
| 02 | `immigrant_outsider_coded.xlsx`, `immigrant_outsider_summary.csv` |
| 03 | `theory_fit_master.csv`, `theory_fit_ranking.png` |
| 04 | `network_node_matrix.csv`, `network_node_metrics.csv`, `network_edges.csv`, `theory_variable_network.png`, `theory_network_interactive.html` |

## Method notes & caveats (read before quoting numbers)
- **Two coding sources.** Frameworks A/B/C come from the LLM pipeline (more sensitive);
  the four added theories (Servant, Transformational, Relational, Authentic) and all
  theme/pronoun measures come from discourse markers. Cross-method *coverage*
  comparisons are therefore indicative — centrality (a reasoned rating in
  `03_theory_fit.py:CENTRALITY`) is the firmer cross-theory axis.
- **Network within-framework inflation.** Variables coded from the same pipeline
  framework co-occur partly by construction, inflating their within-cluster
  centrality. The 86%-cross-theory headline is robust to this; treat within-theory
  density cautiously.
- **Known data-quality issues in the pipeline inputs** (fix before final stats):
  `codes_C.csv` has one corrupt cell (`dominant_dimension = "0.75"`); `codes_B.csv`
  contains a stray id `"B"` and is missing `IFM-004`; two different guests are both
  named "Shireen Saleh" (IFF-015, IFF-019); "Anita Huberman" appears as IFF-012 and
  IFF-017. The scripts tolerate these but the counts they affect are noted in output.

## Editing the analysis
- Change a theme/theory definition → edit the regex in `markers.py`.
- Change a theory's centrality rating or the composite weights → `03_theory_fit.py`.
- Change network edge thresholds (lift / co-occurrence / phi) → `build_network()` args
  in `04_theory_network.py`.
