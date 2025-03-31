# scraper/scrape_and_prepare_data.py

import hashlib
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError
import time

def get_tour_id(name, url):
    return hashlib.md5((name + url).encode()).hexdigest()

def extract_brochure_url(page, tour_url):
    try:
        page.goto(tour_url, timeout=60000)
        page.wait_for_timeout(2000)
        links = page.query_selector_all("a[href$='.pdf']")
        for link in links:
            href = link.get_attribute("href")
            if href:
                return href if href.startswith("http") else f"https://www.aptouring.com{href}"
    except Exception as e:
        print(f"⚠️ Could not extract brochure from {tour_url}: {e}")
    return ""

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
        detail_page = browser.new_page()

        for section in tour_sections:
            print(f"Scraping {section}...")
            page.goto(section, timeout=60000)
            try:
                page.wait_for_selector("a.card--tour", timeout=10000)
            except TimeoutError:
                print(f"⚠️ No tour cards found on {section} within timeout.")
                continue

            cards = page.query_selector_all("a.card--tour")
            if not cards:
                print(f"⚠️ No tour cards found after load on {section}")
                continue

            for card in cards:
                try:
                    url_suffix = card.get_attribute("href")
                    tour_url = f"https://www.aptouring.com{url_suffix}"
                    title_elem = card.query_selector("h3.card--tour__title")
                    title = title_elem.inner_text().strip() if title_elem else "Unknown"
                    brochure_url = extract_brochure_url(detail_page, tour_url)

                    all_tours.append({
                        "TOUR_ID": get_tour_id(title, tour_url),
                        "TOUR_NAME": title,
                        "DURATION": "N/A",
                        "URL": tour_url,
                        "BROCHURE_URL": brochure_url,
                        "VALIDATED": "No",
                        "SUMMARY": ""
                    })
                except Exception as e:
                    print(f"Error parsing tour: {e}")

            time.sleep(1)

        browser.close()

    df = pd.DataFrame(all_tours).drop_duplicates(subset="TOUR_ID")
    df.to_csv("tours_scraped.csv", index=False)
    print(f"✅ Scraped {len(df)} unique tours. Saved to tours_scraped.csv")

if __name__ == "__main__":
    scrape_tours()
