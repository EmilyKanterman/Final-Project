from urllib.request import Request
from urllib.request import urlopen
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import requests
import json
import sqlite3
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json
import os

#get base url and initialize Beautiful Soup
url='https://www.imdb.com/list/ls076828102/'
def getSoupObjFromURL(url):
    """ return a soup object from the url """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req, context=ctx).read() # Line modified
    soup = BeautifulSoup(html, "html.parser")
    return soup
soup = getSoupObjFromURL(url)

#create a dictionary of the top 100 artists from imdb top 100 chart
#make the key the title of the song
#and values the artist name and the ranking in a list
def scrape(soup):
    imdb={}
    table_container=soup.find('div',class_='lister list detail sub-list')
    table=table_container.find('div', class_='lister-list')
    songs=table.find_all('div', class_='lister-item mode-detail')
    for song in songs:
        #find artist of song
        content=song.find('div', class_='lister-item-content')
        song_info=content.find("h3", class_="lister-item-header")
        artist=song_info.a.text
        a=artist.strip()

        #find title of song
        title_info=song.find('div', class_='list-description')
        title=title_info.find('p')
        t= title.text.strip()

        #find ranking of the song
        rank_info=song.find('span', class_="lister-item-index unbold text-primary")
        r=rank_info.text
        x=r.strip('. ')
        ranking=int(x)
        
        #make dictionary where title is the key and the artist and the ranking is the value
        imdb[t]=[a, ranking]
    return imdb
scrape(soup)

#set up the cache to write to json file
f = open('imdb_cache.json','w')
f.write(json.dumps(scrape(soup)))
f.close()

def make_database():
        try:
            conn=sqlite3.connect('music.sqlite')
            cur=conn.cursor()
        except:
            print('Could not connect')
        statement='''
        DROP TABLE IF EXISTS 'Imdb';
        '''
        cur.execute(statement)
        conn.commit()
        statement= '''CREATE TABLE 'Imdb' (song TEXT, artist TEXT, ranking INTEGER)'''
        cur.execute(statement)
        conn.commit()
        conn.close()
make_database()

def populate_database():
        conn=sqlite3.connect('music.sqlite')
        cur=conn.cursor()

        for song in scrape(soup).keys():
                t = song
                artist = scrape(soup)[t][0]
                ranking = int(scrape(soup)[t][1])
                cur.execute('''INSERT INTO 'Imdb' (song, artist, ranking)
                 VALUES (?,?,?)''', (t,artist,ranking))
        conn.commit()
populate_database()

conn=sqlite3.connect('music.sqlite')
cur=conn.cursor()

queen_lst=[]
for song in cur.execute("SELECT song FROM Imdb WHERE artist = 'Queen'"):
        queen_lst.append(song)

print(len(queen_lst))

fleetwood_lst = []
for song in cur.execute("SELECT song FROM Imdb WHERE artist = 'Fleetwood Mac'"):
        fleetwood_lst.append(song)

print(len(fleetwood_lst))

creedence_lst = []
for song in cur.execute("SELECT song FROM Imdb WHERE artist = 'Creedence Clearwater Revival'"):
        creedence_lst.append(song)

print(len(creedence_lst))

x="Queen"
y="Fleetwood Mac"
z="Creedence Clearwater Revival"
d={}
d[x]=queen_lst
d[y]=fleetwood_lst
d[z]=creedence_lst


l=open('classic_artists.json', 'w')
l.write(json.dumps(d))
l.close()

xvals = ['Queen', 'Fleetwood Mac', 'Creedence Clearwater Revival']
yvals = [len(queen_lst),len(fleetwood_lst),len(creedence_lst)]

plt.bar(xvals, yvals, align='center', color= ['pink', 'green', 'orange'])
#3.Give ylabel to the plot
plt.ylabel("# of Songs in the Top 100 Imdb list")
#4.Give xlabel to the plot
plt.xlabel("Classic Artists")
#5.Give the title to the plot
plt.title("How Many Songs Do The Classic Artists Have in the Top 100 Imdb List?")
#6.Save the plot as a .png file
plt.savefig('classic_artists.png')

plt.show()













