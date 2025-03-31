# scraper/scrape_and_prepare_data.py

import hashlib
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError
import time

def get_tour_id(name, url):
    return hashlib.md5((name + url).encode()).hexdigest()

def scrape_tours():
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
        page = browser.new_page()

        for section in tour_sections:
            print(f"Scraping {section}...")
            page.goto(section, timeout=60000)
            try:
                page.wait_for_selector(".trip-card", timeout=10000)
            except TimeoutError:
                print(f"⚠️ No tour cards found on {section} within timeout.")
                continue

            cards = page.query_selector_all(".trip-card")

            if not cards:
                print(f"⚠️ No trip cards found after load on {section}")
                continue

            for card in cards:
                try:
                    title_elem = card.query_selector(".card-title")
                    duration_elem = card.query_selector(".card-duration")
                    link_elem = card.query_selector("a")

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.inner_text().strip()
                    duration = duration_elem.inner_text().strip() if duration_elem else "N/A"
                    link = link_elem.get_attribute("href")
                    full_link = f"https://www.aptouring.com{link}" if link.startswith("/") else link

                    all_tours.append({
                        "TOUR_ID": get_tour_id(title, full_link),
                        "TOUR_NAME": title,
                        "DURATION": duration,
                        "URL": full_link,
                        "BROCHURE_URL": "",
                        "VALIDATED": "No",
                        "SUMMARY": ""
                    })
                except Exception as e:
                    print(f"Error parsing card: {e}")

            time.sleep(2)

        browser.close()

    df = pd.DataFrame(all_tours).drop_duplicates(subset="TOUR_ID")
    df.to_csv("tours_scraped.csv", index=False)
    print(f"✅ Scraped {len(df)} unique tours. Saved to tours_scraped.csv")

if __name__ == "__main__":
    scrape_tours()
