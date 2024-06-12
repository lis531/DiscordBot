import discord
from discord.ext import commands

BOT_TOKEN = "MTA4MjczOTkyNDAyMjg2MTg1Ng.Gtg1cD.QIgWEVho2SGOvH_-WEyL8-qPeFPvkCUVwudvQY";

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all());

@bot.event
async def on_ready():
    print("Bot is ready")

# @bot.command(name='rzut')
# async def rzut(ctx, member: discord.Member = None):
#     print("Rzuca");
#     """Rzuca"""
#     if member:
#         for channel in ctx.guild.channels:
#             if isinstance(channel, discord.VoiceChannel) and channel.name == "Jail":
#                 await member.move_to(channel)
#                 await ctx.send(f"{member.mention} has been moved to Jail!")
#                 break;

jajco_count = 0

@bot.hybrid_command(name="first_slash")
async def first_slash(ctx): 
   await ctx.send("You executed the slash command!")

@bot.event
async def on_message(message):
    global jajco_count;
    if bot.user.mentioned_in(message):
        await message.channel.send("SHUT THE FUCK UP")
    if message.content == "jajco":
        jajco_count += 1;
        await message.channel.send("Ilość jajec: " + str(jajco_count))
        
bot.run(BOT_TOKEN)