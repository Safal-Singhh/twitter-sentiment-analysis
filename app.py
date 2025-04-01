import streamlit as st
import mysql.connector
import os
from twitter_fetch import fetch_and_store_tweets, fetch_stored_tweets

# Custom CSS to improve UI appearance
st.markdown("""
    <style>
        .title {
            font-size: 50px;
            font-weight: bold;
            color: #3e8e41;
            text-align: center;
        }
        .header {
            font-size: 30px;
            font-weight: 600;
            color: #2e7d32;
        }
        .description {
            font-size: 20px;
            font-weight: 400;
            color: #444;
            text-align: center;
        }
        .tweet-container {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background-color: #fafafa;
            margin: 10px 0;
        }
        .tweet {
            font-size: 16px;
            color: #555;
        }
        .sentiment {
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
            padding: 5px;
            border-radius: 5px;
        }
        .positive {
            background-color: #4caf50;
        }
        .negative {
            background-color: #f44336;
        }
        .neutral {
            background-color: #9e9e9e;
        }
    </style>
""", unsafe_allow_html=True)

# Connect to MySQL using environment variables
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "mysql_host"),
    user=os.getenv("DB_USER", "i_am_user"),
    password=os.getenv("DB_PASSWORD", "123Csk738"),
    database=os.getenv("DB_NAME", "twitter_sentiment_db")
)
cursor = conn.cursor()

# Streamlit UI
st.markdown('<div class="title">Twitter Sentiment Analysis</div>', unsafe_allow_html=True)

# Instructions
st.markdown('<div class="description">Search tweets from Twitter or view previously stored tweets in the database.</div>', unsafe_allow_html=True)

# Option to search for tweets from Twitter or from the database
search_option = st.selectbox("Choose your search option:", ["Fetch Tweets from Twitter", "Fetch Stored Tweets from Database"])

# Text input for keyword
keyword = st.text_input("Enter Keyword to Search", key="keyword", placeholder="e.g., Python, AI, etc.")

# Buttons and search functionality
if search_option == "Fetch Tweets from Twitter":
    if st.button("Fetch Tweets", key="fetch_tweets", help="Click to fetch tweets from Twitter"):
        if keyword:
            tweets = fetch_and_store_tweets(keyword)
            if tweets is not None:
                st.success(f"{len(tweets)} Tweets fetched and stored successfully!")
            else:
                st.error("Error occurred while fetching tweets. Please try again later.")
        else:
            st.error("Please enter a keyword to search for tweets.")
            
elif search_option == "Fetch Stored Tweets from Database":
    if st.button("Fetch Stored Tweets", key="fetch_stored_tweets", help="Click to fetch stored tweets from the database"):
        if keyword:
            stored_tweets = fetch_stored_tweets(keyword)
            if stored_tweets is not None:
                if stored_tweets:
                    st.markdown('<div class="header">Stored Tweets</div>', unsafe_allow_html=True)
                    for tweet in stored_tweets:
                        sentiment_class = tweet[1].lower()
                        sentiment_class = "neutral" if sentiment_class not in ["positive", "negative"] else sentiment_class
                        
                        st.markdown(f"""
                            <div class="tweet-container">
                                <div class="tweet">{tweet[0]}</div>
                                <div class="sentiment {sentiment_class}">{tweet[1]}</div>
                                <div class="tweet">Date: {tweet[2]}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No stored tweets found for this keyword.")
            else:
                st.error("Error occurred while fetching stored tweets. Please try again later.")
        else:
            st.error("Please enter a keyword to search for stored tweets.")

# Option to display all stored tweets
if st.button("Show All Stored Tweets", key="show_all"):
    cursor.execute("SELECT tweet_text, sentiment, created_at FROM tweets ORDER BY created_at DESC")
    stored_tweets = cursor.fetchall()
    st.markdown('<div class="header">All Stored Tweets</div>', unsafe_allow_html=True)
    for tweet in stored_tweets:
        sentiment_class = tweet[1].lower()
        sentiment_class = "neutral" if sentiment_class not in ["positive", "negative"] else sentiment_class
        
        st.markdown(f"""
            <div class="tweet-container">
                <div class="tweet">{tweet[0]}</div>
                <div class="sentiment {sentiment_class}">{tweet[1]}</div>
                <div class="tweet">Date: {tweet[2]}</div>
            </div>
        """, unsafe_allow_html=True)
