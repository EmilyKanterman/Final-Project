import requests
import json
from newsapi import NewsApiClient
from collections import defaultdict
import sqlite3
newsapi = NewsApiClient(api_key='131d9c5b07674440ab948ba13c011d68')
#Get all the articles that mention song titles in Peri's List from Billboard Charts and make this into a for loop"
def get_CNN_data(d):
    key_words=["music", "song", "top", "chart", "Billboard", "lyrics", "artist", "popular"]
    new_d=defaultdict(list)
    for song in d:
        all_articles = newsapi.get_everything(q=song,
                                      sources='cnn',
                                    #   from_param='2017-12-01',
                                    #   to='2017-12-12',
                                      language='en',
                                      sort_by='relevancy')
        # print(all_articles)
        for article in all_articles["articles"]:
            description=article["description"]
            
            #print(type(description))
            for word in description.split():
                if word in key_words:
                    #print(song)
                    id_=article["source"]["id"]
                    author=article["author"]
                    title=article["title"]
                    info=(id_, author, title, description)
                    new_d[song].append(info)
            for word in article["title"]:
                if word in key_words:
                  id_=article["source"]["id"]
                  author=article["author"]
                  title=article["title"]
                  info=(id_, author, title, description)
                  new_d[song].append(info)
    return new_d
  
    
with open("billboard_cache.json", "r") as read_file:
  data = json.load(read_file)
  print(data.keys())

di={"Old Town Road", "Body", "breathin'", "Hello"}
print(get_CNN_data(data.keys()))
for i in get_CNN_data(data.keys()):
  print(i)
  print()
print(len(get_CNN_data(data.keys())))

#conn=sqlite3.connect('CNN.sqlite')
#cur=conn.cursor()
#cur.execute('DROP TABLE ')