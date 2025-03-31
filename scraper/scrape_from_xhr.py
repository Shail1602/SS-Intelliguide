# scraper/scrape_from_xhr.py

import hashlib
import json
import pandas as pd
from playwright.sync_api import sync_playwright

def get_tour_id(name, url):
    return hashlib.md5((name + url).encode()).hexdigest()

def scrape_from_xhr():
    tour_sections = [
        "https://www.aptouring.com/en-au/tours/europe",
        "https://www.aptouring.com/en-au/tours/australia",
        "https://www.aptouring.com/en-au/tours/new-zealand",
        "https://www.aptouring.com/en-au/tours/asia",
        "https://www.aptouring.com/en-au/tours/africa",
        "https://www.aptouring.com/en-au/tours/south-america",
        "https://www.aptouring.com/en-au/tours/north-america",
        "https://www.aptouring.com/en-au/tours/antarctica"
    ]

    all_tours = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):
            if "tripSearch" in response.url and response.status == 200:
                try:
                    json_data = response.json()
                    for tour in json_data.get("Trips", []):
                        name = tour.get("Title", "Unknown Tour")
                        url = f"https://www.aptouring.com{tour.get('Url', '')}"
                        all_tours.append({
                            "TOUR_ID": get_tour_id(name, url),
                            "TOUR_NAME": name,
                            "DURATION": tour.get("DurationText", "N/A"),
                            "URL": url,
                            "BROCHURE_URL": "",  # Will fill later if needed
                            "VALIDATED": "No",
                            "SUMMARY": ""
                        })
                except Exception as e:
                    print(f"Error parsing XHR data: {e}")

        page.on("response", handle_response)

        for section in tour_sections:
            print(f"Scraping from {section}...")
            page.goto(section, timeout=60000)
            page.wait_for_timeout(8000)

        browser.close()

    df = pd.DataFrame(all_tours).drop_duplicates(subset="TOUR_ID")
    df.to_csv("tours_scraped.csv", index=False)
    print(f"✅ Extracted {len(df)} tours from XHR responses. Saved to tours_scraped.csv")

if __name__ == "__main__":
    scrape_from_xhr()
