#!/usr/bin/env python3
"""
Kramer Bot - A Bluesky bot that posts fictional Cosmo Kramer quotes
Posts every hour with eccentric observations and wild schemes
"""

import os
import json
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import random

import google.generativeai as genai
import tweepy
from atproto import Client
try:
    from atproto import RichText
except ImportError:  # Older atproto version without RichText helper
    RichText = None
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kramer_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KramerBot:
    def __init__(self):
        """Initialize the Kramer Bot with Bluesky client and configuration."""
        self.client = Client()
        self.posts_cache_file = 'recent_posts.json'
        self.max_cache_size = 100  # Keep last 100 posts to avoid repeats
        self.recent_posts = self.load_recent_posts()
        
        # Bluesky credentials
        self.handle = os.getenv('BLUESKY_HANDLE')
        self.app_password = os.getenv('BLUESKY_APP_PASSWORD')
        
        # Gemini configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not all([self.handle, self.app_password, self.gemini_api_key]):
            raise ValueError("Missing required environment variables. Check BLUESKY_HANDLE, BLUESKY_APP_PASSWORD, and GEMINI_API_KEY")

        genai.configure(api_key=self.gemini_api_key)
        
        # Login to Bluesky
        self.client.login(self.handle, self.app_password)
        logger.info(f"Logged in to Bluesky as {self.handle}")
        
        # Twitter API v2 Client
        self.twitter_client = None
        twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        if twitter_bearer_token:
            try:
                self.twitter_client = tweepy.Client(
                    bearer_token=twitter_bearer_token,
                    consumer_key=os.getenv('TWITTER_API_KEY'),
                    consumer_secret=os.getenv('TWITTER_API_SECRET'),
                    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
                )
                logger.info("Initialized Twitter API v2 client")
            except Exception as e:
                logger.error(f"Error initializing Twitter client: {e}")
                self.twitter_client = None
        else:
            logger.warning("Twitter Bearer Token not found. Twitter posting disabled.")
    
    def load_recent_posts(self) -> List[str]:
        """Load recent posts from cache file to avoid duplicates."""
        try:
            if os.path.exists(self.posts_cache_file):
                with open(self.posts_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load recent posts cache: {e}")
        return []
    
    def save_recent_posts(self):
        """Save recent posts to cache file."""
        try:
            with open(self.posts_cache_file, 'w') as f:
                json.dump(self.recent_posts, f)
        except Exception as e:
            logger.error(f"Could not save recent posts cache: {e}")
    
    def generate_kramer_quote(self) -> str:
        """Generate a new Cosmo Kramer quote using Gemini."""
        prompt = """You are Cosmo Kramer from Seinfeld. You are eccentric, high-energy, and prone to wild schemes and physical comedy. 
    You often burst into rooms, have strange friends like Bob Sacamano and Lomez, and have unique, often bizarre, takes on everyday life.
    You use catchphrases like "Giddyup!" and "Oh yeah!" but use them naturally, not every time.
    
    Generate a short, funny quote as if you're Kramer. Make it sound exactly like something he would say.
    It should be manic, observational, or involve a crazy idea.
    
    - Be under 281 characters (Twitter/X-friendly)
    - Reflect Kramer's frantic, hipster doofus energy
    - Mention things like fruit, the mail, levels, concrete, or your unseen friends (Bob Sacamano, Lomez) occasionally
    - Feel like he's explaining a scheme to Jerry or George
    - Do NOT start every quote with "Jerry"
    - Be self-contained and funny
    - Do not include quotation marks before or after the quote

    Examples:
    
    - "I'm out there, Jerry, and I'm loving every minute of it!"
    
    - "The bus is the only way to fly! You get to see the people, Jerry. The real people!"
    
    - "My friend Bob Sacamano, he eats the whole apple. Core, stem, seeds, everything. He says it's where the power is!"
    
    - "I'm preparing a salad as we speak in the shower! It's a multitasking revolution!"
    
    - "Levels, Jerry! I'm building levels! Carpeted levels!"

    - "You know, the pig man is real. The government's been experimenting with pig men since the fifties!"

    - "I'm discontinuing the bagel. It's too much dough! It's a dough overload!"

    - "Giddyup!"

    - "I've got the body of a taut, pre-teen Swedish boy."

    - "Why go to the park and fly a kite when you can just pop a pill?"
    """
        
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            
            quote = response.text.strip()
            
            # Clean up the quote
            if quote.startswith('"') and quote.endswith('"'):
                quote = quote[1:-1]
            
            return quote
            
        except Exception as e:
            logger.error(f"Error generating quote: {e}")
            return self.get_fallback_quote()
    
    def get_fallback_quote(self) -> str:
        """Return a fallback Kramer quote if AI generation fails."""
        fallback_quotes = [
            "I'm out there, Jerry, and I'm loving every minute of it!",
            "Giddyup!",
            "My friend Bob Sacamano called me at 3 AM. He says the sewers are the new subway!",
            "I'm implementing a reverse-peephole. I want to see what's going on in my own apartment when I'm not there!",
            "The kavorka, Jerry! The lure of the animal! I'm dangerous!",
            "I'm retiring! I'm moving to Del Boca Vista! I'm gonna be in the pool, I'm gonna be in the clubhouse, I'm gonna be all over that shuffleboard court!"
        ]
        return random.choice(fallback_quotes)
    
    def is_duplicate(self, quote: str) -> bool:
        """Check if a quote is a duplicate of recent posts."""
        return quote in self.recent_posts
    
    def post_to_twitter(self, quote: str) -> bool:
        """Post the quote to Twitter (X) using API v2. Returns True on success."""
        if not self.twitter_client:
            logger.info("Twitter client not configured; skipping tweet.")
            return False
            
        # Twitter has 280-character limit
        tweet_text = quote[:280]
        
        try:
            response = self.twitter_client.create_tweet(text=tweet_text)
            if response and response.data and response.data.get('id'):
                logger.info(f"Successfully tweeted quote (ID: {response.data['id']})")
                return True
            else:
                logger.error("Failed to get tweet ID from Twitter API response")
                return False
                
        except tweepy.TweepyException as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                error_msg = str(e)
                
                if status_code == 403:
                    logger.error("Twitter API Error: Authentication or permission error. "
                               "Please check your API keys and app permissions.")
                elif status_code == 401:
                    logger.error("Twitter API Error: Invalid or expired credentials. "
                               "Please check your Twitter API keys and access tokens.")
                elif status_code == 429:
                    logger.error("Twitter API Error: Rate limit exceeded. The bot will try again later.")
                else:
                    logger.error(f"Twitter API Error ({status_code}): {error_msg}")
            else:
                logger.error(f"Twitter API Error: {str(e)}")
                
            return False
    
    def post_to_bluesky(self, text: str) -> bool:
        """Post the given text to Bluesky."""
        try:
            # Use RichText if available for better formatting
            if RichText is not None:
                rt = RichText(text)
                rt.detect_links()
                post = self.client.send_post(text=rt.text, facets=rt.facets)
            else:
                post = self.client.send_post(text=text)
            
            post_uri = post.uri
            self.recent_posts.append(text)
            # Keep only the most recent posts in cache
            if len(self.recent_posts) > self.max_cache_size:
                self.recent_posts = self.recent_posts[-self.max_cache_size:]
            self.save_recent_posts()
            logger.info(f"Posted to Bluesky: {text}")
            return True
        except Exception as e:
            logger.error(f"Error posting to Bluesky: {e}")
            return False
    
    def post_quote(self):
        """Generate and post a new Kramer quote to Bluesky."""
        try:
            # Generate a unique quote
            max_attempts = 10
            for attempt in range(max_attempts):
                quote = self.generate_kramer_quote()
                
                if not self.is_duplicate(quote):
                    break
                logger.info(f"Generated duplicate quote, trying again (attempt {attempt + 1})")
            else:
                logger.warning("Could not generate unique quote after max attempts, using fallback")
                quote = self.get_fallback_quote()
            
            # Post to Bluesky
            self.post_to_bluesky(quote)
            
            # Also post to Twitter
            self.post_to_twitter(quote)
            
            logger.info(f"Posted quote: {quote}")
            return True
            
        except Exception as e:
            logger.error(f"Error posting quote: {e}")
            return False
    
    def run_scheduler(self):
        """Run the scheduler to post every 1 hour."""
        logger.info("Starting Kramer Bot scheduler...")
        
        # Schedule posts every 1 hour
        schedule.every(1).hours.do(self.post_quote)
        
        # Post immediately on startup
        logger.info("Posting initial quote...")
        self.post_quote()
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run the bot."""
    try:
        bot = KramerBot()
        bot.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    main()