from bs4 import BeautifulSoup
import requests

def parseHTML():
    resp = requests.get("https://www.crunchyroll.com/simulcastcalendar?filter=free")
    link = resp.text
    html = BeautifulSoup(link,'lxml')
    articles = html.find_all('article')
    for article in articles :
        if article.attrs != None :
            attr = article.attrs
            if "data-slug" in attr :
                animeName = attr["data-slug"]
                animeName = animeName.replace('-',' ')
                epNbr = int(attr["data-episode-num"]) + 1
                print(animeName+ " " + str(epNbr) )

if __name__ == '__main__':
    parseHTML()
