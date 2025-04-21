# NOT NEEDED, A BIG MISTAKE
import requests
from bs4 import BeautifulSoup
import time
import json

BASE_URL = "https://www.alta.ru"
RAILWAY_LIST_URL = f"{BASE_URL}/railway/"

import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    # add more if needed
]

"""
PROXIES = [
    "https://217.23.15.50:14917",
]

def get_random_proxy():
    return {
        "http": random.choice(PROXIES),
        "https": random.choice(PROXIES),
    }
"""

def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def safe_request(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=get_random_headers(), timeout=10)
            if random.uniform(0, 1) > 0.85:
                time.sleep(4)
            if res.status_code == 200:
                time.sleep(1 + random.uniform(0,0.5))
                return res
            elif res.status_code in (429, 403):
                wait = 2 ** attempt + random.uniform(1, 3)
                print(f"Rate limited. Sleeping for {wait:.1f}s...")
                time.sleep(wait)
            else:
                print(f"Error {res.status_code} on {url}")
                return None
        except requests.RequestException as e:
            print(f"Request error ({type(e).__name__}) on {url}. Retrying...")
            time.sleep(2 ** attempt + random.uniform(1, 4))
    return None


def get_russian_railway_links():
    res = safe_request(RAILWAY_LIST_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    railway_links = []

    russia_div = soup.find("div", class_="h3", string="Россия")
    if not russia_div:
        raise Exception("Couldn't find Россия section.")

    # Grab all <div>s until the next <div class="h3">
    current = russia_div.find_next_sibling()
    while current and (not current.has_attr("class") or "h3" not in current["class"]):
        a_tag = current.find("a", class_="pRailway_item")
        if a_tag and a_tag["href"].startswith("/railway/"):
            full_url = BASE_URL + a_tag["href"]
            railway_links.append(full_url)
        current = current.find_next_sibling()

    return railway_links

def get_station_links(railway_url):
    res = safe_request(railway_url)
    soup = BeautifulSoup(res.text, "html.parser")

    station_links = []
    for a in soup.find_all("a", class_="pRailway_item mFastSearch_key", href=True):
        if a["href"].startswith("/railway/station/"):
            station_links.append(BASE_URL + a["href"])
    return station_links

def get_station_coords(station_url):
    res = safe_request(station_url)
    soup = BeautifulSoup(res.text, "html.parser")

    coords = {}

    # Grab all right-side columns (could be multiple)
    coord_blocks = soup.find_all("div", class_="pRailway_column pRailway_column-right")
    
    for block in coord_blocks:
        divs = block.find_all("div", class_="dib")
        for div in divs:
            label = div.find("strong")
            if label and label.text.strip() == "Широта:":
                parts = div.contents
                # Find text after <br> tag
                for i, item in enumerate(parts):
                    if item.name == "br" and i + 1 < len(parts):
                        coords['latitude'] = parts[i + 1].strip()
            elif label and label.text.strip() == "Долгота:":
                parts = div.contents
                for i, item in enumerate(parts):
                    if item.name == "br" and i + 1 < len(parts):
                        coords['longitude'] = parts[i + 1].strip()

    return coords if 'latitude' in coords and 'longitude' in coords else None

import os

SAVE_PATH = "station_coords.json"

def load_existing_coords():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_coords(coords):
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(coords, f, ensure_ascii=False, indent=2)

def main():
    all_coords = load_existing_coords()
    processed_ids = set(all_coords.keys())

    railway_links = get_russian_railway_links()
    print(f"Found {len(railway_links)} Russian railways")

    for railway_url in railway_links:
        print(f"\nProcessing railway: {railway_url}")
        station_links = get_station_links(railway_url)
        print(f"  Found {len(station_links)} stations")

        for i, station_url in enumerate(station_links):
            station_id = station_url.rstrip("/").split("/")[-1]
            if station_id in processed_ids:
                print(f"    Skipping already processed station {station_id}")
                continue

            try:
                coords = get_station_coords(station_url)
                if coords:
                    all_coords[station_id] = coords
                    processed_ids.add(station_id)
                    print(f"    {station_id}: {coords}")
                else:
                    print(f"    {station_id}: No coordinates found")

                # Save every 10 stations
                if i % 10 == 0:
                    save_coords(all_coords)

                #time.sleep(random.uniform(1, 4))  # Stay human-like
            except Exception as e:
                print(f"    Error fetching {station_url}: {e}")
                time.sleep(random.uniform(5, 10))  # Longer pause on error

    # Final save
    save_coords(all_coords)
    print("Finished and saved all data.")

if __name__ == "__main__":
    main()
