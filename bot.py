from discord.ext import commands
import discord

BOT_TOKEN = "MTA4MjczOTkyNDAyMjg2MTg1Ng.Gtg1cD.QIgWEVho2SGOvH_-WEyL8-qPeFPvkCUVwudvQY"
CHANNEL_ID = 1085689119713284209

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello World")

@bot.event
async def on_message(message):
    if message.author.id == 438396518375096320:
        custom_emoji = bot.get_emoji(1085690437056073728)
        await message.add_reaction(custom_emoji)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Hello!")

bot.run(BOT_TOKEN)
