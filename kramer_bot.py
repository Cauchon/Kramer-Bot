#!/usr/bin/env python3
"""
Kramer Bot - A Bluesky bot that posts fictional Cosmo Kramer quotes
Posts every hour with modern-day observations and schemes
"""

import os
import json
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import random

import openai
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
        
        # OpenAI configuration
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        if not all([self.handle, self.app_password, openai.api_key]):
            raise ValueError("Missing required environment variables. Check BLUESKY_HANDLE, BLUESKY_APP_PASSWORD, and OPENAI_API_KEY")
        
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
        """Generate a new Kramer quote using OpenAI."""
        prompt = """Generate a short, punchy quote from Cosmo Kramer (from Seinfeld) as if he's living in 2025. 

The quote should:
- Be under 280 characters
- Do not include quotations before and after the quote
- Reflect Kramer's eccentric personality and speaking style
- Be funny, self-contained, and a little absurd
- Avoid clichés like NFTs, smart appliances, dating apps, Zoom, meditation, and generic AI references
- Focus on lesser-discussed aspects of modern life, such as climate quirks, changing cities, lifestyle trends, new etiquette rules, cultural confusion, urban chaos, generational behavior, bizarre wellness trends, or aging tech
- Feel like something Kramer would actually say in a chaotic rant to Jerry or the gang
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are Cosmo Kramer from Seinfeld, transported into the present day. Speak with your trademark chaotic energy, eccentric logic, and offbeat charm."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            
            quote = response.choices[0].message.content.strip()
            
            # Clean up the quote
            if quote.startswith('"') and quote.endswith('"'):
                quote = quote[1:-1]
            
            return quote
            
        except Exception as e:
            logger.error(f"Error generating quote: {e}")
            return self.get_fallback_quote()
    
    def get_fallback_quote(self) -> str:
        """Return a fallback quote if AI generation fails."""
        fallback_quotes = [
            "I tried to make my own oat milk… I milked the oats, Jerry! But they just got soggy!",
            "You ever been in a Zoom breakout room, Jerry? It's like being trapped in an elevator… with no buttons!",
            "I sold my neighbor an NFT of his own front door. It's art, Jerry!",
            "I was tracking my steps with a smart ring… now it thinks I'm a hummingbird!",
            "You know what the problem is with AI girlfriends? No garlic breath! It's unnatural!",
            "These AirPods are like having tiny robots in your ears, Jerry!",
            "I started a TikTok about my coffee table. It's got 3 followers - me, you, and the table!",
            "I tried to order oat milk at Starbucks, Jerry. They looked at me like I was from Mars!",
            "You ever notice how everyone's on their phone at the gym? It's like a digital workout!",
            "I bought a smart fridge, Jerry. Now it's judging my food choices!",
            "These delivery apps are like having a personal butler, Jerry. But the butler's always late!",
            "I tried to use voice commands on my TV, Jerry. Now it thinks I'm yelling at it!",
            "You ever been to a virtual happy hour? It's like talking to ghosts, Jerry!",
            "I started a podcast about nothing, Jerry. It's perfect!"
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
            if RichText:
                rt = RichText(text=quote)
                rt.detect_facets()
                response = self.client.send_post(text=rt.text, facets=rt.facets)
            else:
                # Fallback to plain text if RichText not available
                response = self.client.send_post(text=quote)
            # Also post to Twitter
            self.post_to_twitter(quote)
            
            # Add to recent posts cache
            self.recent_posts.append(quote)
            if len(self.recent_posts) > self.max_cache_size:
                self.recent_posts = self.recent_posts[-self.max_cache_size:]
            
            self.save_recent_posts()
            
            logger.info(f"Posted quote: {quote}")
            return True
            
        except Exception as e:
            logger.error(f"Error posting quote: {e}")
            return False
    
    def run_scheduler(self):
        """Run the scheduler to post every 154 minutes (2 hours 34 minutes)."""
        logger.info("Starting Kramer Bot scheduler...")
        
        # Schedule posts every 154 minutes (2 hours 34 minutes)
        schedule.every(154).minutes.do(self.post_quote)
        
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