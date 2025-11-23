#!/usr/bin/env python3
"""
Test script for Kramer Bot - generates quotes without posting to Bluesky
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_quote_generation():
    """Test the quote generation functionality."""
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    genai.configure(api_key=gemini_api_key)
    
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
        print("🤖 Testing Gemini API connection...")
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        quote = response.text.strip()
        
        # Clean up the quote
        if quote.startswith('"') and quote.endswith('"'):
            quote = quote[1:-1]
        
        print("✅ Gemini API connection successful!")
        print(f"📝 Generated quote: {quote}")
        print(f"📏 Character count: {len(quote)}")
        
        if len(quote) > 281:
            print("⚠️  Warning: Quote exceeds 281 character limit (Twitter limit)")
        else:
            print("✅ Quote within 281 character limit (Twitter compatible)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False

def test_fallback_quotes():
    """Test the fallback quote system."""
    print("\n🔄 Testing fallback quotes...")
    
    fallback_quotes = [
        "I'm out there, Jerry, and I'm loving every minute of it!",
        "Giddyup!",
        "My friend Bob Sacamano called me at 3 AM. He says the sewers are the new subway!",
        "I'm implementing a reverse-peephole. I want to see what's going on in my own apartment when I'm not there!",
        "The kavorka, Jerry! The lure of the animal! I'm dangerous!",
        "I'm retiring! I'm moving to Del Boca Vista! I'm gonna be in the pool, I'm gonna be in the clubhouse, I'm gonna be all over that shuffleboard court!"
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
        'GEMINI_API_KEY'
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
    
    # Test Gemini API
    gemini_ok = test_quote_generation()
    print()
    
    # Test fallback quotes
    fallback_ok = test_fallback_quotes()
    
    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"Environment variables: {'✅' if env_ok else '❌'}")
    print(f"Gemini API: {'✅' if gemini_ok else '❌'}")
    print(f"Fallback quotes: {'✅' if fallback_ok else '❌'}")
    print(f"Twitter API: {twitter_status}")
    
    if all([env_ok, gemini_ok, fallback_ok]):
        print("\n🎉 All tests passed! The bot should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()