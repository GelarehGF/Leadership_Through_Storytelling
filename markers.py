"""
markers.py — shared discourse-marker definitions for the IF-Leadership analyses.

Every marker is a case-insensitive regex applied to the lower-cased concatenation
of a guest's self-description passages (one string per interview). A marker "fires"
for an interview if re.search finds it anywhere in that interview's text.

These are transparent, editable operationalisations. Tighten or extend them and
re-run the scripts to see how results move — that is the point of shipping the code.
"""
import re

# ---- leadership-theme families (used by 01_themes and 03_theory_fit) ----
THEME_PATTERNS = {
    "service/helping":
        r"\bhelp (you|them|people|others|someone|us|business|companies|startups)\b|\blet me help\b|"
        r"\blove to help\b|\bi (can|want to|wanted to) help\b|\bserve\b|\bservice\b|\bmeet(ing)? them where\b|"
        r"\bgive back\b|\bcommunity\b|\bit'?s about the people\b|\btake(s)? care of (my |our |their )?(patients|clients|customers|people)\b",
    "immigrant/outsider":
        r"\bimmigrant\b|\bcame to canada\b|\bfrom iran\b|\bfrom brazil\b|\bnewcomer\b|\blanguage barrier\b|"
        r"\bmy country\b|\bback home\b|\bmoved to\b|\bvisa\b|\binternational student\b|\bstarting over\b",
    "developing others/mentorship":
        r"\bmentor\b|\bcoach(ing)?\b|\bdevelop(ing)? (my |our )?(team|people|others)\b|\bhelp .* (grow|succeed|excel)\b|"
        r"\bsee (other )?people succeed\b|\bempower\b|\bhire\b|\bmy team\b",
    "vision/mission":
        r"\bvision\b|\bmission\b|\bpurpose\b|\bimpact\b|\bchange the world\b|\bbigger than\b|\bbelieve in\b|\bnorth star\b",
    "risk/leap":
        r"\brisk\b|\btook a chance\b|\bleap\b|\bjump(ed)? (in|into)\b|\bgamble\b|\ball in\b|\bquit my job\b",
    "failure/resilience":
        r"\bfail(ed|ure|ing)?\b|\bmistake(s)?\b|\bhomeless\b|\brock bottom\b|\bstruggle(d)?\b|\blost everything\b|\bresilien\w*\b",
    "gender barriers":
        r"\bas a woman\b|\bwoman of colou?r\b|\bwomen in\b|\bmale-?dominated\b|\bglass ceiling\b|\bbias\b|"
        r"\bmicroaggress\w*\b|\bprove myself\b|\bsacred ground\b",
    "hustle/hard work":
        r"\bhustle\b|\bgrind\b|\bwork(ed|ing)? (hard|really hard)\b|\bnonstop\b|\bsacrifice\b|\blong hours\b|\b24/7\b",
}

# ---- pronoun families (used by 01_themes: individual vs collective framing) ----
FIRST_SINGULAR = r"\b(i|i'm|i've|i'd|i'll|my|myself|me)\b"
FIRST_PLURAL   = r"\b(we|we're|we've|our|us|ourselves|team)\b"

# ---- theory-level marker families for the four "added" theories (03_theory_fit) ----
SERVICE  = r"\bhelp (you|them|people|others|someone|us|business|companies|startups)\b|\blet me help\b|\blove to help\b|\bi (can|want to|wanted to) help\b"
SERVE    = r"\bserve\b|\bservice\b|\bserving\b|\bgive back\b|\bmeet(ing)? them where\b|\bit'?s about the people\b|\btake(s)? care of (my |our |their )?(patients|clients|customers|people)\b|\bhelp make them better\b"
DEVELOP  = r"\bmentor\b|\bcoach(ing)?\b|\bempower\b|\bsee (other )?people succeed\b|\bhelp .* (grow|succeed|excel)\b|\bdevelop(ing)? (my |our )?(team|people|others)\b"
VISION   = r"\bvision\b|\bmission\b|\bpurpose\b|\bnorth star\b|\bmission-?driven\b"
INSPIRE  = r"\binspir(e|ing|ation)\b|\bmotivat(e|ing)\b|\bimpact\b|\bchange the world\b|\bbigger than\b|\brally the\b|\bbelieve in\b"
COFOUND  = r"\bco-?founder(s)?\b|\bmy partner\b|\bbusiness partner\b|\bpartners\b|\bour team\b|\bmy team\b|\bteam member(s)?\b"
COLLAB   = r"\btogether\b|\bcollaborat(e|ion|ive)\b|\bwe built\b|\bwe (started|created|decided|did)\b|\brelationship(s)?\b|\bpartnership\b"
VALUES   = r"\bvalue(s)?\b|\btrue to (my|myself|my heart)\b|\bauthentic\b|\bintegrity\b|\bprinciple(s)?\b|\bmoral\b|\bwho i (am|really am)\b|\bmy why\b"
TRANSP   = r"\bhonest\b|\btransparen(t|cy)\b|\bopen and honest\b|\bbe real\b"
VULN     = r"\bfail(ed|ure|ing)?\b|\bmistake(s)?\b|\bvulnerab\w*\b|\blost everything\b|\bself-?aware\b"

def has(pattern, text):
    """1 if the regex is found in text (already lower-cased), else 0."""
    return 1 if re.search(pattern, text) else 0

def count(pattern, text):
    """number of matches of pattern in text."""
    return len(re.findall(pattern, text))
