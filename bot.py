import discord
from discord.ext import commands

BOT_TOKEN = "MTA4MjczOTkyNDAyMjg2MTg1Ng.Gtg1cD.QIgWEVho2SGOvH_-WEyL8-qPeFPvkCUVwudvQY"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.channel.send("SHUT THE FUCK UP")

jajco_count = {}

@bot.hybrid_command()
async def jajco(ctx, user: discord.User):
    if not user:
        await ctx.send("Wprowadź nazwę użytkownika")
        return
    user_id = str(user.id)
    jajco_count[user_id] = jajco_count.get(user_id, 0) + 1
    await ctx.send(f"{user.mention} ilość jajec to {jajco_count[user_id]}.")

async def jajcoCheck(ctx, user: discord.User):
    if not user:
        await ctx.send("Wprowadź nazwę użytkownika")
        return
    user_id = str(user.id)
    await ctx.send(f"{user.mention} ilość jajec to {jajco_count[user_id]}.")

bot.run(BOT_TOKEN)