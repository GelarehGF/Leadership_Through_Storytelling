"""
04_theory_network.py
Co-occurrence network where NODES are leadership-theory variables and EDGES link
variables that appear together in the same interview above chance.

Steps:
  1. Build a 61 x 26 interview-by-variable binary matrix (pipeline codings for the
     Identity/Provisional/Implicit variables, discourse markers for the rest).
  2. For every pair compute co-occurrence, lift (obs/expected), and phi.
  3. Keep edges with lift>1.15, co-occurrence>=6, phi>0.05; weight = phi.
  4. Compute degree/eigenvector/betweenness centrality and Louvain communities.
  5. Write node metrics, edge list, a static figure and a self-contained HTML explorer.

Run:  python 04_theory_network.py
Out:  outputs/network_node_metrics.csv, network_edges.csv,
      theory_variable_network.png, theory_network_interactive.html
"""
import re, json, itertools, pandas as pd, numpy as np, networkx as nx
from common import load_evidence, load_pipeline, out
from markers import has

PAL = {"Servant": "#1b9e8f", "IdentityConstruction": "#d1495b", "ImplicitLeadership": "#e6a417",
       "Relational": "#2e6f95", "ProvisionalSelves": "#8c6bb1", "Authentic": "#5a9e6f",
       "Transformational": "#e07a5f"}
LBL = {"Servant": "Servant", "IdentityConstruction": "Identity Construction",
       "ImplicitLeadership": "Implicit Leadership", "Relational": "Relational / LAP",
       "ProvisionalSelves": "Provisional Selves", "Authentic": "Authentic",
       "Transformational": "Transformational"}

def build_matrix(epi, P):
    A, B, C = P["A"], P["B"], P["C"]
    def m(pat, tid): return 1 if re.search(pat, epi.loc[tid, "t"]) else 0
    # (theory, function tid -> 0/1)
    nodes = {}
    # ---- Servant ----
    nodes["SV:serving/helping"]      = ("Servant", lambda i: m(r"\bhelp (you|them|people|others|someone|us|business|companies|startups)\b|\blet me help\b|\blove to help\b|\bi (can|want to|wanted to) help\b|\bmeet(ing)? them where\b|\bserve\b|\bservice\b|\bit'?s about the people\b|\btake(s)? care of (my |our |their )?(patients|clients|customers|people)\b", i))
    nodes["SV:developing others"]    = ("Servant", lambda i: m(r"\bmentor\b|\bcoach(ing)?\b|\bsee (other )?people succeed\b|\bhelp .* (grow|succeed|excel)\b|\bdevelop(ing)? (my |our )?(team|people|others)\b", i))
    nodes["SV:community/stewardship"]= ("Servant", lambda i: m(r"\bcommunity\b|\bgive back\b|\bgiving back\b|\bour nation\b|\bpeople-?centric\b|\bleave the planet\b", i))
    nodes["SV:empowerment"]          = ("Servant", lambda i: m(r"\bempower\b|\bconfiden(t|ce) (in|to)\b|\byou'?re better than you think\b|\bmotivate\b|\benable them\b", i))
    # ---- Transformational ----
    nodes["TF:vision/mission"]       = ("Transformational", lambda i: m(r"\bvision\b|\bmission\b|\bpurpose\b|\bnorth star\b", i))
    nodes["TF:inspiration/impact"]   = ("Transformational", lambda i: m(r"\binspir(e|ing|ation)\b|\bmotivat(e|ing)\b|\bimpact\b|\bchange the world\b|\bbigger than\b|\bbelieve in\b", i))
    nodes["TF:innovation/challenge"] = ("Transformational", lambda i: m(r"\binnovat(e|ion|ive)\b|\bdisrupt\b|\bchallenge the (status quo|way)\b|\bahead of my time\b|\bbetter way\b|\breinvent\b", i))
    # ---- Relational / LAP ----
    nodes["RL:co-founder/team"]      = ("Relational", lambda i: m(r"\bco-?founder(s)?\b|\bmy partner\b|\bbusiness partner\b|\bour team\b|\bmy team\b|\bteam member(s)?\b|\bwe hire\b", i))
    nodes["RL:collaboration"]        = ("Relational", lambda i: m(r"\bcollaborat(e|ion|ive)\b|\btogether\b|\bwe built\b|\bwe (started|created|decided|did)\b|\bwork(ing)? with (our|the) (partners|community|nation)\b", i))
    nodes["RL:relationship-based"]   = ("Relational", lambda i: m(r"\brelationship(s)?\b|\bpartnership(s)?\b|\bstrategic partner\b|\bnetwork\b|\bpeople will seek you out\b", i))
    # ---- Authentic ----
    nodes["AU:values/integrity"]     = ("Authentic", lambda i: m(r"\bvalue(s)?\b|\bintegrity\b|\bprinciple(s)?\b|\bmoral\b|\bethical\b|\bnever (compromise|going to compromise)\b", i))
    nodes["AU:self-awareness"]       = ("Authentic", lambda i: m(r"\bself-?aware\b|\btrue to (my|myself|my heart)\b|\bwho i (am|really am)\b|\bmy why\b|\bknow (myself|yourself|who you are)\b|\blisten to yourself\b", i))
    nodes["AU:transparency/honesty"] = ("Authentic", lambda i: m(r"\bhonest\b|\btransparen(t|cy)\b|\bopen and honest\b|\bbe real\b|\bauthentic\b|\btell the truth\b", i))
    nodes["AU:vulnerability/failure"]= ("Authentic", lambda i: m(r"\bfail(ed|ure|ing)?\b|\bmistake(s)?\b|\bvulnerab\w*\b|\blost everything\b|\brock bottom\b|\bstruggl(e|ed)\b", i))
    # ---- Identity Construction (pipeline A) ----
    nodes["IC:identity claim (explicit)"] = ("IdentityConstruction", lambda i: 1 if (i in A.index and A.loc[i, "identity_internalization"] == "explicit") else 0)
    nodes["IC:identity claim (implicit)"] = ("IdentityConstruction", lambda i: 1 if (i in A.index and A.loc[i, "identity_internalization"] == "implicit") else 0)
    nodes["IC:granting to others"]        = ("IdentityConstruction", lambda i: 1 if (i in A.index and A.loc[i, "reciprocity"] in ("claims_and_grants", "grants_without_claiming")) else 0)
    nodes["IC:collective endorsement"]    = ("IdentityConstruction", lambda i: 1 if (i in A.index and A.loc[i, "collective_endorsement"] == "present") else 0)
    # ---- Provisional Selves (pipeline B) ----
    nodes["PS:role-model observing"] = ("ProvisionalSelves", lambda i: 1 if (i in B.index and B.loc[i, "observing"] in ("named_role_model", "generic_role_model", "institutional")) else 0)
    nodes["PS:experimenting"]        = ("ProvisionalSelves", lambda i: 1 if (i in B.index and B.loc[i, "experimenting"] == "explicit_experimentation") else 0)
    nodes["PS:evaluating"]           = ("ProvisionalSelves", lambda i: 1 if (i in B.index and B.loc[i, "evaluating"] in ("both", "external_feedback", "internal_standards")) else 0)
    nodes["PS:becoming trajectory"]  = ("ProvisionalSelves", lambda i: 1 if (i in B.index and B.loc[i, "identity_trajectory"] == "becoming") else 0)
    # ---- Implicit Leadership prototypes (pipeline C) ----
    for dim in ["sensitivity", "intelligence", "dedication", "dynamism"]:
        nodes[f"ILT:{dim}"] = ("ImplicitLeadership", (lambda d: lambda i: 1 if (i in C.index and C.loc[i, d] in ("central", "illustrated")) else 0)(dim))

    ids = list(epi.index)
    M = pd.DataFrame({name: [fn(i) for i in ids] for name, (th, fn) in nodes.items()}, index=ids)
    theory_of = {name: th for name, (th, fn) in nodes.items()}
    return M, theory_of

def build_network(M, theory_of, lift_min=1.15, cooccur_min=6, phi_min=0.05):
    nodes = list(M.columns); n = len(M); pm = M.mean()
    G = nx.Graph()
    for nd in nodes:
        G.add_node(nd, theory=theory_of[nd], prevalence=float(pm[nd]))
    edge_rows = []
    for a, b in itertools.combinations(nodes, 2):
        both = int(((M[a] == 1) & (M[b] == 1)).sum())
        if both == 0:
            continue
        exp = pm[a] * pm[b] * n
        lift = both / exp if exp > 0 else 0
        phi = np.corrcoef(M[a], M[b])[0, 1]
        cross = theory_of[a] != theory_of[b]
        keep = (lift > lift_min and both >= cooccur_min and phi > phi_min)
        edge_rows.append((a, b, both, round(lift, 3), round(float(phi), 3), cross, keep))
        if keep:
            G.add_edge(a, b, weight=float(phi), cooccur=both, lift=lift)
    edges = pd.DataFrame(edge_rows, columns=["a", "b", "cooccur", "lift", "phi", "cross_theory", "kept"])
    return G, edges

def metrics_frame(G, M, theory_of):
    deg = dict(G.degree(weight="weight"))
    eig = nx.eigenvector_centrality_numpy(G, weight="weight") if G.number_of_edges() else {}
    btw = nx.betweenness_centrality(G, weight=lambda u, v, d: 1/(d["weight"]+1e-6))
    comms = nx.community.louvain_communities(G, weight="weight", seed=42) if G.number_of_edges() else []
    nc = {nd: ci for ci, s in enumerate(comms) for nd in s}
    pm = M.mean()
    df = pd.DataFrame({
        "node": list(M.columns),
        "theory": [theory_of[x] for x in M.columns],
        "prevalence": [round(float(pm[x]), 3) for x in M.columns],
        "weighted_degree": [round(deg.get(x, 0), 3) for x in M.columns],
        "eigenvector": [round(eig.get(x, 0), 3) for x in M.columns],
        "betweenness": [round(btw.get(x, 0), 3) for x in M.columns],
        "community": [nc.get(x, -1) for x in M.columns],
    }).sort_values("eigenvector", ascending=False)
    return df, comms

def static_figure(G, met, kept, theory_of):
    import matplotlib.pyplot as plt, matplotlib as mpl
    from matplotlib.lines import Line2D
    mpl.rcParams.update({"font.family": "DejaVu Sans"})
    prev = dict(zip(met.node, met.prevalence))
    pos = nx.spring_layout(G, weight="weight", k=1.6, iterations=500, seed=11)
    fig, ax = plt.subplots(figsize=(15, 11.6))
    fig.suptitle("Theory-variable co-occurrence network across 61 founder interviews",
                 fontsize=17, fontweight="bold", x=0.02, ha="left", y=0.985)
    for _, r in kept.iterrows():
        x = [pos[r.a][0], pos[r.b][0]]; y = [pos[r.a][1], pos[r.b][1]]
        ax.plot(x, y, color="#9aa0a6" if r.cross_theory else "#cfd3d8",
                lw=0.5 + 3.4*r.phi, alpha=0.25 + 0.5*r.phi, zorder=1, solid_capstyle="round")
    for _, r in met.iterrows():
        x, y = pos[r.node]
        ax.scatter(x, y, s=260 + prev[r.node]*2200, c=PAL[r.theory], edgecolor="white", linewidth=1.5, zorder=3)
        ax.text(x, y - (0.052 + prev[r.node]*0.045), r.node.split(":", 1)[1], fontsize=8.2, ha="center", va="top", zorder=4)
    h = [Line2D([0], [0], marker="o", color="w", markerfacecolor=PAL[k], markersize=13, label=LBL[k]) for k in PAL]
    ax.legend(handles=h, title="Theory (node colour)", loc="upper left", fontsize=9.5)
    ax.axis("off"); ax.margins(0.13); plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out("theory_variable_network.png"), dpi=150, bbox_inches="tight", facecolor="white")

def interactive_html(met, kept, theory_of):
    nodes = [{"id": r.node, "label": r.node.split(":", 1)[1], "group": r.theory,
              "value": float(r.prevalence), "color": PAL[r.theory],
              "title": f"{r.node}<br>{LBL[r.theory]}<br>prevalence {r.prevalence:.0%} · eig {r.eigenvector} · btw {r.betweenness}"}
             for _, r in met.iterrows()]
    edges = [{"from": r.a, "to": r.b, "value": float(r.phi), "cross": bool(r.cross_theory),
              "title": f"co-occur {int(r.cooccur)} · phi {r.phi} · lift {r.lift}"} for _, r in kept.iterrows()]
    legend = "".join(f'<span style="margin-right:12px"><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{PAL[k]}"></span> {LBL[k]}</span>' for k in PAL)
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>body{{font-family:system-ui,Arial;margin:0}}header{{padding:14px 20px}}#net{{height:80vh;border-top:1px solid #eee}}</style></head>
<body><header><h2>Leadership theory-variable co-occurrence network</h2>
<div style="font-size:13px;color:#555">Nodes = theory variables · edges = above-chance co-occurrence (phi-weighted). 86% of edges cross theory boundaries.</div>
<div style="margin-top:6px;font-size:12px">{legend}</div>
<label style="font-size:12px"><input type="checkbox" id="cross"> cross-theory edges only</label></header>
<div id="net"></div><script>
const N={json.dumps(nodes)},E={json.dumps(edges)};
const nodes=new vis.DataSet(N),edges=new vis.DataSet(E.map((e,i)=>({{id:i,from:e.from,to:e.to,value:e.value,title:e.title,width:0.5+e.value*7,color:{{color:e.cross?'#9aa0a6':'#d5d5d5'}}}})));
const net=new vis.Network(document.getElementById('net'),{{nodes,edges}},{{nodes:{{shape:'dot',scaling:{{min:10,max:50}}}},physics:{{barnesHut:{{springLength:150}}}},interaction:{{hover:true}}}});
document.getElementById('cross').onchange=e=>{{edges.clear();edges.add(E.filter(x=>!e.target.checked||x.cross).map((x,i)=>({{id:i,from:x.from,to:x.to,value:x.value,title:x.title,width:0.5+x.value*7,color:{{color:x.cross?'#9aa0a6':'#d5d5d5'}}}})));}};
</script></body></html>"""
    open(out("theory_network_interactive.html"), "w").write(html)

def main():
    _, epi = load_evidence(); P = load_pipeline()
    M, theory_of = build_matrix(epi, P)
    M.to_csv(out("network_node_matrix.csv"))
    G, edges = build_network(M, theory_of)
    edges.to_csv(out("network_edges.csv"), index=False)
    kept = edges[edges.kept].reset_index(drop=True)
    met, comms = metrics_frame(G, M, theory_of)
    met.to_csv(out("network_node_metrics.csv"), index=False)
    cross = kept.cross_theory.mean() if len(kept) else 0
    print(f"nodes={G.number_of_nodes()} edges={G.number_of_edges()} "
          f"cross-theory={kept.cross_theory.sum()}/{len(kept)} ({cross:.0%})")
    print("\ncommunities (Louvain):")
    for ci, s in enumerate(comms):
        print(f"  C{ci}: " + ", ".join(sorted(s)))
    print("\ntop nodes by eigenvector centrality:")
    print(met.head(8)[["node", "theory", "prevalence", "eigenvector", "betweenness"]].to_string(index=False))
    static_figure(G, met, kept, theory_of)
    interactive_html(met, kept, theory_of)
    print("\nwrote outputs/theory_variable_network.png and theory_network_interactive.html")

if __name__ == "__main__":
    main()
