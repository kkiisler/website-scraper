# website-scraper

Here’s a detailed README.md for your multi-threaded Python website crawler, including full setup instructions, usage, optional virtual environment, and output details.

⸻


# 🕸️ Multi-Threaded Website Crawler (Python 3)

This is a multi-threaded web crawler that recursively scrapes all accessible pages from a given domain, extracting page metadata, visible text content, image links, and downloadable file URLs.

Output is saved as a structured JSON file.

---

## 📦 Features

- Multi-threaded crawling using `ThreadPoolExecutor`
- Domain-restricted recursive crawling
- Extracts:
  - Page title
  - Meta description
  - Visible text (`h1–h6`, `p`, `li`)
  - All image URLs
  - All downloadable file URLs (e.g., PDF, DOCX, ZIP)
- Deduplicates visited URLs
- Saves all data in `example_com_content.json`

---

## 🛠️ Setup

### 1. Install Python 3.9 or newer

Make sure Python is installed:

```bash
python3 --version

2. Clone or download the script

git clone https://github.com/yourname/multi-threaded-crawler.git
cd multi-threaded-crawler

Or just save the script as scrape_site.py.

3. (Optional but recommended) Use a virtual environment

python3 -m venv .venv
source .venv/bin/activate      # on Linux/macOS
# OR
.venv\Scripts\activate.bat     # on Windows

4. Install required packages

pip install -r requirements.txt

If you don’t have requirements.txt, install directly:

pip install requests beautifulsoup4 tqdm


⸻

▶️ Usage

Basic usage

python scrape_site.py https://example.com

Example:

python scrape_site.py https://pilvio.com

Optional: Cap the number of pages

You can modify the MAX_PAGES = ... value in the script if you want to limit crawl depth.

⸻

🧪 Output
	•	Creates a file like: example_com_content.json
	•	JSON format:

[
  {
    "url": "https://example.com/page",
    "title": "Example Page",
    "description": "Short meta description",
    "text": "All visible text content...",
    "images": [
      "https://example.com/images/logo.png",
      ...
    ],
    "files": [
      "https://example.com/files/menu.pdf",
      ...
    ]
  },
  ...
]


⸻

🧹 Clean up

To deactivate the virtual environment:

deactivate

To delete .venv:

rm -rf .venv


⸻

🧱 Requirements
	•	Python ≥ 3.9
	•	Packages:
	•	requests
	•	beautifulsoup4
	•	tqdm

⸻

📖 License

MIT License © 2025 Your Name

---

Let me know if you'd like me to package this into a `.zip` along with the `.py` script and `requirements.txt`.
