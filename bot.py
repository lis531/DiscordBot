import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp
import os

BOT_TOKEN = "MTA4MjczOTkyNDAyMjg2MTg1Ng.Gtg1cD.QIgWEVho2SGOvH_-WEyL8-qPeFPvkCUVwudvQY"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

queue_list = []
current_audio_file = None

def create_embed(title, color, description=""):
    return discord.Embed(title=title, description=description, color=color)

async def download_youtube_video(link):
    for file in os.listdir("downloaded_songs"):
        os.remove(os.path.join("downloaded_songs", file))
        print(f"Removed: {file}")
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'outtmpl': f'downloaded_songs/%(id)s.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link if link.startswith('https://www.youtube.com') else await get_first_youtube_result(link), download=True)
            filename = f"downloaded_songs/{info['id']}.mp3"
            return filename
    except Exception as e:
        print(f"Download error: {e}")
        return None

# !help
@bot.hybrid_command(
    name='help',
    brief='Show all commands',
    description='Show all commands available'
)
async def help_command(ctx):
    embed = create_embed("Help", discord.Color.blue(), description="**List of all available commands:**")
    for command in bot.commands:
        embed.add_field(name=f"!{command.name}{", " + str(command.aliases) if command.aliases else ""}", value=command.description, inline=False)
    await ctx.send(embed=embed)

# !ping
@bot.hybrid_command(
    name='ping',
    brief='Check bot latency',
    description='Check bot latency in milliseconds'
)
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(embed=create_embed("Ping", discord.Color.green() if latency < 50 else discord.Color.orange() if latency < 100 else discord.Color.red(), str(latency) + "ms"))

async def get_first_youtube_result(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    return result['result'][0]['link'] if result['result'] else None

async def play_song(vc, link):
    global current_audio_file
    current_audio_file = await download_youtube_video(link)
    if current_audio_file:
        vc.play(discord.FFmpegPCMAudio(current_audio_file), after=lambda e: bot.loop.create_task(play_next(vc)))
    else:
        print("Failed to download song.")

# !play <query>
@bot.hybrid_command(
    name='force',
    aliases=['f'],
    brief='Force play a song',
    description='Force play a song (replaces the current song if playing).'
)
async def force(ctx, *, query: str):
    global is_playing
    global current_audio_file
    await ctx.defer()

    if not query:
        await ctx.send(embed=create_embed("Error", discord.Color.light_grey(), "No query provided."))
        return
    if not ctx.author.voice.channel:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "You are not connected to a voice channel."))
        return

    channel = ctx.author.voice.channel
    current_audio_file = await download_youtube_video(query)

    if not current_audio_file:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "Failed to download the song."))
        return

    if ctx.voice_client:
        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(current_audio_file))
    else:
        if not ctx.voice_client:
            vc = await channel.connect()
        else:
            vc = ctx.voice_client
            if not vc.is_connected():
                await vc.move_to(channel)
        vc.play(discord.FFmpegPCMAudio(current_audio_file))
    await ctx.send(embed=create_embed("Now Playing", discord.Color.green(), query))

# !play <query>
@bot.hybrid_command(
    name='play',
    aliases=['p'],
    brief='Add a song to the queue',
    description='Add a song to the queue'
)
async def play(ctx, *, query: str):
    await ctx.defer()

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "You are not connected to a voice channel."))
        return
    
    channel = ctx.author.voice.channel
    
    if ctx.voice_client is None:
        vc = await channel.connect()
    else:
        vc = ctx.voice_client
        if not vc.is_connected():
            await vc.move_to(channel)

    link = await get_first_youtube_result(query)
    if not vc.is_playing():
        await play_song(vc, link)
    if link:
        queue_list.append(link)
        await ctx.send(embed=create_embed("Added to Queue", discord.Color.yellow(), f"**{query}** has been added to the queue."))
    else:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No results found."))

# !queue
@bot.hybrid_command(
    name='queue', 
    brief='Show the queue',
    description='Displays the current queue.'
)
async def queue(ctx):
    embed = discord.Embed(title="Current Queue", color=discord.Color.blue())
    embed.add_field(name="Queue is empty", value="Add songs to the queue with `/play <query>`.") if not queue_list else [embed.add_field(name="", value=str(i) + ". " + link, inline=False) for i, link in enumerate(queue_list, 1)]
    await ctx.send(embed=embed)

current_audio_file = None

# !seek <time>
@bot.hybrid_command(
    name='seek',
    brief='Seek to a specific time',
    description='Seek to a specific time in the current song (in seconds)',
)
async def seek(ctx, time: int):
    global current_audio_file
    vc = ctx.voice_client
    if not vc.is_playing():
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No song is currently playing."))
        return

    ffmpeg_options = {
        "before_options": f"-ss {time}",
        "options": "-vn"
    }
    vc.stop()
    vc.play(discord.FFmpegPCMAudio(current_audio_file, **ffmpeg_options))
    await ctx.send(f"Seeked to {time} seconds.")

async def play_next(vc):
    if queue_list:
        print(queue_list)
        next_link = queue_list.pop(0)
        print(f"Playing next song: {next_link}")
        await play_song(vc, next_link)
    else:
        await vc.disconnect()
        print("Queue ended, bot disconnected.")

# !skip
@bot.hybrid_command(
    name='skip',
    aliases=['s'],
    brief='Skip the current song',
    description='Skips the current song.'
)
async def skip(ctx):
    await ctx.defer()
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await play_next(ctx.voice_client)
        await ctx.send(embed=create_embed("Skipped", discord.Color.blue(), "Skipped to the next song."))
    else:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No song is currently playing."))

# !yt <query>
@bot.hybrid_command(
    name='yt',
    brief='Search YouTube for a video',
    description='Search YouTube for a video'
)
async def yt(ctx, *, query: str):
    link = await get_first_youtube_result(query)
    if link:
        await ctx.send(link)
    else:
        await ctx.send("No results found.")

# !leave
@bot.hybrid_command(
    name='leave',
    aliases=['disconnect'],
    brief='Leave the voice channel',
    description='Leave the voice channel'
)
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        vc.stop()
        await vc.disconnect()
        await ctx.send(embed=create_embed("Disconnected from the voice channel.", discord.Color.red()))

jajco_count = 0

@bot.event
async def on_message(message):
    global jajco_count
    if bot.user.mentioned_in(message):
        print("Mentioned")
        await message.channel.send("SHUT THE FUCK UP")
    if "jajco" in message.content.lower():
        jajco_count += 1
        await message.channel.send(embed=create_embed("Ilość jajec", discord.Color.green(), str(jajco_count)))
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print("Syncing commands...")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(BOT_TOKEN)