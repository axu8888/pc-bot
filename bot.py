from discord.ext import tasks, commands
import pandas
import praw
import time
import asyncio
import discord




# @bot.command(name = "scrape")
# async def scrape():
#     print("i am here")
#     subreddit = reddit.subreddit('buildapcsales')
#     channel = bot.get_channel(411692488177483787)
#     if(channel == None):
#         print("channel is None")
#     for post in subreddit.new(limit=10):
#         # for word in keywords:
#         #     temp = word.lower()
#         #     if temp in post.title:
#         print("nice")
#         await channel.send(post.title + " " +  post.url)
#     await asyncio.sleep(5)

client = discord.Client()
bot = commands.Bot(command_prefix='!')
reddit = praw.Reddit(client_id='9qfv43B5Uu7bcA', client_secret='kfS26jo2EU8-XoafwFfK4LVmfxK6iA', user_agent = 'yodude8888')



def get_channel(channels, channel_name):
    for channel in client.get_all_channels():
        if channel.name == channel_name:
            return channel
    return None

client = discord.Client()
general_channel = get_channel(client.get_all_channels(), 'general')


@bot.event
async def on_ready():
    print("fjaewoifjoaweifjaoweifjaweoifjweoaif")
    bot.loop.create_task(scrape())


async def scrape():
    #await bot.wait_until_ready()
    subreddit = reddit.subreddit('buildapcsales')

    channel = bot.get_channel(411692488177483787)
    while not client.is_closed:
        for post in subreddit.new(limit=10):
            # for word in keywords:
            #     temp = word.lower()
            #     if temp in post.title:
            print("nice")
            await channel.send(post.title + " " +  post.url)
            await asyncio.sleep(5)





@bot.command(name="idea", help = "idea generator")
async def notify(ctx):
    await ctx.send("I love Kerim")

# @bot.event
# async def on_ready():
#     print("pog")

with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)




# hot_posts = subreddit.top("day",limit=10)
# for post in hot_posts:
#     print(post.title)


keywords = ['b550', '3080', '5800x', '5600x', '3080 ti', '3070', '3080']

dict = {}










