"""Join the pinned release's directory rows to the Food Web app export (open-food-web.json).

The release's directory.csv is the flat list the map is drawn from; the export holds what the flat file
cannot: visits with their hours, whether guests are welcome, sales channels, sources and who confirmed what.
directory.csv carries no IDs, so a row is matched to its record by name, then (for repeated names) by
town, then by distance to one of the record's places, then producer over outlet. A row that still matches
more than one record gets no detail rather than the wrong one.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

EXPORT = Path(__file__).resolve().parent.parent.parent / "data" / "foodweb" / "open-food-web.json"


def nkey(s) -> str:
    s = (s or "").lower().replace("’", "'").replace("�", "'").replace("'", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


class Export:
    def __init__(self, path: Path = EXPORT):
        self.data = json.loads(path.read_text(encoding="utf-8"))
        self.vocab = self.data.get("vocab", {})
        self._by_name: Dict[str, List[dict]] = {}
        for kind in ("producers", "markets", "outlets", "access_points"):
            for rec in self.data.get(kind, []):
                self._by_name.setdefault(nkey(rec["name"]), []).append(rec)

    @staticmethod
    def _places(rec: dict) -> List[dict]:
        return rec.get("locations") or ([rec["location"]] if rec.get("location") else [])

    def match(self, name: str, city: Optional[str], lat: Optional[float], lng: Optional[float]) -> Optional[dict]:
        cands = self._by_name.get(nkey(name), [])
        if len(cands) <= 1:
            return cands[0] if cands else None
        if city:
            by_town = [c for c in cands if any(nkey(p.get("city")) == nkey(city) for p in self._places(c))]
            if len(by_town) == 1:
                return by_town[0]
        if lat is not None and lng is not None:
            near = [c for c in cands if any(p.get("lat") is not None and abs(p["lat"] - lat) < 0.01
                                            and abs(p["lon"] - lng) < 0.01 for p in self._places(c))]
            if len(near) == 1:
                return near[0]
        prod = [c for c in cands if c["id"].startswith("co-p-")]
        return prod[0] if len(prod) == 1 else None

    def channel_labels(self, rec: dict) -> List[str]:
        labels = self.vocab.get("sales_channels", {})
        return [labels.get(c, c) for c in rec.get("sales_channels") or [] if c != "none"]


def guests(rec: dict) -> Optional[str]:
    """Do they want visitors? 'yes' (a stand, shop, tour...), 'appointment', 'no' (they said so), or None (unknown)."""
    visits = rec.get("visits") or []
    types = {v["type"] for v in visits}
    if types - {"by_appointment"}:
        return "yes"
    if "by_appointment" in types:
        return "appointment"
    if rec.get("dropin_visits") is True:
        return "yes"
    if rec.get("dropin_visits") is False:
        return "no"
    return None


def detail(ex: Export, rec: dict) -> dict:
    """The compact visit facts the map popup needs. Empty keys are left out to keep markets.json small."""
    out = {"id": rec["id"], "slug": rec["slug"]}
    g = guests(rec)
    if g:
        out["guests"] = g
    if rec.get("visits"):
        out["ways"] = [{"label": v["label"], **({"detail": v["detail"]} if v.get("detail") else {})} for v in rec["visits"]]
    if rec.get("visit_note"):
        out["visitNote"] = rec["visit_note"]
    if rec.get("farm_pickup") is True:
        out["pickup"] = True
    ch = ex.channel_labels(rec)
    if ch:
        out["channels"] = ch
    return out
