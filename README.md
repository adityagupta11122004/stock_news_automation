# Stock News Tracker
Type a stock (TCS, INFY, AAPL...) -> latest news, sentiment tags, CSV export.

## Run locally
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    streamlit run app.py

## Deploy free (Streamlit Community Cloud)
1. Push this folder to a public GitHub repo.
2. Go to share.streamlit.io -> New app -> select repo, branch, `app.py`.
3. Click Deploy -> you get a public URL to present.
