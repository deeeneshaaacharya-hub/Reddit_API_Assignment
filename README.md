# Reddit API Assignment
This repository demonstrates connecting Google Colab to GitHub and using the Reddit API.

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
