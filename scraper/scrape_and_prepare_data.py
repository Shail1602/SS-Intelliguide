# scraper/scrape_and_prepare_data.py

import hashlib
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.aptouring.com/en-au/trips"

def get_tour_id(name, url):
    return hashlib.md5((name + url).encode()).hexdigest()

def scrape_tours():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select(".trip-card")  # Update selector based on actual site
    tours = []

    for card in cards:
        title = card.select_one(".card-title")
        duration = card.select_one(".card-duration")
        link_tag = card.find("a", href=True)

        if title and link_tag:
            url = "https://www.aptouring.com" + link_tag['href']
            name = title.text.strip()
            tours.append({
                "TOUR_ID": get_tour_id(name, url),
                "TOUR_NAME": name,
                "DURATION": duration.text.strip() if duration else "N/A",
                "URL": url,
                "BROCHURE_URL": "",  # Placeholder
                "VALIDATED": "No",
                "SUMMARY": ""
            })

    df = pd.DataFrame(tours)
    df.to_csv("tours_scraped.csv", index=False)
    print("Tours scraped and saved to tours_scraped.csv")

if __name__ == "__main__":
    scrape_tours()
