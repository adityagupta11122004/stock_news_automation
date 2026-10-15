import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

import feedparser
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Stock News Tracker", page_icon="📈", layout="centered")

POSITIVE = {"surge", "gain", "gains", "jumps", "rally", "profit", "growth", "beats", "wins",
            "record", "upgrade", "buy", "rises", "soars", "bullish", "order", "deal"}
NEGATIVE = {"fall", "falls", "drops", "loss", "losses", "slump", "cuts", "downgrade", "sell",
            "decline", "plunges", "bearish", "probe", "fraud", "layoffs", "weak", "miss"}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(query: str, days: int):
    """Fetch news from Google News RSS for a stock name/ticker."""
    q = quote_plus(f"{query} stock when:{days}d")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    rows = []
    for e in feed.entries:
        published = datetime(*e.published_parsed[:6], tzinfo=timezone.utc) if getattr(e, "published_parsed", None) else None
        source = e.get("source", {}).get("title", "Unknown")
        title = re.sub(rf"\s*-\s*{re.escape(source)}$", "", e.title)
        rows.append({"Title": title, "Source": source, "Published": published, "Link": e.link})
    return pd.DataFrame(rows)


def sentiment(title: str) -> str:
    words = set(re.findall(r"[a-z]+", title.lower()))
    score = len(words & POSITIVE) - len(words & NEGATIVE)
    return "🟢 Positive" if score > 0 else "🔴 Negative" if score < 0 else "⚪ Neutral"


st.title("📈 Stock News Tracker")
st.caption("Type any stock name or ticker (e.g. TCS, Reliance, INFY, AAPL) to get the latest news.")

col1, col2, col3 = st.columns([3, 1, 1])
query = col1.text_input("Stock", placeholder="TCS", label_visibility="collapsed")
days = col2.selectbox("Period", [1, 3, 7, 30], index=2, format_func=lambda d: f"{d}d")
limit = col3.selectbox("Show", [10, 20, 30], index=0)

if query.strip():
    with st.spinner(f"Fetching news for {query.upper()}..."):
        df = fetch_news(query.strip(), days)

    if df.empty:
        st.warning("No news found. Try a different name or a longer period.")
    else:
        df = df.sort_values("Published", ascending=False).head(limit).reset_index(drop=True)
        df["Sentiment"] = df["Title"].apply(sentiment)

        m1, m2, m3 = st.columns(3)
        m1.metric("Articles", len(df))
        m2.metric("Positive", int((df["Sentiment"].str.contains("Positive")).sum()))
        m3.metric("Negative", int((df["Sentiment"].str.contains("Negative")).sum()))
        st.divider()

        for _, r in df.iterrows():
            when = r["Published"].strftime("%d %b %Y, %H:%M UTC") if pd.notna(r["Published"]) else ""
            st.markdown(f"**[{r['Title']}]({r['Link']})**  \n{r['Source']} · {when} · {r['Sentiment']}")

        st.download_button("⬇️ Download CSV", df.to_csv(index=False), f"{query.upper()}_news.csv", "text/csv")
else:
    st.info("Enter a stock above to begin.")

st.caption("Headlines via Google News RSS. Sentiment is a simple keyword heuristic, not investment advice.")
