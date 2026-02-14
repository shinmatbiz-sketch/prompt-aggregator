#!/usr/bin/env python3
"""
Prompt Aggregator Crawler
=========================
Crawls prompt pages from nanyo-city.jpn.org/prompt/ (001.html ~ 999.html)
and outputs structured JSON data.

Features:
  - Resumable: tracks progress in progress.log
  - Polite: 1.0s sleep between requests
  - Robust: handles 404, timeouts, and errors gracefully
"""

import json
import io
import os
import sys
import time
import logging
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Fix Windows console encoding
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "https://nanyo-city.jpn.org/prompt/"
START_ID = 1
END_ID = 999
SLEEP_SECONDS = 1.0
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_FILE = DATA_DIR / "prompts.json"
PROGRESS_FILE = SCRIPT_DIR / "progress.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler(SCRIPT_DIR / "crawler.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[console_handler, file_handler],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Progress tracking (resume support)
# ---------------------------------------------------------------------------

def load_progress() -> set[str]:
    """Load set of already-crawled IDs from progress log."""
    if not PROGRESS_FILE.exists():
        return set()
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def save_progress(prompt_id: str) -> None:
    """Append a crawled ID to the progress log."""
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{prompt_id}\n")

# ---------------------------------------------------------------------------
# Existing data management
# ---------------------------------------------------------------------------

def load_existing_data() -> list[dict]:
    """Load previously saved prompts so we can append incrementally."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Corrupted prompts.json – starting fresh.")
                return []
    return []


def save_data(prompts: list[dict]) -> None:
    """Persist prompt list to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------------
# HTML Parsing
# ---------------------------------------------------------------------------

def parse_page(html: str, prompt_id: str) -> dict | None:
    """
    Extract structured prompt data from raw HTML.

    Returns dict with keys: id, title, body, url
    or None if the page doesn't contain a valid prompt.
    """
    soup = BeautifulSoup(html, "html.parser")

    # --- Title ---
    # Pages use .box-title (first one) or <title> tag, not <h1>
    title_el = soup.select_one(".box-title")
    if not title_el:
        title_el = soup.find("title")
    if not title_el:
        title_el = soup.find("h1")
    if not title_el:
        logger.warning(f"[{prompt_id}] No title found - skipping.")
        return None

    raw_title = title_el.get_text(strip=True)
    title = raw_title

    # --- Body: extract content from .box-bun sections ---
    sections: list[str] = []
    boxes = soup.select(".box-bun")

    if boxes:
        for box in boxes:
            # Get section heading from <h2> inside the box
            heading_el = box.find("h2")
            section_title = heading_el.get_text(strip=True) if heading_el else ""

            # Collect content from direct children:
            # - Text nodes (direct text)
            # - <textarea> default values (these contain the prompt template)
            # - <label> text
            # - Skip: <h2> (captured above), <input>, <select>, <button>, <script>
            content_parts: list[str] = []
            for child in box.children:
                if not hasattr(child, 'name'):
                    # NavigableString (text node)
                    text = str(child).strip()
                    if text:
                        content_parts.append(text)
                    continue

                if child.name == 'h2':
                    continue
                if child.name in ('script', 'style', 'button', 'input', 'select'):
                    continue
                if child.name == 'div' and 'box-title' in (child.get('class') or []):
                    continue

                if child.name == 'textarea':
                    # Textarea default values contain the actual prompt content
                    val = child.get_text(strip=True)
                    if val:
                        content_parts.append(val)
                elif child.name == 'label':
                    val = child.get_text(strip=True)
                    if val:
                        content_parts.append(val)
                elif child.name == 'br':
                    continue
                else:
                    val = child.get_text(strip=True)
                    if val:
                        content_parts.append(val)

            content = "\n".join(content_parts)
            if section_title and content:
                sections.append(f"[{section_title}]\n{content}")
            elif section_title:
                sections.append(f"[{section_title}]")
            elif content:
                sections.append(content)
    else:
        # Fallback: extract all text from .form-content
        form_content = soup.select_one(".form-content")
        if form_content:
            # Remove script, style, input, textarea, select, button
            for tag in form_content.find_all(['script', 'style', 'input', 'textarea', 'select', 'button']):
                tag.decompose()
            sections.append(form_content.get_text(separator="\n", strip=True))
        else:
            # Last resort: body text
            body_text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
            if not body_text:
                logger.warning(f"[{prompt_id}] No extractable content - skipping.")
                return None
            sections.append(body_text)

    body = "\n\n".join(sections)

    if not body or len(body) < 10:
        logger.warning(f"[{prompt_id}] Body too short ({len(body)} chars) - skipping.")
        return None

    url = f"{BASE_URL}{prompt_id}.html"

    return {
        "id": prompt_id,
        "title": title,
        "body": body,
        "url": url,
    }

# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch_page(prompt_id: str) -> str | None:
    """Fetch a single prompt page. Returns HTML string or None on failure."""
    url = f"{BASE_URL}{prompt_id}.html"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent": "PromptAggregator/1.0 (educational project)",
                    "Accept": "text/html",
                    "Accept-Language": "ja,en;q=0.9",
                },
            )

            if resp.status_code == 404:
                logger.info(f"[{prompt_id}] 404 Not Found - skipping.")
                return None

            if resp.status_code != 200:
                logger.warning(
                    f"[{prompt_id}] HTTP {resp.status_code} (attempt {attempt}/{MAX_RETRIES})"
                )
                if attempt < MAX_RETRIES:
                    time.sleep(2)
                    continue
                return None

            # Force UTF-8: pages declare <meta charset="UTF-8">
            resp.encoding = "utf-8"
            return resp.text

        except requests.exceptions.Timeout:
            logger.warning(f"[{prompt_id}] Timeout (attempt {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            logger.error(f"[{prompt_id}] Request error: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2)

    return None

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("=" * 60)
    logger.info("Prompt Aggregator Crawler – Starting")
    logger.info(f"Range: {START_ID:03d} ~ {END_ID:03d}")
    logger.info("=" * 60)

    done = load_progress()
    prompts = load_existing_data()
    existing_ids = {p["id"] for p in prompts}

    total = END_ID - START_ID + 1
    skipped = 0
    fetched = 0
    errors = 0

    for i in range(START_ID, END_ID + 1):
        prompt_id = f"{i:03d}"

        if prompt_id in done:
            skipped += 1
            continue

        logger.info(f"[{prompt_id}] Fetching... ({i}/{total})")

        html = fetch_page(prompt_id)

        if html is None:
            errors += 1
            save_progress(prompt_id)  # Mark as processed to skip on resume
            time.sleep(SLEEP_SECONDS)
            continue

        result = parse_page(html, prompt_id)

        if result and result["id"] not in existing_ids:
            prompts.append(result)
            existing_ids.add(result["id"])
            fetched += 1

        save_progress(prompt_id)

        # Save incrementally every 50 pages
        if fetched > 0 and fetched % 50 == 0:
            save_data(prompts)
            logger.info(f"  >> Checkpoint saved ({len(prompts)} total prompts)")

        time.sleep(SLEEP_SECONDS)

    # Final save
    # Sort by ID
    prompts.sort(key=lambda p: p["id"])
    save_data(prompts)

    logger.info("=" * 60)
    logger.info("Crawl complete!")
    logger.info(f"  Total processed : {total}")
    logger.info(f"  Skipped (resume): {skipped}")
    logger.info(f"  Fetched          : {fetched}")
    logger.info(f"  Errors/404       : {errors}")
    logger.info(f"  Total in JSON    : {len(prompts)}")
    logger.info(f"  Output           : {OUTPUT_FILE}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
