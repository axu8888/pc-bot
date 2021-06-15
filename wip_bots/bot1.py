from discord.ext import tasks, commands
from discord import Client
import pandas
import praw
import time
import asyncio
import discord
import nest_asyncio

nest_asyncio.apply()

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('Bot activated')
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.scrape())

    async def scrape(self):
        await self.wait_until_ready()
        channel = self.get_channel(411692488177483787)
        while not self.is_closed():
            for post in subreddit.new(limit=10):
                print("nice")
                await channel.send(post.title + " " +  post.url)
                await asyncio.sleep(5)

reddit = praw.Reddit(client_id='9qfv43B5Uu7bcA', client_secret='kfS26jo2EU8-XoafwFfK4LVmfxK6iA', user_agent = 'yodude8888')
subreddit = reddit.subreddit('buildapcsales')

client = MyClient()




with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    client.run(TOKEN)












