from __future__ import annotations
import time
from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


class PublicWebCrawler:
    """Small, auditable public-web crawler.

    It only requests http/https pages, checks robots.txt, stays on an allowlisted
    host by default, throttles requests, and never handles credentials/cookies.
    """

    def __init__(self, timeout: int = 20, delay: float = 1.0, max_chars: int = 100_000):
        self.timeout = int(timeout)
        self.delay = max(0.0, float(delay))
        self.max_chars = int(max_chars)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "JARVIS-V4-public-research-crawler/1.0"})
        self._robots: dict[str, RobotFileParser | None] = {}

    def _robot_ok(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            rp = RobotFileParser()
            rp.set_url(origin + "/robots.txt")
            try:
                rp.read()
                self._robots[origin] = rp
            except Exception:
                # If robots.txt cannot be read, do not treat that as permission to
                # crawl broadly. The caller can opt into this page manually through
                # the single-URL ingest command; automatic crawling remains conservative.
                self._robots[origin] = None
        rp = self._robots[origin]
        if rp is None:
            return False
        return rp.can_fetch(self.session.headers["User-Agent"], url)

    @staticmethod
    def _normalize(base: str, href: str) -> str | None:
        if not href:
            return None
        u = urldefrag(urljoin(base, href))[0].strip()
        p = urlparse(u)
        if p.scheme not in ("http", "https") or not p.netloc:
            return None
        return u

    def fetch(self, url: str) -> tuple[str, list[str]]:
        if urlparse(url).scheme not in ("http", "https"):
            raise ValueError("Only HTTP/HTTPS URLs are allowed.")
        if not self._robot_ok(url):
            raise PermissionError(f"robots.txt disallows or is unavailable for automatic crawl: {url}")
        r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "").lower()
        if "text/html" not in content_type and "text/plain" not in content_type:
            return "", []
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "canvas", "template"]):
            tag.decompose()
        text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
        links = []
        if "text/html" in content_type:
            for a in soup.find_all("a", href=True):
                u = self._normalize(url, a.get("href"))
                if u:
                    links.append(u)
        return text[: self.max_chars], links

    def crawl(self, seeds: list[str], max_pages: int = 20, max_depth: int = 2, same_host: bool = True):
        queue = deque((u, 0) for u in seeds)
        seen: set[str] = set()
        out = []
        seed_hosts = {urlparse(u).netloc for u in seeds if urlparse(u).netloc}
        while queue and len(out) < int(max_pages):
            url, depth = queue.popleft()
            if url in seen or depth > int(max_depth):
                continue
            seen.add(url)
            try:
                text, links = self.fetch(url)
                if text.strip():
                    out.append({"url": url, "depth": depth, "text": text})
                if depth < int(max_depth):
                    for nxt in links:
                        if same_host and urlparse(nxt).netloc not in seed_hosts:
                            continue
                        if nxt not in seen:
                            queue.append((nxt, depth + 1))
            except Exception as exc:
                out.append({"url": url, "depth": depth, "text": "", "error": repr(exc)})
            if queue:
                time.sleep(self.delay)
        return out
