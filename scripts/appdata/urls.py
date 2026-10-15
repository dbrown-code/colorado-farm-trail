"""Website / Facebook / Instagram URL normalization used when building the map data."""
from __future__ import annotations

import re

_HANDLE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
# Scheme-less values that already start with one of these are URLs missing "https://".
_SOCIAL_DOMAINS = ("facebook.com/", "www.facebook.com/", "m.facebook.com/", "fb.com/",
                   "instagram.com/", "www.instagram.com/")
FACEBOOK_BASE = "https://facebook.com/"
INSTAGRAM_BASE = "https://instagram.com/"


def _has_scheme(v):
    vl = v.lower()
    return vl.startswith("http://") or vl.startswith("https://")


def _normalize_scheme(v):
    """Lowercase just the scheme (e.g. HTTPS://Foo -> https://Foo); host case is left alone."""
    for scheme in ("https://", "http://"):
        if v[:len(scheme)].lower() == scheme:
            return scheme + v[len(scheme):]
    return v


def website_url(value):
    """Normalize a website cell into a usable URL, or None.

    Most cells are bare domains missing the scheme (e.g. "bergharvest.com") --
    those become https://. Names, "none", or anything with spaces -> None.
    """
    v = (value or "").strip()
    if not v or v.lower() == "none":
        return None
    if _has_scheme(v):
        return _normalize_scheme(v)
    if any(c.isspace() for c in v) or "." not in v:
        return None  # a business name, not a domain
    return "https://" + v


def social_url(value, base):
    """Normalize a social field (full URL or bare @handle) into a URL, or None.

    Bare cells that are actually business names (spaces, "&", apostrophes) can't
    form a valid link and return None rather than a broken URL.
    """
    v = (value or "").strip()
    if not v:
        return None
    if any(c.isspace() for c in v):
        return None  # a business name, not a link
    if _has_scheme(v):
        return _normalize_scheme(v)
    # Scheme-less but already a social URL, e.g. "facebook.com/x", "www.instagram.com/x".
    if v.lower().startswith(_SOCIAL_DOMAINS):
        return "https://" + v
    # A bare handle, e.g. "@growinggardensboulder", "berg.harvest", "abundant.spaces".
    handle = v.lstrip("@").strip("/")
    if not handle or "/" in handle or not _HANDLE_RE.match(handle):
        return None
    return base + handle
