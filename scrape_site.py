#!/usr/bin/env python3
"""
Multi-threaded crawler: Crawl a domain and dump page data to JSON.
Usage: python scrape_site.py https://example.com
"""

import json
import re
import sys
import threading
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configuration
MAX_WORKERS = 10       # Number of threads
MAX_PAGES = None       # Limit total pages
TIMEOUT = 15           # HTTP timeout

seen_urls = set()
seen_lock = threading.Lock()

def normalize_url(url, base, domain):
    url, _ = urldefrag(urljoin(base, url))
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None
    return url if parsed.netloc == domain else None

def visible_text(soup):
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    texts = [tag.get_text(strip=True, separator=" ") for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"])]
    return " ".join(t for t in texts if t)

def scrape_page(url, headers):
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
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

        return {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "description": meta_desc["content"].strip() if meta_desc else "",
            "text": text,
            "images": images,
            "files": files,
            "links": [normalize_url(a["href"], url, urlparse(url).netloc) for a in soup.find_all("a", href=True)]
        }
    except Exception as exc:
        print(f"[skip] {url} — {exc}", file=sys.stderr)
        return None

def crawl(start_url):
    domain = urlparse(start_url).netloc
    headers = {"User-Agent": f"{domain}-Crawler/1.0 (+https://github.com/your-repo)"}
    output_file = Path(f"{domain.replace('.', '_')}_content.json")

    pages = []
    stack = [start_url]
    pbar = tqdm(total=0, unit="page", desc="Crawled")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while stack:
            # Deduplicate stack entries
            with seen_lock:
                stack = [url for url in stack if url not in seen_urls]
                for url in stack:
                    seen_urls.add(url)

            if not stack:
                break

            # Limit how many URLs to process at once
            batch = stack[:MAX_WORKERS]
            stack = stack[MAX_WORKERS:]

            futures = {executor.submit(scrape_page, url, headers): url for url in batch}
            for future in as_completed(futures):
                result = future.result()
                if not result:
                    continue
                pages.append(result)
                pbar.update(1)

                for link in result["links"]:
                    if link:
                        with seen_lock:
                            if link not in seen_urls:
                                stack.append(link)

                if MAX_PAGES and len(pages) >= MAX_PAGES:
                    break

    # Save results
    for page in pages:
        page.pop("links", None)  # Remove raw link list from output
    output_file.write_text(json.dumps(pages, ensure_ascii=False, indent=2))
    pbar.close()
    print(f"\nDone. {len(pages)} pages saved to {output_file.resolve()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scrape_site.py https://example.com")
        sys.exit(1)
    crawl(sys.argv[1])
