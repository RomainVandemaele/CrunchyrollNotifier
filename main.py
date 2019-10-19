from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import os

from lxml.html import fromstring
from itertools import cycle
import traceback
from ip2geotools.databases.noncommercial import DbIpCity

animes = []
day = datetime.today().weekday()
dayDict = {0 : "Monday",1:"Tuesday",2:"Wednesday",3:"Thrusday",4:"Friday",5:"Saterday",6:"Sunday"}

"""
Script used to parse the site Crunchyroll toget notified when a new episode is released on their US version. It was created because the site as no public API.
It is my first project that parse html and proxies. That explain its simplicity and small scale. Notheless it was nice to do and explore a new facet of programming
"""

def get_proxies(range):
    """
    Look through US free proxy
    """
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:range]:
        if i.xpath('.//td[7][contains(text(),"yes")]') and i.xpath('.//td[3][contains(text(),"US")]') : #and i.xpath('.//td[5][contains(text(),"elite")]') :
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

def parseHTML():
    """
    Obtain list of anime and release times
    """
    proxies = set()
    range = 1000
    while len(proxies) == 0 :
        proxies = get_proxies(range)
        range += 100
    proxy = proxies.pop()
    error = True
    #Go through the list of obtained proxies and test if it is not blacklisted or else try the next one
    while error and len(proxies) > 0:
        try :
            resp = requests.get("https://www.crunchyroll.com/simulcastcalendar?filter=free",proxies={"http": 'http://' + proxy, "https": 'https://' +proxy})
            if "Access denied" in resp.text :
                raise ConnectionRefusedError("Aces denied")
            error = False
        except :
            proxy = proxies.pop()
            if len(proxies) == 0 :
                proxies = get_proxies(range)
    link = resp.text
    html = BeautifulSoup(link,'lxml')
    articles = html.find_all('article')
    times = html.find_all('time')

    for article in articles :
        if article.attrs != None :
            attr = article.attrs
            if "data-slug" in attr : #get article with useful information
                animeName = attr["data-slug"].replace('-',' ')
                if attr["data-episode-num"].isdigit() :
                    epNbr = int(attr["data-episode-num"]) + 1
                else :
                    epNbr = 0
                animes.append([animeName,epNbr])
    count = 0
    for time in times :
        if time.attrs != None :
            attr = time.attrs
            if 'class' in attr and attr['class'][0] == 'available-time' :
                h = time.text
                suffix = h[len(h)-2:]
                h = h[:len(h)-2].split(':')
                h = [int(h[0]),int(h[1])]
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
    """
    Infinite loop checking periodically if an anime has released and send OS notification if that is the case
    """
    todayAnimes = []
    for anime in animes :
        if anime[4] == day :
            print(anime[0],anime[2],anime[3])
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
