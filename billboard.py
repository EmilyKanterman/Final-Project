#import BeautifulSoup
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
url = 'https://www.billboard.com/charts/hot-100/'
def getSoupObjFromURL(url):
    """ return a soup object from the url """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # Line added

    html = urlopen(req, context=ctx).read() # Line modified
    soup = BeautifulSoup(html, "html.parser")
    return soup

soup = getSoupObjFromURL(url)
#create a dictionary of the top 100 charts
#make the key the song title
#and values the artist and ranking on the chart

def scrape(soup):
        billboard = {}
        lst_of_everything = soup.find_all('div',class_ = 'chart-list-item')
        for song in lst_of_everything:
                #create a song title variable
                song_info = song.find('div', class_ = 'chart-list-item__title')
                song_title = song_info.span.text
                #create an artist variable
                artist_info = song.find('div', class_ = 'chart-list-item__artist')
                artist = artist_info.text
                #create a ranking variable
                ranking_info = song.find('div', class_ = 'chart-list-item__rank')
                ranking = ranking_info.text
                #add these into the dictionary
                billboard[song_title.strip()] = [artist.strip(), ranking.strip()]
        return billboard

scrape(soup)


#this isn't used but could possibly be useful -- shows the weeks on the top 100 chart
lst = []
for x in soup.find_all('div', class_="chart-list-item__weeks-on-chart"):
        lst.append(x.text)

f = open('billboard_cache.json','w')
f.write(json.dumps(scrape(soup)))
f.close()

def make_database():
        try:
                conn=sqlite3.connect('music.sqlite')
                cur=conn.cursor()
        except:
                print('Could not connect')
        statement='''
        DROP TABLE IF EXISTS 'Billboard';
        '''
        cur.execute(statement)
        conn.commit()
        statement= '''CREATE TABLE 'Billboard' (song TEXT, artist TEXT, ranking INTEGER)'''
        cur.execute(statement)
        conn.commit()
        conn.close()

make_database()

def populate_database():
        conn=sqlite3.connect('music.sqlite')
        cur=conn.cursor()

        for song in scrape(soup).keys():
                song_title = song
                artist_name = scrape(soup)[song_title][0]
                rankings = int(scrape(soup)[song_title][1])
                cur.execute('''INSERT INTO 'Billboard' (song, artist, ranking)
                 VALUES (?,?,?)''', (song_title,artist_name,rankings))
        conn.commit()

populate_database()


ari_lst = []
#for song in scrape(soup).keys():
        #if 'Ariana Grande' in scrape(soup)[song][0]:
                #ari_lst.append(song)



conn=sqlite3.connect('music.sqlite')
cur=conn.cursor()

for song in cur.execute("SELECT song FROM Billboard WHERE artist = 'Ariana Grande'"):
        ari_lst.append(song)

print(len(ari_lst))

post_lst = []
for song in cur.execute("SELECT song FROM Billboard WHERE artist = 'Post Malone'"):
        post_lst.append(song)

print(len(post_lst))

billie_lst = []
for song in cur.execute("SELECT song FROM Billboard WHERE artist = 'Billie Eilish'"):
        billie_lst.append(song)

print(len(billie_lst))

x = 'Ariana Grande'
y = 'Post Malone'
w = 'Billie Eilish'
d = {}
d[x] = ari_lst
d[y] = post_lst
d[w] = billie_lst


z = open('fav_artists.json','w')
z.write(json.dumps(d))

xvals = ['Ariana Grande', 'Post Malone', 'Billie Eilish']
yvals = [len(ari_lst),len(post_lst),len(billie_lst)]

plt.bar(xvals, yvals, align='center', color= ['pink', 'purple', 'blue'])
#3.Give ylabel to the plot
plt.ylabel("# of Solo Songs in the Hot 100")
#4.Give xlabel to the plot
plt.xlabel("Favorite Artists")
#5.Give the title to the plot
plt.title("How Many Solo Songs Do Our Favorite Artists Have in the Top 100?")
#6.Save the plot as a .png file
plt.savefig('top100.png')

plt.show()
