#!/usr/bin/env python3
"""
Crawl a website and dump all page data to JSON.
Run:  python scrape_site.py https://example.com
"""

import json
import re
import sys
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
OUTPUT_FILE = Path("site_content.json")
HEADERS = {"User-Agent": "WebsiteScraper/1.0 (+https://github.com/your-repo)"}
MAX_PAGES = None
TIMEOUT = 15  # seconds

# ----------------------------------------------------------------------------

def normalize_url(url, base, domain):
    url, _ = urldefrag(urljoin(base, url))  # drop #fragment, make absolute
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or parsed.netloc != domain:
        return None
    # Normalize paths like /index.html
    norm_path = re.sub(r"/index\.html?$", "/", parsed.path).rstrip("/")
    normalized = parsed._replace(path=norm_path)
    return normalized.geturl()


def visible_text(html: BeautifulSoup):
    for tag in html(["script", "style", "noscript", "template"]):
        tag.decompose()
    texts = []
    for tag in html.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = tag.get_text(strip=True, separator=" ")
        if text:
            texts.append(text)
    return " ".join(texts)


def scrape_page(url, domain):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        meta_desc = soup.find("meta", attrs={"name": "description"})
        images = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]
        files = [
            urljoin(url, a["href"])
            for a in soup.find_all("a", href=True)
            if re.search(r"\.(pdf|zip|xlsx?|docx?|png|jpe?g|svg)$", a["href"], re.I)
        ]
        text = visible_text(soup)

        page_data = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "description": meta_desc["content"].strip() if meta_desc else "",
            "text": text,
            "images": images,
            "files": files,
        }

        # Also return soup for link discovery
        return page_data, soup

    except Exception as e:
        print(f"[skip] {url} — {e}", file=sys.stderr)
        return None, None


def crawl(start_url):
    parsed_start = urlparse(start_url)
    domain = parsed_start.netloc
    seen_urls = set()
    seen_hashes = set()
    stack = [start_url]
    pages = []

    pbar = tqdm(total=0, unit="page", desc="Crawled")

    while stack:
        url = stack.pop()
        if url in seen_urls:
            continue

        page_data, soup = scrape_page(url, domain)
        seen_urls.add(url)

        if not page_data or not soup:
            continue

        content_hash = hashlib.sha256(page_data["text"].encode("utf-8")).hexdigest()
        if content_hash in seen_hashes:
            continue
        seen_hashes.add(content_hash)

        pages.append(page_data)
        pbar.update(1)

        for a in soup.find_all("a", href=True):
            nxt = normalize_url(a["href"], url, domain)
            if nxt and nxt not in seen_urls:
                stack.append(nxt)

        if MAX_PAGES and len(pages) >= MAX_PAGES:
            break

    OUTPUT_FILE.write_text(json.dumps(pages, ensure_ascii=False, indent=2))
    pbar.close()
    print(f"\nDone. {len(pages)} pages saved to {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrape_site.py https://example.com", file=sys.stderr)
        sys.exit(1)
    crawl(sys.argv[1])
