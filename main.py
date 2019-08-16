from bs4 import BeautifulSoup
from datetime import datetime
import requests

animes = []
day = datetime.today().weekday()
dayDict = {0 : "Monday",1:"Tuesday",2:"Wednesday",3:"Thrusday",4:"Friday",5:"Saterday",6:"Sunday"}

def parseHTML():
    resp = requests.get("https://www.crunchyroll.com/simulcastcalendar?filter=free")
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
                animes[count].append(time.text)
                date = attr['datetime'][:10].split("-") #format YYYY-MM-DD
                day = datetime(int(date[0]),int(date[1]),int(date[2])).weekday()
                animes[count].append(day)

                count+=1
    print(count)


if __name__ == '__main__':
    parseHTML()
    for anime in animes :
        print(anime[0]+ " episode " + str(anime[1]) + " will be available at "+ anime[2] + " on " + dayDict[anime[3]])
