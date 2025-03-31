import streamlit as st
import snowflake.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
import hashlib
import time

MODELS = ["mistral-large2", "llama3.1-70b", "llama3.1-8b"]
st.set_page_config(page_title="SS Intelliguide", layout="wide")
st.title("SS Intelliguide – AI-Powered Travel Intelligence")

model_choice = st.selectbox("Choose your LLM model:", MODELS)

connection_parameters = {
    "user": st.secrets["snowflake"]["user"],
    "password": st.secrets["snowflake"]["password"],
    "account": st.secrets["snowflake"]["account"],
    "warehouse": st.secrets["snowflake"]["warehouse"],
    "database": st.secrets["snowflake"]["database"],
    "schema": st.secrets["snowflake"]["schema"],
    "role": st.secrets["snowflake"].get("role", "ACCOUNTADMIN")
}

def call_llm(prompt, model):
    conn = snowflake.connector.connect(**connection_parameters)
    cur = conn.cursor()
    cur.execute(f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', OBJECT_CONSTRUCT('prompt', %s))", (prompt,))
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result

def get_tours():
    conn = snowflake.connector.connect(**connection_parameters)
    cur = conn.cursor()
    cur.execute("SELECT TOUR_ID, TOUR_NAME, DURATION, URL, VALIDATED FROM TOUR_PRODUCTS")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(data, columns=["TOUR_ID", "TOUR_NAME", "DURATION", "URL", "VALIDATED"])

def get_tour_id(name, url):
    return hashlib.md5((name + url).encode()).hexdigest()

def scrape_and_prepare_data():
    base_url = "https://www.aptouring.com"
    tour_pages = [
        "/en-au/tours/europe", "/en-au/tours/australia", "/en-au/tours/new-zealand",
        "/en-au/tours/asia", "/en-au/tours/africa", "/en-au/tours/south-america",
        "/en-au/tours/antarctica", "/en-au/tours/north-america"
    ]

    tours = []
    for path in tour_pages:
        full_url = base_url + path
        st.write(f"Scraping: {full_url}")
        try:
            response = requests.get(full_url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link["href"]
                text = link.get_text(strip=True)
                if "/en-au/trips/" in href and text:
                    full_link = base_url + href
                    tours.append({
                        "TOUR_ID": get_tour_id(text, full_link),
                        "TOUR_NAME": text,
                        "DURATION": "Unknown",
                        "URL": full_link,
                        "BROCHURE_URL": "",
                        "VALIDATED": "No",
                        "SUMMARY": ""
                    })
            time.sleep(1)  # Be nice to the server
        except Exception as e:
            st.error(f"Error scraping {full_url}: {e}")

    df = pd.DataFrame(tours).drop_duplicates(subset="TOUR_ID")
    return df

def load_to_snowflake(df):
    conn = snowflake.connector.connect(**connection_parameters)
    cursor = conn.cursor()
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO TOUR_PRODUCTS (
                    TOUR_ID, TOUR_NAME, DURATION, URL, BROCHURE_URL, VALIDATED, SUMMARY
                )
                SELECT %s, %s, %s, %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM TOUR_PRODUCTS WHERE TOUR_ID = %s
                )
            """, (
                row["TOUR_ID"], row["TOUR_NAME"], row["DURATION"], row["URL"],
                row["BROCHURE_URL"], row["VALIDATED"], row["SUMMARY"],
                row["TOUR_ID"]
            ))
        except Exception as e:
            st.error(f"Error inserting row: {e}")
    conn.commit()
    cursor.close()
    conn.close()

# Admin Panel
st.subheader("⚙️ Admin Panel")
if st.button("🔄 Scrape & Load Tour Data"):
    scraped_df = scrape_and_prepare_data()
    st.write("Scraped Tours Preview", scraped_df.head(10))
    if scraped_df.empty:
        st.warning("⚠️ No tours found. Check HTML structure or URLs.")
    else:
        load_to_snowflake(scraped_df)
        st.success("✅ Tours scraped and loaded into Snowflake!")

# Display Data
df = get_tours()
st.dataframe(df)

# Summarization Section
st.subheader("Summarize All Tours")
if st.button("Generate Summary"):
    prompt = "Summarize all APT tours in 3 bullet points per tour."
    summary = call_llm(prompt, model_choice)
    st.write(summary)

# Chat Section
st.subheader("Ask a question about the brochures")
user_q = st.text_input("Enter your question:")
if user_q:
    answer = call_llm(user_q, model_choice)
    st.success(answer)
