import os
import discord
from discord.ext import commands
import yt_dlp
from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

queue_list = {}
current_song = None
is_forced = False
is_skipping = False
current_stream_url = None

def create_embed(title, color, description=""):
    return discord.Embed(title=title, description=description, color=color)

async def get_youtube_url(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return (f"https://www.youtube.com/watch?v={info['entries'][0]['id']}", info['entries'][0]['url'], info['entries'][0]['title']) if 'entries' in info and info['entries'] else (None, None, None)

async def play_song(vc, query=None, ctx=None):
    global current_song, is_skipping, current_stream_url

    url, stream_url, title = await get_youtube_url(query)
    current_stream_url = stream_url
    if stream_url:
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 10 -nostdin',
            'options': '-vn'
        }
        try:
            vc.play(
                discord.FFmpegPCMAudio(stream_url, **ffmpeg_options),
                after=lambda e: bot.loop.create_task(play_next_with_error_handling(vc, ctx))
            )
        except Exception as ex:
            print(f"Error in play_song: {ex}")
            if ctx:
                await ctx.send(embed=create_embed("Error", discord.Color.red(), str(ex)))
        if ctx:
            await ctx.send(embed=create_embed("Now Playing", discord.Color.green(), "**" + title + "**" + " " + url) if not is_skipping else create_embed("Skipped to", discord.Color.orange(), "**" + title + "**" + " " + url))
            is_skipping = False
            current_song = f"**{title}** {url}"
    else:
        if ctx:
            await ctx.send(embed=create_embed("Error", discord.Color.red(), "Failed to retrieve stream URL."))

async def play_next_with_error_handling(vc, ctx=None):
    try:
        await play_next(vc, ctx)
    except Exception as e:
        print(f"Error in after callback: {e}")

# !help
@bot.hybrid_command(
    name='help',
    brief='Show all commands',
    description='Show all commands available'
)
async def help_command(ctx):
    embed = create_embed("Help", discord.Color.blue(), description="**List of all available commands:**")
    for command in bot.commands:
        embed.add_field(name=f'`/{command.name}`{f", `/{', /'.join(command.aliases)}`" if command.aliases else ""}', value=command.description, inline=False)
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

# !force <query>
@bot.hybrid_command(
    name='force',
    aliases=['f'],
    brief='Force play a song',
    description='Force play a song (replaces the current song if playing).'
)
async def force(ctx, *, query: str, do_defer=True):
    global is_forced
    if do_defer:
        is_forced = True
        await ctx.defer()

    if not query:
        await ctx.send(embed=create_embed("Error", discord.Color.light_grey(), "No query provided."))
        return

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

    vc.stop()
    await play_song(vc, query, ctx)

# !play <query>
@bot.hybrid_command(
    name='play',
    aliases=['p'],
    brief='Add a song to the queue',
    description='Add a song to the queue'
)
async def play(ctx, *, query: str):
    await ctx.defer()
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        await force(ctx, query=query, do_defer=False)
    else:
        url, _, title = await get_youtube_url(query)
        if url:
            queue_list[query] = url
            await ctx.send(embed=create_embed("Added to Queue", discord.Color.yellow(), f"**{title}** has been added to the queue."))
        else:
            await ctx.send(embed=create_embed("Error", discord.Color.red(), "No results found."))

# !now_playing
@bot.hybrid_command(
    name='now_playing',
    brief='Show the current song',
    description='Displays the current song.'
)
async def now_playing(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        await ctx.send(embed=create_embed("Currently Playing", discord.Color.orange(), current_song))
    else:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No song is currently playing."))

# !queue
@bot.hybrid_command(
    name='queue',
    brief='Show the queue',
    description='Displays the current queue.'
)
async def queue(ctx):
    embed = discord.Embed(title="Current Queue", color=discord.Color.blue())
    embed.add_field(name="Queue is empty", value="Add songs to the queue with `/play <query>`.") if not queue_list else [embed.add_field(name="", value=f"{i}. **{query}** {link}", inline=False) for i, (query, link) in enumerate(queue_list.items(), 1)]
    await ctx.send(embed=embed)

# !seek <time>
@bot.hybrid_command(
    name='seek',
    brief='Seek to a specific time',
    description='Seek to a specific time in the current song (in seconds)',
)
async def seek(ctx, time: int):
    global current_stream_url
    vc = ctx.voice_client
    if not vc or not vc.is_playing():
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No song is currently playing."))
        return

    ffmpeg_options = {
        "before_options": f"-ss {time}",
        "options": "-vn"
    }
    vc.stop()
    if current_stream_url:
        vc.play(discord.FFmpegPCMAudio(current_stream_url, **ffmpeg_options))
        await ctx.send(f"Seeked to {time} seconds.")
    else:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No current stream URL available."))

async def play_next(vc, ctx=None):
    global is_forced, current_song
    if is_forced:
        return

    if queue_list:
        query, _ = queue_list.popitem()
        await play_song(vc, query, ctx)
    else:
        current_song = None

# !skip
@bot.hybrid_command(
    name='skip',
    aliases=['s'],
    brief='Skip the current song',
    description='Skips the current song.'
)
async def skip(ctx):
    await ctx.defer()
    global is_skipping
    is_skipping = True
    if ctx.voice_client and ctx.voice_client.is_playing():
        if queue_list:
            ctx.voice_client.stop()
            await play_next(ctx.voice_client, ctx)
        else:
            await ctx.send(embed=create_embed("Error", discord.Color.red(), "No songs in the queue."))
    else:
        await ctx.send(embed=create_embed("Error", discord.Color.red(), "No song is currently playing."))

# !yt <query>
@bot.hybrid_command(
    name='yt',
    brief='Search YouTube for a video',
    description='Search YouTube for a video'
)
async def yt(ctx, *, query: str):
    _, link, _ = await get_youtube_url(query)
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

# additional features
@bot.hybrid_command(
    name='throw',
    aliases=['rzut'],
    brief='Throw a user',
    description='Throw a user'
)
async def throw(ctx, member: discord.Member, repeats: int = 1):
    channel = bot.get_channel(1321581483093131406)
    currentChannel = member.voice.channel
    if repeats > 10 or ctx.author.name == "digel2123":
        print(repeats)
        await ctx.send("https://media.discordapp.net/attachments/1122900157260894209/1129071902875455488/attachment.gif?ex=67984ee6&is=6796fd66&hm=671181dbbf90b49d2b8e50e8801105383b39efbfcf2fbab02a8b817b49efd2df&")
        return
    for _ in range(repeats):
        await member.move_to(channel)
        await member.move_to(currentChannel)
    await ctx.send(f"Threw {member.mention} {repeats} times.")

jajco_count = 0
@bot.event
async def on_message(message):
    global jajco_count
    if bot.user.mentioned_in(message):
        await message.channel.send("**SHUT THE FUCK UP :face_with_symbols_over_mouth:**")
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

bot.run(DISCORD_TOKEN)