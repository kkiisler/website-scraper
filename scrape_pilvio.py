#!/usr/bin/env python3
"""
Crawl pilvio.com (or any single domain) and dump all page data to JSON.
Run:  python scrape_pilvio.py
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

START_URL      = "https://pilvio.com/"
OUTPUT_FILE    = Path("pilvio_site_content.json")
DOMAIN         = urlparse(START_URL).netloc
HEADERS        = {"User-Agent": "PilvioCrawler/1.0 (+https://github.com/your-repo)"}  # polite UA
MAX_PAGES      = None       # set to integer to cap crawl (e.g., 200)
TIMEOUT        = 15         # seconds for HTTP requests

# ---------------------------------------------------------------------------

def normalize_url(url, base):
    url, _ = urldefrag(urljoin(base, url))     # drop #fragment, make absolute
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    return url if parsed.netloc == DOMAIN else None   # stay on pilvio.com

def visible_text(html: BeautifulSoup):
    # Remove script/style/noscript and hidden elements
    for tag in html(["script", "style", "noscript", "template"]):
        tag.decompose()
    texts = []
    for tag in html.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = tag.get_text(strip=True, separator=" ")
        if text:
            texts.append(text)
    return " ".join(texts)

def scrape_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup  = BeautifulSoup(resp.text, "html.parser")

    meta_desc = soup.find("meta", attrs={"name": "description"})
    images    = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]
    files     = [
        urljoin(url, a["href"])
        for a in soup.find_all("a", href=True)
        if re.search(r"\.(pdf|zip|xlsx?|docx?|png|jpe?g|svg)$", a["href"], re.I)
    ]
    text      = visible_text(soup)

    return {
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "description": meta_desc["content"].strip() if meta_desc else "",
        "text": text,
        "images": images,
        "files": files,
    }, soup

def crawl(start_url=START_URL):
    seen, stack, pages = set(), [start_url], []
    pbar = tqdm(total=0, unit="page", desc="Crawled")

    while stack:
        url = stack.pop()
        if url in seen:
            continue
        try:
            page_data, soup = scrape_page(url)
        except Exception as exc:
            print(f"[skip] {url} — {exc}", file=sys.stderr)
            seen.add(url)
            continue

        pages.append(page_data)
        pbar.update(1)
        seen.add(url)

        # enqueue new links
        for a in soup.find_all("a", href=True):
            nxt = normalize_url(a["href"], url)
            if nxt and nxt not in seen:
                stack.append(nxt)

        if MAX_PAGES and len(pages) >= MAX_PAGES:
            break

    OUTPUT_FILE.write_text(json.dumps(pages, ensure_ascii=False, indent=2))
    pbar.close()
    print(f"\nDone. {len(pages)} pages saved to {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    crawl()
