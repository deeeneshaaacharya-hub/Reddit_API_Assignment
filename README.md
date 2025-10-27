# Reddit API Data Pipeline (PRAW + pandas)

This project collects Reddit posts using PRAW, cleans them with pandas, and exports a CSV file. It follows the assignment spec: secure credentials via an environment file, fetch **hot** posts from multiple subreddits, perform a **keyword search**, and export a deduplicated `reddit_data.csv` with the required columns.

## How to Run

### 1) Prerequisites
- Python 3.9+
- A Reddit app with **Client ID**, **Client Secret**, and a **User Agent** you define (e.g., `"My MSBA212 App by u/<your_username>"`).

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure credentials
Create a file named **`reddit.env`** (or `.env`) in the same folder as `reddit_code.py` with:
```
REDDIT_CLIENT_ID="YOUR_CLIENT_ID_HERE"
REDDIT_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
REDDIT_USER_AGENT="YOUR_USER_AGENT_HERE"
```
> **Do not** commit your real secrets to GitHub. Keep `reddit.env` out of version control via `.gitignore`.

### 4) Run
```bash
python reddit_code.py
```
The script will:
- Fetch hot posts from your chosen subreddits
- Search for your chosen keyword across selected subreddits
- Deduplicate and export **`reddit_data.csv`**

## Output
`reddit_data.csv` includes at least these columns:

- `title`, `score`, `upvote_ratio`, `num_comments`, `author`, `subreddit`, `url`, `permalink`, `created_utc`, `is_self`, `selftext` (truncated to 500 chars), `flair`, `domain`, `search_query`

## Colab Tips
- Upload `reddit.env` next to `reddit_code.py` or put it in your current working directory.
- If you see `Missing required credentials` or `401`, double‑check your **Client ID/Secret** and **User Agent**, and that your Reddit app type supports script/personal use read‑only access.
