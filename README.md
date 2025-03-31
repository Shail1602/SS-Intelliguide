# SS Intelliguide 🚀

**SS Intelliguide** is an AI-powered travel product knowledge platform developed for Australia Pacific Touring (APT). It transforms unstructured tour and brochure data into structured insights, summaries, and an interactive chatbot interface — all powered by modern LLMs.

Developed by: **Shailesh Rahul** & **Saumya Shruti**  
Built for: **AI Hackathon 2025**

---

## 🔍 Features

- 🌐 **Web Scraping** of APT tour pages and brochures
- 📄 **PDF Parsing & Summarization** using Snowflake Cortex LLMs
- 🤖 **AI Chatbot Interface** to ask natural questions about tours
- ✅ **Supplier Validation UI** to update tour validation status
- 📊 **Dashboard** for tour insights
- ☁️ **Snowflake Integration** for structured backend storage
- 🌙 **Dark/Light Theme Toggle**

---

## 📂 Project Structure

```
SS_Intelliguide/
│
├── scraper/
│   └── scrape_and_prepare_data.py         # Scrapes APT website & prepares tour data
│
├── snowflake_loader/
│   └── load_to_snowflake.py               # Loads scraped data into Snowflake tables
│
├── streamlit_app/
│   └── app.py                             # Main Streamlit interface for users
│
├── requirements.txt                       # Python dependencies
```

---

## 🧠 Powered By

- **Streamlit** – frontend UI
- **Snowflake Cortex** – LLM-powered summarization and Q&A
- **FAISS (optional)** – for semantic search (expandable)
- **Python + BeautifulSoup** – for scraping and parsing

---

## 🔐 Secrets Configuration (For Deployment)

Please add your credentials to **Streamlit Community Cloud** `secrets.toml` under **Settings > Secrets**:

## 🚀 How to Run

1. Clone the repo or unzip this project.
2. Set up your Snowflake tables using the provided SQL DDL scripts.
3. Run the scraper:
   ```bash
   python scraper/scrape_and_prepare_data.py
   ```
4. Load into Snowflake:
   ```bash
   python snowflake_loader/load_to_snowflake.py
   ```
5. Launch the app:
   ```bash
   streamlit run streamlit_app/app.py
   ```

---

## 🧑‍💻 Developers

- **Shailesh Rahul** – Full Stack Engineering
- **Saumya Shruti** – UX/Data Design

---


