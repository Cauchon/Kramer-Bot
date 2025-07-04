#!/usr/bin/env python3
"""
Test script for Kramer Bot - generates quotes without posting to Bluesky
"""

import os
import sys
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def test_quote_generation():
    """Test the quote generation functionality."""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai.api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
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
        print("🤖 Testing OpenAI API connection...")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cosmo Kramer from Seinfeld, transported into the present day. Speak with your trademark chaotic energy, eccentric logic, and offbeat charm. You're fascinated—and confused—by modern technology, trends, and culture"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.9
        )
        
        quote = response.choices[0].message.content.strip()
        
        # Clean up the quote
        if quote.startswith('"') and quote.endswith('"'):
            quote = quote[1:-1]
        
        print("✅ OpenAI API connection successful!")
        print(f"📝 Generated quote: {quote}")
        print(f"📏 Character count: {len(quote)}")
        
        if len(quote) > 280:
            print("⚠️  Warning: Quote exceeds 280 character limit (Twitter limit)")
        else:
            print("✅ Quote within 280 character limit (Twitter compatible)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI API: {e}")
        return False

def test_fallback_quotes():
    """Test the fallback quote system."""
    print("\n🔄 Testing fallback quotes...")
    
    fallback_quotes = [
        "I tried to make my own oat milk… I milked the oats, Jerry! But they just got soggy!",
        "You ever been in a Zoom breakout room, Jerry? It's like being trapped in an elevator… with no buttons!",
        "I sold my neighbor an NFT of his own front door. It's art, Jerry!",
        "I was tracking my steps with a smart ring… now it thinks I'm a hummingbird!",
        "You know what the problem is with AI girlfriends? No garlic breath! It's unnatural!"
    ]
    
    for i, quote in enumerate(fallback_quotes, 1):
        print(f"📝 Fallback quote {i}: {quote}")
        print(f"📏 Character count: {len(quote)}")
        if len(quote) > 300:
            print("⚠️  Warning: Quote exceeds 300 character limit")
        print()
    
    return True

def test_environment_variables():
    """Test that all required environment variables are set."""
    print("🔧 Testing environment variables...")
    
    required_vars = [
        'BLUESKY_HANDLE',
        'BLUESKY_APP_PASSWORD', 
        'OPENAI_API_KEY'
    ]
    
    # Optional Twitter API variables
    twitter_vars = [
        'TWITTER_BEARER_TOKEN',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET'
    ]
    
    # Check if any Twitter credentials are set
    twitter_configured = any(os.getenv(var) for var in twitter_vars)
    
    all_set = True
    # Test required variables
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    # Test Twitter variables
    print("\n🔍 Twitter API Configuration:")
    twitter_status = ""
    if twitter_configured:
        missing = [var for var in twitter_vars if not os.getenv(var)]
        if missing:
            print(f"⚠️  Twitter API partially configured. Missing: {', '.join(missing)}")
            twitter_status = "Partially Configured"
            
            # Check if at least Bearer Token is set (required for v2)
            if not os.getenv('TWITTER_BEARER_TOKEN'):
                print("❌ TWITTER_BEARER_TOKEN is required for Twitter API v2")
        else:
            print("✅ Twitter API v2 fully configured")
            twitter_status = "Fully Configured"
    else:
        print("ℹ️  Twitter API not configured (optional)")
        twitter_status = "Not Configured"
    
    return all_set, twitter_status

def main():
    """Run all tests."""
    print("🧪 Kramer Bot Test Suite")
    print("=" * 50)
    
    # Test environment variables
    env_ok, twitter_status = test_environment_variables()
    print()
    
    # Test OpenAI API
    openai_ok = test_quote_generation()
    print()
    
    # Test fallback quotes
    fallback_ok = test_fallback_quotes()
    
    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"Environment variables: {'✅' if env_ok else '❌'}")
    print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
    print(f"Fallback quotes: {'✅' if fallback_ok else '❌'}")
    print(f"Twitter API: {twitter_status}")
    
    if all([env_ok, openai_ok, fallback_ok]):
        print("\n🎉 All tests passed! The bot should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 