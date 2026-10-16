"""The directory-to-export join: repeated names resolve by town, then place, then producer; never to the wrong record."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from appdata import foodweb_export as fx


def _export(recs):
    ex = fx.Export.__new__(fx.Export)
    ex.vocab = {"sales_channels": {"csa": "CSA", "none": "No public sales"}}
    ex._by_name = {}
    for r in recs:
        ex._by_name.setdefault(fx.nkey(r["name"]), []).append(r)
    return ex


def test_match_by_town_then_place_then_producer():
    a = {"id": "co-p-1", "name": "Roasted Chili", "locations": [{"city": "Pueblo", "lat": 38.2, "lon": -104.6}]}
    b = {"id": "co-p-2", "name": "Roasted Chili", "locations": [{"city": "Salida", "lat": 38.5, "lon": -106.0}]}
    o = {"id": "co-o-1", "name": "Hidy Honey", "locations": []}
    p = {"id": "co-p-3", "name": "Hidy Honey", "locations": []}
    ex = _export([a, b, o, p])
    assert ex.match("Roasted Chili", "Salida", None, None) is b
    assert ex.match("Roasted Chili", None, 38.2, -104.6) is a
    assert ex.match("Roasted Chili", None, None, None) is None
    assert ex.match("Hidy Honey", None, None, None) is p


def test_guests_uses_their_answer_and_stated_visits():
    assert fx.guests({"visits": [{"type": "farm_stand"}]}) == "yes"
    assert fx.guests({"visits": [{"type": "by_appointment"}]}) == "appointment"
    assert fx.guests({"visits": [], "dropin_visits": False}) == "no"
    assert fx.guests({"visits": [{"type": "tour"}], "dropin_visits": False}) == "yes"   # tours kept when no drop-ins
    assert fx.guests({"visits": [], "dropin_visits": None}) is None


def test_detail_leaves_out_empty_fields():
    ex = _export([])
    d = fx.detail(ex, {"id": "x", "slug": "x", "visits": [], "sales_channels": ["none"]})
    assert d == {"id": "x", "slug": "x"}
