# Kramer Bot 🤖

A Bluesky bot that automatically posts fictional Cosmo Kramer quotes every 3 hours, as if he were living in 2025 and experiencing modern technology and culture.

## Features

- **Automatic posting**: Posts every hour using a scheduler
- **AI-generated quotes**: Uses gpt-4o-mini to create unique, in-character Kramer quotes
- **Duplicate prevention**: Caches recent posts to avoid repeats
- **Modern context**: Quotes reference current technology (AirPods, TikTok, AI, Zoom, etc.)
- **Easy deployment**: Ready to deploy,
- **Fallback system**: Includes backup quotes if AI generation fails

## Example Quotes

- "I tried to make my own oat milk… I milked the oats, Jerry! But they just got soggy!"
- "You ever been in a Zoom breakout room, Jerry? It's like being trapped in an elevator… with no buttons!"
- "I sold my neighbor an NFT of his own front door. It's art, Jerry!"
- "I was tracking my steps with a smart ring… now it thinks I'm a hummingbird!"

## Setup

### Prerequisites

1. **Bluesky Account**: You need a Bluesky account and an App Password
2. **OpenAI API Key**: For generating quotes with gpt-4o-mini

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Kramer-Bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```
   BLUESKY_HANDLE=your-handle.bsky.social
   BLUESKY_APP_PASSWORD=your-app-password
   OPENAI_API_KEY=your-openai-api-key
   ```

4. **Run the bot**:
   ```bash
   python kramer_bot.py
   ```

### Bluesky App Password Setup

1. Go to [Bluesky Settings](https://bsky.app/settings)
2. Navigate to "App Passwords"
3. Create a new app password
4. Use this password in your `.env` file

## Deployment on Render.com

1. **Connect your repository** to Render.com
2. **Create a new Worker Service**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python kramer_bot.py`
   - **Environment**: Python

4. **Add environment variables** in Render dashboard:
   - `BLUESKY_HANDLE`
   - `BLUESKY_APP_PASSWORD`
   - `OPENAI_API_KEY`

5. **Deploy**! The bot will start posting every 3 hours.

## Configuration

### Posting Schedule
The bot posts every 1 hour by default. To change this, modify the schedule in `kramer_bot.py`:

```python
schedule.every(1).hours.do(self.post_quote)
```

### Quote Generation
- **Character limit**: 300 characters max
- **AI model**: gpt-4o-mini
- **Temperature**: 0.9 (for creativity)
- **Fallback quotes**: 15 pre-written quotes if AI fails

### Duplicate Prevention
- **Cache size**: Last 100 posts
- **Storage**: JSON file (`recent_posts.json`)
- **Retry attempts**: Up to 10 attempts for unique quotes

## File Structure

```
Kramer-Bot/
├── kramer_bot.py          # Main bot script
├── requirements.txt       # Python dependencies
├── render.yaml           # Render.com deployment config
├── env.example           # Environment variables template
├── README.md            # This file
└── recent_posts.json    # Generated cache file
```

## Logging

The bot logs all activities to:
- **Console output**: Real-time logs
- **File**: `kramer_bot.log`

## Customization

### Adding More Fallback Quotes
Edit the `get_fallback_quote()` method in `kramer_bot.py`:

```python
fallback_quotes = [
    "Your new quote here, Jerry!",
    # ... existing quotes
]
```

### Modifying the AI Prompt
Edit the `generate_kramer_quote()` method to change the quote style or topics.

### Changing Post Frequency
Modify the scheduler in `run_scheduler()` method.

## Troubleshooting

### Common Issues

1. **Authentication errors**: Check your Bluesky handle and app password
2. **API rate limits**: The bot includes retry logic for OpenAI API
3. **Duplicate posts**: Check the `recent_posts.json` cache file
4. **Deployment issues**: Ensure all environment variables are set in Render

### Logs
Check the logs for detailed error information:
```bash
tail -f kramer_bot.log
```

## Contributing

Feel free to submit issues or pull requests to improve the bot!

## License

This project is open source. Feel free to use and modify as needed.

---

*"I'm telling you, Jerry, this bot is going to be huge!"* - Cosmo Kramer