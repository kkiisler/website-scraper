Great! Here’s the updated README.md tailored for your repo website-scraper:

⸻


# 🕸️ Website Scraper

**website-scraper** is a multi-threaded Python crawler that recursively scans a single domain, extracting visible text, page metadata, images, and downloadable files. Results are saved in a clean JSON format.

---

## 🚀 Features

- 🔄 Multi-threaded crawling using `ThreadPoolExecutor`
- 🌐 Stays within the target domain
- 🧠 Extracts:
  - Page title & meta description
  - Visible text content (`h1–h6`, `p`, `li`)
  - Image URLs (`<img src=...>`)
  - File links (e.g., `.pdf`, `.zip`, `.docx`)
- ✅ Deduplicates visited URLs
- 📁 Outputs to a single `.json` file per domain

---

## 🛠️ Setup

### 1. Install Python (3.9+)

```bash
python3 --version

2. Clone the repository

git clone https://github.com/your-username/website-scraper.git
cd website-scraper

3. (Optional but recommended) Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate     # macOS/Linux
# OR
.venv\Scripts\activate.bat    # Windows

4. Install dependencies

pip install -r requirements.txt

If you don’t have requirements.txt, install manually:

pip install requests beautifulsoup4 tqdm


⸻

▶️ Usage

Crawl a website:

python scrape_site.py https://example.com

This will crawl all internal pages on example.com and save the output to:

example_com_content.json

Example:

python scrape_site.py https://pilvio.com


⸻

🧾 Output Format

[
  {
    "url": "https://example.com/page",
    "title": "Welcome to Example",
    "description": "Example description",
    "text": "Visible text content from the page...",
    "images": [
      "https://example.com/assets/logo.png"
    ],
    "files": [
      "https://example.com/files/brochure.pdf"
    ]
  },
  ...
]


⸻

🔧 Configuration

Edit the following values in scrape_site.py if needed:
	•	MAX_WORKERS = 10 → Number of threads
	•	MAX_PAGES = None → Limit the number of pages (e.g. 200)
	•	TIMEOUT = 15 → HTTP timeout in seconds

⸻

🧹 Cleanup

To deactivate your virtual environment:

deactivate

To remove it:

rm -rf .venv


⸻

📄 License

MIT License © 2025 Kaur Kiisler

⸻

🧠 Notes
	•	This tool does not obey robots.txt
	•	Use responsibly on public websites
	•	Consider adding robots.txt respect if you plan to share or deploy publicly

