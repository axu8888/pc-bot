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


# connect to PostgreSQL db
db = psycopg2.connect(
    host = os.getenv('HOST'),
    dbname = os.getenv('DB_NAME'),
    user = os.getenv('USER'),
    password = os.getenv('PASSWORD'),
    port = os.getenv('PORT')
)

conn = db.cursor()



# try:
#     a = 'a'
#     b = 'b'
#     conn.execute("INSERT INTO artists (uri, name) VALUES(%s, %s)", (a, b))  #order of column names matters
#     print("here")
# except:
#     print("error")

#returns true if d1 is >= d2, meaning if d1 is more recent than d2
def compare_dates(d1, d2):
    d1 = d1.split('-')
    d2 = d2.split('-')
    for i in range(len(d1)):
        if(int(d1[i])>int(d2[i])):
            return True
        elif(int(d1[i])<int(d2[i])):
            return False
    return True


@bot.command(name="search", help = "Search for artist")
async def search(ctx, *args):
    name = ' '.join(args[:])
    
    results = sp.search(name)
    
    artists = ""
    try:
        artists = results['tracks']['items'][0]['artists']
    except:
        await ctx.send("No Artist Found")


    artist_uri = ""
    for i in range(len(artists)):
        print(i)
        if(name.lower() in artists[i]['name'].lower()):
            artist_uri = artists[i]['uri']
            break
    if(artist_uri == ''):
        await ctx.send("No Artist Found")
    sp_albums = sp.artist_albums(artist_uri)

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
    name = ' '.join(args[:])
    conn = db.cursor()
    

    spotify_results = sp.search(name)
    name = name.lower()

    try:
        artists = spotify_results['tracks']['items'][0]['artists']
    except:
        await ctx.send("No Artist Found")  #check if in spotify database
        return
    artist_uri = ""
    artist_name = ""  #artist name in spotify database
    for i in range(len(artists)):
        if(name.lower() in artists[i]['name'].lower()):
            artist_uri = artists[i]['uri']
            artist_name = artists[i]['name']
            break
    print(artist_name)
    print(artist_uri)
    if(artist_uri == ''):
        await ctx.send("No Artist Found")
        return
    # artist_uri = spotify_results['tracks']['items'][0]['artists'][0]['uri'] 
    # artist_name = spotify_results['tracks']['items'][0]['artists'][0]['name']

    #check if not in postgresql database
    conn.execute("SELECT artistid from artists where name = %s", (artist_name,))
    query_results = conn.fetchall()
    artist_id = -1
    if(len(query_results)==0):   
        await ctx.send("Artist successfully added")
        conn.execute("INSERT INTO artists (uri, name) VALUES(%s, %s)", (artist_uri, artist_name))
        
        conn.execute("SELECT artistid FROM artists WHERE artists.name = %s", (artist_name,))
        results = conn.fetchall()
        artist_id = results[0][0]

        conn.execute("""INSERT INTO favorites (userid, artistid)
                        VALUES(%s, %s)
                    """, (ctx.author.id, artist_id))
    else:
        artist_id = query_results[0][0]
        await ctx.send("Artist already added")

    #check for new releases/add to database
    sp_albums = sp.artist_albums(artist_uri)
    album_uris = []

    await ctx.send("New Releases")  #embed?

    sp_albums = sp_albums['items']
    album_set = ()
    prev = "hopefully no album is named this"

    #albums ordered by date (most recently added), so compare with most recent date
    conn.execute("""SELECT releasedate FROM albums
                    WHERE releasedate >= ALL(SELECT releasedate FROM albums)""")
    results = conn.fetchall()
    most_recent = '00-00-0000'
    if(len(results) != 0):
        most_recent = results[0][0]

    for i in range(len(sp_albums)):  #for each album
        curr_name = sp_albums[i]['name']

        #check for duplicates on same date
        if(prev == curr_name):
            continue
        prev = curr_name
        curr_uri = sp_albums[i]['uri']
        curr_release = sp_albums[i]['release_date']

        album_uris.append(curr_uri)
        try:
            #if release date is only year, just set to January 1st
            if('-' not in curr_release):
                curr_release = curr_release + '-01-01'

            #if current release is not new release (not in database)
            if(compare_dates(curr_release, most_recent) == False):
                return

            conn.execute("INSERT INTO albums (name, uri, releasedate) VALUES(%s, %s, %s)", (curr_name, 
                                                                                        curr_uri, 
                                                                                        curr_release))
            #await ctx.send(curr_name + " " + curr_uri + " " + curr_release)
            conn.execute("SELECT albumid FROM albums where albums.uri = %s", (curr_uri,))
            results = conn.fetchall()
            album_id = results[0][0]
            conn.execute("INSERT INTO creates (artistid, albumid) VALUES(%s, %s)", (artist_id, album_id))

            tracks = sp.album_tracks(curr_uri)['items']
            print(len(tracks))
            for i in range(len(tracks)):
                song_name = tracks[i]['name']
                song_uri = tracks[i]['uri']
                conn.execute("INSERT INTO songs (albumid, name, uri) VALUES(%s, %s, %s)", (album_id, song_name, song_uri))
                #await ctx.send(curr_name + " " + song_name + " " + song_uri)
        except:
            continue
        
        
    

    # conn.execute()
    # for uri in album_uris:
    db.commit()
    conn.close()   
    
@bot.command(name = "show", help = 'Show artists and their albums')
async def show(ctx, arg):
    if(arg.lower() == 'artists'):
        conn.execute("""SELECT artists.name from 
                        users natural join favorites 
                        natural join artists
                        """)
        artists = conn.fetchall()
        for artist in artists:
            await ctx.send(artist)
    elif(arg.lower() == 'songs'):
        conn.execute("""SELECT songs.name from 
                        users natural join 
                        favorites natural join 
                        artists natural join 
                        creates natural join albums 
                        natural join songs""")
    elif():
        await ctx.send("Invalid Command")




with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)