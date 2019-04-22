from urllib.request import Request
from urllib.request import urlopen
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import requests
import json
import sqlite3
import re
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import os
#import Plotly_Key

from IPython.display import IFrame
IFrame(src= "https://dash-simple-apps.plotly.host/dash-figurelabelsplot/", width="100%", height="650px", frameBorder="0")

#plotly.__version__
#plotly.tools.set_credentials_file(username='landauha', api_key=Plotly_Key.api_key)

# Get base url and initialize Beautifup Soup
url = 'https://spotifycharts.com/regional'
def getSoupObjFromURL(url):
    """Return a soup object from the url"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = Request(url, headers = {'User-Agent': 'Mozilla/5.0'}) # Line added

    html = urlopen(req, context=ctx).read() # Line modified
    soup = BeautifulSoup(html, "html.parser")
    return soup

soup = getSoupObjFromURL(url)

# Create a dictionary of the top 200 songs
# Make the key the song title
# and the values the artists, position on chart, and amount of times streamed

spotify = {}
lst_of_everything = soup.find('table', class_ = 'chart-table') # Need to check these are the proper titles
lst_of_songs = lst_of_everything.find_all('tr')
for song in lst_of_songs[1:]:
    # Create a song title variable
    song_info = song.find('td', class_ = 'chart-table-track')
    song_title = song_info.strong.text
    # Create an artist variable
    artist_info = song.find('td', class_ = 'chart-table-track')
    artist = artist_info.span.text.strip('by ')
    #print(artist_info)
    # Create a position variable
    position_info = song.find('td', class_ = 'chart-table-position')
    position = position_info.text
    #print(position_info)
    # Create a streams variable
    stream_info = song.find('td', class_ = 'chart-table-streams')
    stream = stream_info.text
    #print(stream_info)
    # Add these into the dictionary
    spotify[song_title.strip()] = (artist.strip(), position.strip(), stream.strip())

#print(spotify)

# Set up Cache
f = open('spotify_cache_scatter.json', 'w')
f.write(json.dumps(spotify))
f.close()

conn = sqlite3.connect('music.sqlite')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Spotify (song TEXT, artist TEXT, position INTEGER, streams INTEGER)')

for song in spotify.keys():
    song_title = song
    artist_name = spotify[song_title][0]
    positions = int(spotify[song_title][1])
    streams = spotify[song_title][2]
    cur.execute('''INSERT OR IGNORE INTO Spotify (song, artist, position, streams) VALUES (?,?,?,?)''', (song_title, artist_name, positions, streams))
conn.commit()

# make a list of song positions
positions_lst = []
for song in spotify.values():
    positions_lst.append(song[1])

# make a list of # of streams
streams_lst = []
for song in spotify.values():
    streams_lst.append(song[2])

trace = go.Scatter(x = positions_lst, y = streams_lst, mode = 'markers')

data = [trace]
#axis_template = dict(title = "How Many Times Has Each Top 200 Song on Spotify Been Played?")
#layout = go.Layout(xaxis = axis_template, yaxis = axis_template)
layout =  go.Layout(
    title=go.layout.Title(
        text="How Many Times Has Each Top 200 Song on Spotify Been Played?",
        font=dict(
                family='Arial',
                size=18,
                color='#000000'
            ),
        xref='paper',
        x=0
    ),
    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text='Position on Spotify Top 200',
            font=dict(
                family='Arial',
                size=18,
                color='#000000'
            )
        )
    ),
    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='# of Streams',
            font=dict(
                family='Arial',
                size=18,
                color='#000000'
            )
        )
    )
)

fig = go.Figure(data = data, layout = layout)

py.iplot(fig, filename = 'Spotify_Scraping', auto_open=True)
