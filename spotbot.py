from discord.ext import tasks, commands
from discord import Client
import discord
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import psycopg2

#TO DO: add database functionality (probability PostGreSQL)
#User table with favorite artists

#load .env file
load_dotenv('.env')

#initialize bot
bot = commands.Bot(command_prefix='!')


#connect to Spotify API
cid = os.getenv('SPOTIFY_CID')
secret = os.getenv('SPOTIFY_SECRET')
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


#connect to PostgreSQL db
db = psycopg2.connect(
    host = "localhost",
    dbname = "newReleases",
    user = "postgres",
    password = "247478",
    port = "5432"
)



results = sp.search("Joji")
artist_uri = results['tracks']['items'][0]['artists'][0]['uri']
sp_albums = sp.artist_albums(artist_uri, album_type='album')
print(sp_albums['items'][0]['release_date'])


@bot.command(name="search", help = "Search for artist")
async def search(ctx, *args):
    name = ''.join(args[:])
    results = sp.search(name)
    print(results)
    artist_uri = ""
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


@bot.command(name = "register")
async def info(ctx):
    conn = db.cursor()

    conn.execute("SELECT userid from users where userid = %s", (ctx.author.id,))
    results = conn.fetchall()
    if(len(results)==0):
        try:
            conn.execute("INSERT INTO users (userid, username) VALUES(%s, %s)", (ctx.author.id, ctx.author.name))
            await ctx.send("User successfully registered")
        except:
            await ctx.send("Error registering. Please try again")
    else:
        await ctx.send("User already registered")
    
    # await ctx.send("id: " + str(ctx.author.id))
    # await ctx.send("username: " + ctx.author.name)
    conn.execute("SELECT * from users where userid = %s", (ctx.author.id,))
    results = conn.fetchall()

    embed = discord.Embed(title='Current User', colour = discord.Colour.red())
    embed.add_field(name = "userId", value = results[0][0], inline = True)
    embed.add_field(name = "username", value = results[0][1], inline = True)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

    db.commit()
    conn.close()


#TODO : add functionality to check first/last name and give suggestions

#Add artist to database
@bot.command(name = "add")
async def favorite(ctx, *args):
    name = ''.join(args[:])
    name = name.lower()
    conn = db.cursor()
    

    conn.execute("SELECT LOWER(name) from artist where name = %s", (name,))
    query_results = conn.fetchall()
    spotify_results = sp.search(name)
    if(len(spotify_results['items'])==0): #check if in spotify database
        await ctx.send("No Artist Found")
        return
    artist_uri = spotify_results['tracks']['items'][0]['artists'][0]['uri'] 
    artist_name = spotify_results['tracks']['items'][0]['artists'][0]['name']
    if(len(query_results)==0):   #check if not in postgresql database
        conn.execute("INSERT INTO artists (name, URI) VALUES(%s, %s)", (artist_name, artist_uri))
    
    #check for new releases/add to database
    sp_albums = sp.artist_albums(artist_uri, album_type='album')

    album_names = []
    album_uris = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
        album_uris.append(sp_albums['items'][i]['uri'])
        conn.execute("INSERT INTO albums (name, URI) VALUES(%s, %s)", (artist_name, artist_uri))


    album_names = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
    
    await ctx.send(album_names)
    

    conn.execute("""SELECT songs.name from 
                    users natural join 
                    favorites natural join 
                    artists natural join 
                    creates natural join albums 
                    natural join songs""")





with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)