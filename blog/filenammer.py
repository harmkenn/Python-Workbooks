import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.title("Blogger Title + Date Scraper (Working for New Blogger Layout)")

start_url = st.text_input(
    "Paste the first Blogger 'search' page URL:",
    "https://micheleharmon13.blogspot.com"
)

if st.button("Start Scraping"):

    # TOP dataframe placeholder
    df_placeholder = st.empty()
    st.write("---")

    all_rows = []
    visited = set()
    current_url = start_url
    page_count = 0

    progress = st.progress(0.0)

    while current_url and current_url not in visited and page_count < 300:
        visited.add(current_url)
        page_count += 1

        st.write(f"📄 Scraping page {page_count}: {current_url}")

        # Fetch page
        try:
            r = requests.get(current_url, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
        except:
            break

        # ===============================
        # CORRECT SELECTORS FOR YOUR BLOG
        # ===============================
        posts = soup.select("article.post")

        for p in posts:
            title_el = p.select_one("h3.post-title.entry-title a")
            date_el = p.select_one("time.published")

            if title_el and date_el:
                all_rows.append({
                    "title": title_el.text.strip(),
                    "date": date_el.text.strip(),
                    "url": title_el["href"]
                })

        # Update live dataframe
        if all_rows:
            df_placeholder.dataframe(pd.DataFrame(all_rows))

        # Find next page
        next_btn = soup.select_one("a.blog-pager-older-link")
        if next_btn:
            current_url = urljoin(current_url, next_btn["href"])
        else:
            current_url = None

        progress.progress(min(page_count / 300, 1.0))

    # Final output
    st.success(f"Scraped {len(all_rows)} total posts.")
    if all_rows:
        df_final = pd.DataFrame(all_rows)
        st.dataframe(df_final)

        st.download_button(
            "⬇ Download CSV",
            df_final.to_csv(index=False).encode("utf-8"),
            "blog_posts.csv",
            "text/csv"
        )
