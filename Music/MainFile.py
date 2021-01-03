__author__ = 'user'

import urllib.request, glob, urllib.parse, bs4, subprocess, os, time
import csv, datetime
import threading
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT

class GetMusic:

    youtubeSite="https://www.youtube.com"

    def getYoutubeLink(self, Song, Singer):
        Song=str(Song)
        Singer=str(Singer)
        query=urllib.parse.quote(Song+" "+Singer+" audio")
        while True:
            try:
                urlYoutube=urllib.request.urlopen(self.youtubeSite+"/results?search_query="+query)
            except Exception as e:
                print(Song, e)
                continue
            else:
                break
        soupYoutube=bs4.BeautifulSoup(urlYoutube, "html.parser")
        listYoutube=soupYoutube.findAll(attrs={'class':"yt-uix-sessionlink yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 spf-link "})
        return (listYoutube[0]['href'], listYoutube[1]['href'], listYoutube[2]['href'])

    def savetoFile(self, AlbumInfo):
        nowtime=datetime.datetime.today().strftime("%Y%m%d")
        file=open("Music/Info/"+nowtime+".csv", "a", encoding='utf-8')
        cw=csv.writer(file, delimiter=',')
        cw.writerow([AlbumInfo[0], AlbumInfo[1], AlbumInfo[2]])
        print("SaveFileComplete")
        file.close()

    def process(self, Song, Singer, Album, Id):
        YoutubeLink=self.getYoutubeLink(Song, Singer)
        filename="/Music/▣"+Id
        for link in YoutubeLink:
            try:
                url=self.youtubeSite+link
                soup=bs4.BeautifulSoup(urllib.request.urlopen(url), "html.parser")
                title=soup.findAll(attrs={"id":"eow-title"})[0].text
                print(title)
                if title.count("Karaoke")!=0:
                    print("Errr")
                    raise Exception()
                print(filename)
                subprocess.call('youtube-dl -o "'+filename+'.%(ext)s" --extract-audio --audio-format mp3 '+self.youtubeSite+link)
                filesize=os.path.getsize(filename[1:]+".mp3")/(1024**2)
                if filesize<2 or filesize>10:
                    os.remove(filename[1:]+".mp3")
                    raise Exception()
            except Exception as e:
                print(e)
                continue
            else:
                break
        self.savetoFile((Song, Singer, Album))

    def savetolist(self):
        site="https://www.melon.com/chart/week/index.htm"
        url=urllib.request.urlopen(site)
        soup=bs4.BeautifulSoup(url, "html.parser")
        Songs=soup.findAll(attrs={'class':'ellipsis rank01'})
        Singers=soup.findAll(attrs={'class':'ellipsis rank02'})
        Albums=soup.findAll(attrs={'class':'ellipsis rank03'})

        return (Songs, Singers, Albums)
    def getSongbyId(self, Link):
        response=urllib.request.urlopen(Link)
        soup=bs4.BeautifulSoup(response, "html.parser")
        AlbumId=Link.strip("=")[1]
        Title=soup.findAll(attrs={"class":"songname"})[0].text.replace("곡명", "").strip().replace("19금\r\n\t\t\t\t\t\r\n\t\t\t\t\t\r\n\t\t\t\t\t", "")
        Singer=soup.findAll(attrs={"class":"atistname"})[0]['title']
        Album=soup.findAll(attrs={"class":"song_info clfix"})[0].findAll("dd")[1].a['title']
        Date=soup.findAll(attrs={"class":"song_info clfix"})[0].findAll("dd")[2].text[:4]
        Genre=soup.findAll(attrs={"class":"song_info clfix"})[0].findAll("dd")[3].text
        lyrics=soup.findAll(attrs={"id":"d_video_summary"})[0]
        lyrics=str(lyrics).replace('<div class="lyric" id="d_video_summary" style="height:auto;"><!-- height:auto; 로 변경시, 확장됨 -->', "").replace("<br>", "\n").replace("</br>", "").replace("</div>", "").strip()
        AlbumLink=soup.findAll(attrs={"class":"song_info clfix"})[0].findAll("dd")[1].a['href'].split("'")[1]
        AlbumImg=soup.findAll(attrs={"id":"songImgArea"})[0].img['src']
        print(Title, Singer, Album, Date, Genre)
        return (Title, Singer, Album, AlbumId, Date, Genre, AlbumLink, lyrics, AlbumImg)

    def fileRead(self):
        list=[]
        File_List=glob.glob("Music/Info/*.csv")
        for fileName in File_List:
            file=open(fileName, "r", encoding="utf-8")
            reader=csv.reader(file)
            for row in reader:
                if row == []:
                    continue
                list.append(row)
            file.close()
        return list

if __name__=="__main__":
    getmusic=GetMusic()
    list=getmusic.fileRead()
    Tuple = getmusic.savetolist()
    lyrics={}
    file=open("Music/Info/MelonTop100.csv", "w", encoding='utf-8')
    cw=csv.writer(file, delimiter=',')
    print(len(Tuple[0]))
    for i in range(0, 100):
        print(Tuple[0][i].span.strong.a.text, Tuple[1][i].a.text)
        cw.writerow([Tuple[0][i].span.strong.a.text+"-"+Tuple[1][i].a.text])
    file.close()
    print("Melon Top 100")
    for i in range(0, 100):
        flag=0
        AlbumInfo=(Tuple[0][i].span.strong.a.text, Tuple[1][i].a.text, Tuple[2][i].a.text, Tuple[0][i].span.strong.a['href'].split("'")[3])

        print(i, AlbumInfo[0])
        for l in list:
            if l[0]==AlbumInfo[0] \
                    and l[1]==AlbumInfo[1] \
                    and l[2]==AlbumInfo[2]:
                flag=1
                break
        if flag:
            continue

        t=threading.Thread(target=getmusic.process, args=(AlbumInfo))
        t.start()
    while threading.activeCount()>1:
        time.sleep(1)
    import SaveTags
    print("SaveAllFinished")