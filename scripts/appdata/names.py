"""Name matching used by the Gunnison prototype builder."""
import re


def name_key(name: str) -> str:
    """Collapse a market name to a comparison key: lowercase, strip punctuation and
    common filler words so 'Pueblo Farmers Market' == 'Pueblo Farmers' Market'."""
    s = (name or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    stop = {"farmers", "farmer", "market", "markets", "the", "at", "of", "co",
            "colorado", "downtown", "community", "inc", "llc"}
    toks = [t for t in s.split() if t and t not in stop]
    return " ".join(sorted(toks)) if toks else re.sub(r"\s+", " ", s).strip()
