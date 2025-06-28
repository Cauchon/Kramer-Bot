#!/usr/bin/env python3
"""
Kramer Bot - A Bluesky bot that posts fictional Cosmo Kramer quotes
Posts every 3 hours with modern-day observations and schemes
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
from atproto import Client
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
        prompt = """Generate a short, punchy quote from Cosmo Kramer (from Seinfeld) as if he's living in present day. 

The quote should:
- Be under 300 characters
- Reflect Kramer's eccentric personality and speaking style
- Include modern technology, trends, or culture
- Be self-contained and funny
- Start with "I" or "You" and feel like natural Kramer dialogue
- Include his characteristic enthusiasm and bizarre logic

Examples of the style and tone:
"I tried to make my own oat milk… I milked the oats, Jerry! But they just got soggy!"
"You ever been in a Zoom breakout room, Jerry? It's like being trapped in an elevator… with no buttons!"
"I sold my neighbor an NFT of his own front door. It's art, Jerry!"
I tried intermittent fasting, Jerry. But I kept sleeping through the eating window!”
“You ever yell at your smart fridge, Jerry? It remembers! It's holding a grudge!”
“I subscribed to twelve AI girlfriends. Now they're mad I'm not exclusive!”
“I bought a weighted blanket… it's too clingy, Jerry! It's like sleeping under commitment!”
“I got a smartwatch, Jerry. It told me to breathe—while I was already breathing! Now I'm overthinking it!””
“I tried to unsubscribe from emails, Jerry. The link took me to a TED Talk!”
“You ever ghost a spam caller, Jerry? They called back apologizing! Said they missed me!”


Generate only the quote, no additional text or formatting."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at writing dialogue in Cosmo Kramer's unique voice and style."},
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
            "I bought a self-driving e-scooter, Jerry. Now it's driving me crazy!",
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
            response = self.client.send_post(text=quote)
            
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
        """Run the scheduler to post every 30 minutes."""
        logger.info("Starting Kramer Bot scheduler...")
        
        # Schedule posts every 30 minutes
        schedule.every(30).minutes.do(self.post_quote)
        
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