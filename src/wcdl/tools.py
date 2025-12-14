import random
import uuid
import rich
import requests
import time
from typing import List
from click import BadParameter

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8",
    "en;q=0.7",
]

def success(msg):
    rich.print(f"[green bold] [SUCCESS] {msg} [/green bold]")

def warn(msg):
    rich.print(f"[yellow bold] [WARNING] {msg} [/yellow bold]")

def error(msg):
    rich.print(f"[red bold] [ERROR] {msg} [/red bold]")

def notic(msg):
    rich.print(f"[blue bold] [NOTIC] {msg} [/blue bold]")
    
def random_headers(req_url):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        # "Accept-Encoding": "gzip, deflate, br",
        'HX-Request': 'true',
        'HX-Trigger': 'advanced-search-form',
        'HX-Target': 'search-results',
        'HX-Current-URL': req_url,
        "Referer": req_url,
        'Sec-GPC': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        "Connection": "keep-alive",
        "X-Request-ID": str(uuid.uuid4()),
    }

def safe_request(url: str, params:dict=None, headers:dict=None, retries:int=5, timeout:int=15) -> None|requests.Response:
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r
            else:
                warn(f"HTTP {r.status_code} on {url}")
        except requests.exceptions.RequestException as e:
            warn(f" Network error: {e}")

        sleep_time = 2 ** attempt
        print(f"Retrying in {sleep_time}s...")
        time.sleep(sleep_time)

    error(f"Failed all retries for URL: {url}")
    return None

def parse_range_args(range_str: str) -> List[int]:
    """
    Parse range arguments like "1", "1-5", "1,3,5" into a list of chapter numbers.
    
    Args:
        range_str: Range string (e.g., "1", "1-5", "1,3,5-7")
    
    Returns:
        List of chapter numbers to download
    """
    chapters = []
    
    # Handle comma-separated values
    for part in range_str.split(","):
        part = part.strip()
        
        # Check if it's a range (e.g., "1-5")
        if "-" in part:
            try:
                start, end = part.split("-")
                start, end = int(start.strip()), int(end.strip())
                chapters.extend(range(start, end + 1))
            except (ValueError, AttributeError):
                error(f"Invalid range format: {part}")
                raise BadParameter(f"Invalid range format: {part}")
        else:
            try:
                chapters.append(int(part))
            except ValueError:
                error(f"Invalid chapter number: {part}")
                raise BadParameter(f"Invalid chapter number: {part}")
    
    # Remove duplicates and sort
    return sorted(list(set(chapters)))