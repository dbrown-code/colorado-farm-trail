"""Offline tests for the Website / Facebook / Instagram URL cleanup the map build applies
(scripts/appdata/urls.py, used by build_map_data.py). Run: python -m pytest scripts/tests -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import build_map_data
from appdata import urls as U


@pytest.mark.parametrize("raw,exp", [
    # bare handles (Instagram allows dots)
    ("cbfarmersmarket", "https://instagram.com/cbfarmersmarket"),
    ("abundant.spaces", "https://instagram.com/abundant.spaces"),
    # '@' handles
    ("@durangofarmers", "https://instagram.com/durangofarmers"),
    ("@durangofarmers/", "https://instagram.com/durangofarmers"),
    # scheme-less URLs
    ("www.instagram.com/pueblofarmersmarket", "https://www.instagram.com/pueblofarmersmarket"),
    ("instagram.com/x", "https://instagram.com/x"),
    # already a URL; uppercase scheme is lowercased, host case kept
    ("https://www.instagram.com/x/", "https://www.instagram.com/x/"),
    ("HTTPS://Instagram.com/x", "https://Instagram.com/x"),
    # business names and empties are not links
    ("Foodshed Alliance", None),
    ("", None),
    (None, None),
])
def test_instagram_social_url(raw, exp):
    assert U.social_url(raw, U.INSTAGRAM_BASE) == exp


@pytest.mark.parametrize("raw,exp", [
    ("facebook.com/growers", "https://facebook.com/growers"),
    ("@growers", "https://facebook.com/growers"),
    ("Foodshed Alliance", None),
])
def test_facebook_social_url(raw, exp):
    assert U.social_url(raw, U.FACEBOOK_BASE) == exp


@pytest.mark.parametrize("raw,exp", [
    ("bergharvest.com", "https://bergharvest.com"),
    ("http://farm.example/x", "http://farm.example/x"),
    ("HTTPS://Farm.com", "https://Farm.com"),
    ("none", None),
    ("A Farm", None),
    ("", None),
])
def test_website_url(raw, exp):
    assert U.website_url(raw) == exp


def test_map_build_uses_the_shared_helpers():
    assert build_map_data.website_url is U.website_url
    assert build_map_data.social_url is U.social_url
