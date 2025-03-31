import streamlit as st
import snowflake.connector
import pandas as pd
import requests
from bs4 import BeautifulSoup
import hashlib

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
    BASE_URL = "https://www.aptouring.com/en-au/trips"
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select(".trip-card")
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
                "BROCHURE_URL": "",
                "VALIDATED": "No",
                "SUMMARY": ""
            })

    return pd.DataFrame(tours)

def load_to_snowflake(df):
    conn = snowflake.connector.connect(**connection_parameters)
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO TOUR_PRODUCTS (
                TOUR_ID, TOUR_NAME, DURATION, URL, BROCHURE_URL, VALIDATED, SUMMARY
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (TOUR_ID) DO NOTHING
        """, (
            row["TOUR_ID"], row["TOUR_NAME"], row["DURATION"], row["URL"],
            row["BROCHURE_URL"], row["VALIDATED"], row["SUMMARY"]
        ))
    conn.commit()
    cursor.close()
    conn.close()

# Admin Panel
st.subheader("⚙️ Admin Panel")
if st.button("🔄 Scrape & Load Tour Data"):
    scraped_df = scrape_and_prepare_data()
    st.write("Scraped Tours Preview", scraped_df.head())
    load_to_snowflake(scraped_df)
    st.success("Tours successfully scraped and loaded into Snowflake!")

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
