from discord.ext import commands
import random
import praw

bot = commands.Bot(command_prefix='!')

reddit = praw.Reddit(client_id='my_client_id', client_secret='my_client_secret', user_agent='my_user_agent')

@bot.command(name="idea", help = "idea generator")
async def idea():
    await ctx.send("I love Kerim")

with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)