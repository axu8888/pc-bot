from discord.ext import tasks, commands
from discord import Client
import pandas as pd
import praw
import time
import asyncio
import discord
import nest_asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

#TO DO: add database functionality (probability PostGreSQL)
#User table with favorite artists


load_dotenv('.env')

bot = commands.Bot(command_prefix='!')

cid = os.getenv('SPOTIFY_CID')
secret = os.getenv('SPOTIFY_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

results = sp.search("Phil Wickham")
artist_uri = results['tracks']['items'][0]['artists'][0]['uri']


sp_albums = sp.artist_albums(artist_uri, album_type='album')
album_names = []
for i in range(len(sp_albums['items'])):
    album_names.append(sp_albums['items'][i]['name'])
print(album_names)


@bot.command(name="search", help = "Search for artist")
async def search(ctx, *args):
    name = ''.join(args[:])
    results = sp.search(name)

    try:
        artist_uri = results['tracks']['items'][0]['artists'][0]['uri']
    except:
        await ctx.send("No Artist Found")

    sp_albums = sp.artist_albums(artist_uri, album_type='album')

    album_names = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
    
    await ctx.send(album_names)



num_new = 5
# new_songs = sp.new_releases(None, num_new, 0)
# print(new_songs)

song_dic = {}

song_dic['artist names'] = []
song_dic['spotify links'] = []
song_dic['album names'] = []

# print(new_songs['albums']['items'][i])

fav_artists = set(["Jeremy Camp", 'Billie Eilish', 'The Worship Initiative', 'Pat Barrett', "Shane & Shane", "Hillsong United", "Hillsong Worship", "Hillsong Young & Free", "Maverick City Music,"])



@bot.command(name = "new")
async def new(ctx):
    end_flag = 0

    for i in range(0, 1000, num_new):    
        new_songs = sp.new_releases(None, num_new, i)
        for j in range(num_new):
            try:
                curr_info = new_songs['albums']['items'][j]
            except:
                print("Reached end of new releases")
                print(f"{i+j} new releases")
                end_flag = 1
                break
            artist_name = curr_info['artists'][0]['name']
            if(artist_name in fav_artists):
                song_dic['artist names'].append(artist_name) #artist name
                song_dic['spotify links'].append(curr_info['external_urls']['spotify'])  #spotify link
                song_dic['album names'].append(curr_info['name'])  #album/song name
        if(end_flag):
            break

    # if"Pat Barrett" in song_dic['artist names']:
    #     print("found!")

    df = pd.DataFrame.from_dict(song_dic)
    await ctx.send(df)


@bot.command(name = "angel")
async def angel(ctx, artist : str):
    new_release = sp.new_releases(None, 50, 0)
    song_dic = {}
    song_dic['artist names'] = []

    for i in range(50):
        song_dic['artist names'].append(new_release['albums']['items'][i]['artists'][0]['name'])

    for i, t in enumerate(song_dic['artist names']):
        if t == artist:
            await ctx.send(t['name'])

@bot.command(name = "login")
async def info(ctx):
    await ctx.send(ctx.author.id)
    await ctx.send(ctx.author.name)

# def getTrackIDs()



with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)