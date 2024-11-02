import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp as youtube_dl

BOT_TOKEN = "MTA4MjczOTkyNDAyMjg2MTg1Ng.Gtg1cD.QIgWEVho2SGOvH_-WEyL8-qPeFPvkCUVwudvQY"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.hybrid_command()
async def ping(ctx):
    await ctx.send(str(round(bot.latency * 1000)) + "ms")

async def get_first_youtube_result(query):
    videosSearch = VideosSearch(query, limit=1)
    result = videosSearch.result()
    if result['result']:
        return result['result'][0]['link']
    return None

@bot.hybrid_command()
async def play_on_channel(ctx, query):
    channel = ctx.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel.")
        return

    link = await get_first_youtube_result(query)
    if not link:
        await ctx.send("No results found.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3')

    if ctx.voice_client:
        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(filename))
    else:
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(filename))

@bot.hybrid_command()
async def yt(ctx, query):
    link = await get_first_youtube_result(query)
    if link:
        await ctx.send(link)
    else:
        await ctx.send("No results found.")

@bot.hybrid_command()
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        vc.stop()
        await vc.disconnect()

jajco_count = 0

@bot.event
async def on_message(message):
    global jajco_count
    if bot.user.mentioned_in(message):
        print("Mentioned")
        await message.channel.send("SHUT THE FUCK UP")
    if message.content == "jajco":
        jajco_count += 1
        await message.channel.send("Ilość jajec: " + str(jajco_count))
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.run(BOT_TOKEN)