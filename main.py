from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import os

animes = []
day = datetime.today().weekday()
dayDict = {0 : "Monday",1:"Tuesday",2:"Wednesday",3:"Thrusday",4:"Friday",5:"Saterday",6:"Sunday"}

proxies = {
  'http': 'http://162.252.96.65:8080', #GMT-9 9 hours less than here
  'https': 'http://34.94.147.20:3128',
}

def parseHTML():
    resp = requests.get("https://www.crunchyroll.com/simulcastcalendar?filter=free",proxies=proxies)
    link = resp.text
    html = BeautifulSoup(link,'lxml')
    articles = html.find_all('article')
    times = html.find_all('time')

    for article in articles :
        if article.attrs != None :
            attr = article.attrs
            if "data-slug" in attr : #get article with useful information
                animeName = attr["data-slug"].replace('-',' ')
                epNbr = int(attr["data-episode-num"]) + 1
                animes.append([animeName,epNbr])
                #print(animeName+ " " + str(epNbr) )
    count = 0
    for time in times :
        if time.attrs != None :
            attr = time.attrs
            if 'class' in attr and attr['class'][0] == 'available-time' :
                h = time.text
                suffix = h[len(h)-2:]
                h = h[:len(h)-2].split(':')
                h = [int(h[0]),int(h[1])]
                #print(h,suffix) 
                if(suffix == "pm" and h[0]!=12) :
                    h[0] =  int(h[0])+12 
                offset = 0
                h[0] += 9
                if(h[0] >= 24) :
                    h[0] = h[0]%24
                    offset = 1
                animes[count].append(int(h[0]))
                animes[count].append(int(h[1]))

                date = attr['datetime'][:10].split("-") #format YYYY-MM-DD
                day = ( datetime(int(date[0]),int(date[1]),int(date[2])).weekday() + offset ) %7
                animes[count].append(day)
                animes[count].append(False)
                count+=1
    
    
def checkrelease() :
    todayAnimes = []
    for anime in animes :
        if anime[4] == day :
            print(anime[0] + " " + str(anime[2]) + ":" + str(anime[3]) + " day " + dayDict[anime[4]] )
            todayAnimes.append(anime)
    while True :
        now = datetime.now()
        for anime in todayAnimes :
            if( ( anime[2] < now.hour or  (anime[2] == now.hour and anime[3] <= now.minute ) ) and anime[5] == False) :
                os.system("notify-send " + "\"" + anime[0] + " " + str(anime[1]) + " is available since " + str(anime[2]) + ":" + str(anime[3]) + "\"")
                anime[5] = True
        time.sleep(5*60) 


if __name__ == '__main__':
    parseHTML()
    checkrelease()