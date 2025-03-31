import tweepy
import mysql.connector
from textblob import TextBlob

# Twitter Bearer Token
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHU80QEAAAAAfEBlbgaRv7TZRPLQmrKl55Zt5h8%3D9nPGB4ffSmazZYOjlcfUQLmorrMireTgBJ0QJYWhpxFMxJP0lz"

# Authenticate with the Twitter API using Bearer Token
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Connect to MySQL Database
conn = mysql.connector.connect(host="localhost", user="root", password="Csk738", database="twitter_sentiment_db")
cursor = conn.cursor()

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

        # Iterate over the tweets
        for tweet in tweets.data:
            sentiment = analyze_sentiment(tweet.text)
            
            # Insert tweet and sentiment into MySQL table
            sql = "INSERT INTO tweets (tweet_id, tweet_text, sentiment) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE sentiment=%s"
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
        sql = "SELECT tweet_text, sentiment, created_at FROM tweets WHERE tweet_text LIKE %s ORDER BY created_at DESC"
        cursor.execute(sql, ('%' + keyword + '%',))
        stored_tweets = cursor.fetchall()
        
        return stored_tweets
    
    except Exception as e:
        print(f"An error occurred while fetching stored tweets: {e}")
        return None
