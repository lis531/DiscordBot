# Discord bot
This discord bot is my own discord bot which adds functionality that you would have to normally pay. You can feel free to use it on your own!
## Features
- Queue songs
- Seek through music
- Force song play
- Search videos from youtube
## How to use
- `/play <song>`: Adds a song to the queue
- `/force`: Forces the song to play
- `/seek <time>`: Seeks through the song
- `/queue`: Shows the queue
- `/skip`: Skips the current song
- `/leave`: Leaves the voice channel
- `/yt <search>`: Searches for a video on youtube
- `/help`: Shows the help menu
- `/ping`: Pings the bot
## Requirements
- Python 3.x
- Discord account
- Discord bot token
- discord.py, yt-dlp, PyNaCl and python-dotenv packages
## Installation
1. Clone the repo.
2. Run install.bat or install the requirements manually.
3. Create a developer application on the Discord Developer Portal and create a bot.
   - Go to the "Bot" tab and click "Add Bot".
   - Copy the bot token.
   - Invite the bot to your server using the OAuth2 URL with the `bot` scope and appropriate permissions.
4. Create the .env file with your bot token like this (if creating manually):
   ```
   DISCORD_TOKEN=your_token_here
   ```
   Replace `your_token_here` with your actual Discord bot token.
5. Run the bot with `py main.py`.