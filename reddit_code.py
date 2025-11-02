# This code is for the Reddit data scraping
import os
import time
from typing import List, Dict, Any, Optional
import pandas as pd

# Using try block
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# Installing praw for redit
import praw

# Config & Authentication
def load_credentials(env_paths: Optional[List[str]] = None) -> Dict[str, str]:


    env_paths = env_paths or ["/content/reddit.env"]

    # Load the first env file that exists (if python-dotenv is available)
    if load_dotenv:
        for p in env_paths:
            if os.path.exists(p):
                load_dotenv(p, override=True)
                break

    cid = os.getenv("REDDIT_CLIENT_ID", "").strip()
    csec = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    uagt = os.getenv("REDDIT_USER_AGENT", "").strip()

    missing = [k for k, v in {
        "REDDIT_CLIENT_ID": cid,
        "REDDIT_CLIENT_SECRET": csec,
        "REDDIT_USER_AGENT": uagt
    }.items() if not v]

    if missing:
        raise RuntimeError(
            "Missing required credentials in reddit.env/.env: " + ", ".join(missing) +
            "\nCreate a reddit.env file in the SAME folder as this script with:\n"
            'REDDIT_CLIENT_ID="your_id"\nREDDIT_CLIENT_SECRET="your_secret"\nREDDIT_USER_AGENT="Your App by u/YourUsername"')
    return {"client_id": cid, "client_secret": csec, "user_agent": uagt}


def make_reddit(creds: Dict[str, str]) -> praw.Reddit:
    """
    Create a PRAW Reddit instance (read-only).
    """
    reddit = praw.Reddit(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        user_agent=creds["user_agent"],
        check_for_async=False,   # avoid asyncio warnings
        ratelimit_seconds=5)
    return reddit

# These will have predictors in asking in question
POST_FIELDS = [
    "title", "score", "upvote_ratio", "num_comments", "author",
    "subreddit", "url", "permalink", "created_utc", "is_self",
    "selftext", "flair", "domain", "search_query"]

def _safe_get_author_name(sub) -> Optional[str]:
    try:
        return sub.author.name if sub.author else None
    except Exception:
        return None

def _row_from_submission(sub, search_query: Optional[str] = None) -> Dict[str, Any]:
    # Truncate selftext to 500 chars
    body = (sub.selftext or "") if getattr(sub, "selftext", None) else ""
    if body and len(body) > 500:
        body = body[:497] + "..."

    flair = getattr(sub, "link_flair_text", None)
    domain = getattr(sub, "domain", None)

    return {
        "title": getattr(sub, "title", None),
        "score": getattr(sub, "score", None),
        "upvote_ratio": getattr(sub, "upvote_ratio", None),
        "num_comments": getattr(sub, "num_comments", None),
        "author": _safe_get_author_name(sub),
        "subreddit": getattr(sub.subreddit, "display_name", None) if getattr(sub, "subreddit", None) else None,
        "url": getattr(sub, "url", None),
        "permalink": f"https://www.reddit.com{getattr(sub, 'permalink', '')}" if getattr(sub, "permalink", None) else None,
        "created_utc": int(getattr(sub, "created_utc", 0)) if getattr(sub, "created_utc", None) else None,
        "is_self": getattr(sub, "is_self", None),
        "selftext": body,
        "flair": flair,
        "domain": domain,
        "search_query": search_query}

def fetch_hot_posts(reddit: praw.Reddit, subreddits: List[str], limit: int = 50) -> List[Dict[str, Any]]:
    rows = []
    for sr in subreddits:
        try:
            for sub in reddit.subreddit(sr).hot(limit=limit):
                rows.append(_row_from_submission(sub, search_query=None))
            print(f"[HOT] r/{sr}: total rows so far = {len(rows)}")
            time.sleep(1)  # courteous pacing
        except Exception as e:
            print(f"[WARN] Could not fetch hot posts for r/{sr}: {e}")
    return rows

def search_posts(reddit: praw.Reddit, query: str, subreddits: List[str], limit: int = 50) -> List[Dict[str, Any]]:
    rows = []
    for sr in subreddits:
        try:
            for sub in reddit.subreddit(sr).search(query, limit=limit, sort="relevance"):
                rows.append(_row_from_submission(sub, search_query=query))
            print(f"[SEARCH] '{query}' in r/{sr}: total rows so far = {len(rows)}")
            time.sleep(1)
        except Exception as e:
            print(f"[WARN] Search failed in r/{sr} for query '{query}': {e}")
    return rows

# Processing & Exporting
def to_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)

    # Ensure expected columns exist
    for col in POST_FIELDS:
        if col not in df.columns:
            df[col] = None

    # Deduplicate by permalink (fallback to title if permalink missing)
    if "permalink" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["permalink"]).copy()
        print(f"[DEDUP] By permalink: {before} -> {len(df)}")
    elif "title" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["title"]).copy()
        print(f"[DEDUP] By title: {before} -> {len(df)}")

    # Ordering columns
    df = df[POST_FIELDS]
    return df

def save_csv(df: pd.DataFrame, out_path: str = "reddit_data.csv") -> str:
    df.to_csv(out_path, index=False)
    print(f"[SAVE] {len(df)} rows -> {out_path}")
    return out_path

if __name__ == "__main__":
    HOT_SUBREDDITS = ["learnpython", "datascience", "MachineLearning"]
    SEARCH_SUBREDDITS = ["learnpython", "datascience"]
    SEARCH_QUERY = "pandas"
    LIMIT_HOT = 50
    LIMIT_SEARCH = 30
    OUTPUT = "/content/reddit_data.csv"   # <— local

    creds = load_credentials()
    reddit = make_reddit(creds)

    try:
        print(f"[AUTH] reddit.user.me() = {reddit.user.me()}")
    except Exception as e:
        print(f"[AUTH] Warning reading user: {e}")

    hot_rows = fetch_hot_posts(reddit, HOT_SUBREDDITS, limit=LIMIT_HOT)
    search_rows = search_posts(reddit, SEARCH_QUERY, SEARCH_SUBREDDITS, limit=LIMIT_SEARCH)

    all_rows = hot_rows + search_rows
    df = to_dataframe(all_rows)
    save_csv(df, out_path=OUTPUT)

    if not df.empty and "subreddit" in df.columns:
        by_sr = df.groupby("subreddit").size().sort_values(ascending=False)
        print("\n[SUMMARY] Rows by subreddit:\n" + by_sr.to_string())
    print("\n[DONE] Pipeline complete.")

# This code for the creating workspace in google Drive

from google.colab import drive
drive.mount('/content/drive')

# Navigate to your Drive root
%cd /content/drive/MyDrive/

# Create your main assignment folder (only if it doesn’t exist)
!mkdir -p assignment_folder

# Go inside the folder
%cd assignment_folder

# Create the necessary files
!touch reddit_code.py
!touch reddit.env
!touch requirements.txt
!touch README.md

    # This code is for the content writing
    %%writefile .gitignore
# Ignore sensitive environment files
reddit.env

# Ignore Python virtual environment folders and caches
venv/
__pycache__/

    %%writefile reddit.env
# Reddit API Credentials (Template)
REDDIT_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDDIT_USER_AGENT = "YOUR_USER_AGENT_HERE"

%%writefile requirements.txt
praw
pandas
python-dotenv

%%writefile README.md
# Reddit Sentiment Analysis on Netflix Pricing Discussions

# Project Overview
This project uses the **Reddit API (PRAW)** to collect real user discussions about **Netflix pricing and subscription plans** from various subreddits.
The data is then prepared for **sentiment analysis** and **topic modeling** to understand how users perceive Netflix’s pricing compared to other streaming platforms.

---

# Objectives
- Collect Reddit posts from Netflix-related and streaming subreddits
- Analyze user sentiments (positive, neutral, negative) toward Netflix pricing
- Identify major discussion themes using topic modeling (LDA / BERTopic)
- Compare pricing opinions across different streaming platforms

---

# Tools & Libraries
- **Python**
- **PRAW** – Reddit API wrapper
- **pandas** – Data manipulation
- **python-dotenv** – Secure environment variables
- **NLTK / VADER / TextBlob** – Sentiment analysis
- **matplotlib / seaborn** – Visualization
- **Tableau / Power BI** – Dashboard visualization (future step)

---

# Files in This Repository
| File | Description |
|------|--------------|
| `reddit_code.py` | Python script to collect Reddit posts |
| `reddit.env` | Reddit API credentials (ignored by `.gitignore`) |
| `requirements.txt` | Required Python packages |
| `README.md` | Project overview and instructions |
| `.gitignore` | Prevents sensitive files from uploading to GitHub |
| `reddit_data_sample.csv` | Example collected dataset |

---

# How to Run
1. Install required packages
   ```bash
   pip install -r requirements.txt
    
# This code is for the connection Colab and Github

    !git config --global user.name "Dinesh Acharya"
!git config --global user.email "deeeneshaaacharya@gmail.com"

# Ensure you are in your assignment directory
%cd /content/drive/MyDrive/assignment_folder/

# Initialize a new Git repository
!git init

# Stage all your files for the commit
!git add .

# Commit the files with a message
!git commit -m "Initial commit from Google Colab"

from google.colab import userdata

github_token = userdata.get('GITHUB_PAT')
username = "deeeneshaaacharya-hub"
repo_name = "Reddit_API_Assignment "

# Constructing the remote URL with authentication
remote_url = f"https://{username}:{github_token}@github.com/{username}/{repo_name}.git"

# Addding the remote, set the main branch, and push the code
!git remote add origin {remote_url}
!git branch -M main
!git push -u origin main

