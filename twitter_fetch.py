import tweepy
import mysql.connector
import os
from textblob import TextBlob

# Twitter Bearer Token
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate with the Twitter API using Bearer Token
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Connect to MySQL Database using environment variables
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "mysql.railway.internal"),
    port=os.getenv("MYSQL_PORT", "3306"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "ahGZGJsYfAuFNsLmCbvpLLnFPiDGoQBX"),
    database=os.getenv("MYSQL_DB", "railway")
)
cursor = conn.cursor()

# Ensure tweets table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tweets (
        tweet_id BIGINT PRIMARY KEY,
        tweet_text TEXT,
        sentiment VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Function to analyze sentiment
def analyze_sentiment(tweet):
    analysis = TextBlob(tweet)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Function to fetch tweets and store them in the database
def fetch_and_store_tweets(keyword):
    try:
        # Fetch 10 tweets based on the keyword
        tweets = client.search_recent_tweets(query=keyword, max_results=10, tweet_fields=["created_at", "text"])
        
        if not tweets or not tweets.data:
            return None
        
        # Iterate over the tweets
        for tweet in tweets.data:
            sentiment = analyze_sentiment(tweet.text)
            
            # Insert tweet and sentiment into MySQL table
            sql = """
                INSERT INTO tweets (tweet_id, tweet_text, sentiment)
                VALUES (%s, %s, %s) 
                ON DUPLICATE KEY UPDATE sentiment=%s
            """
            cursor.execute(sql, (tweet.id, tweet.text, sentiment, sentiment))
        
        conn.commit()
        return tweets.data
    
    except Exception as e:
        print(f"An error occurred while fetching tweets: {e}")
        return None

# Function to fetch stored tweets from the database based on a keyword
def fetch_stored_tweets(keyword):
    try:
        # Query to fetch stored tweets based on the keyword
        sql = """
            SELECT tweet_text, sentiment, created_at 
            FROM tweets 
            WHERE tweet_text LIKE %s 
            ORDER BY created_at DESC
        """
        cursor.execute(sql, ('%' + keyword + '%',))
        stored_tweets = cursor.fetchall()
        
        return stored_tweets
    
    except Exception as e:
        print(f"An error occurred while fetching stored tweets: {e}")
        return None