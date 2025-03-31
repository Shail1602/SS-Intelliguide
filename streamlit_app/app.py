import streamlit as st
import snowflake.connector
import pandas as pd

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

df = get_tours()
st.dataframe(df)

st.subheader("Summarize All Tours")
if st.button("Generate Summary"):
    prompt = "Summarize all APT tours in 3 bullet points per tour."
    summary = call_llm(prompt, model_choice)
    st.write(summary)

st.subheader("Ask a question about the brochures")
user_q = st.text_input("Enter your question:")
if user_q:
    answer = call_llm(user_q, model_choice)
    st.success(answer)
