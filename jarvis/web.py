from __future__ import annotations
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


def fetch_public(url: str, timeout: int = 30, max_chars: int = 140000) -> str:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        raise ValueError("Only HTTP/HTTPS URLs are supported.")
    r = requests.get(url, timeout=int(timeout), headers={"User-Agent": "JARVIS-V4-research/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())[:int(max_chars)]
