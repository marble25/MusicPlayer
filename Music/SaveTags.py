__author__ = 'user'
import glob, urllib.request, os, bs4
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT

link="https://www.melon.com/song/detail.htm?songId="
files=glob.glob("Music/▣*.mp3")
#files=glob.glob("C:/Users/user/Desktop/Music/▣*.mp3")
cnt=0
def saveTag(link, AlbumInfo, file, lyrics):
        print(link)
        print(AlbumInfo)
        fd=urllib.request.urlopen(link)
        audio=EasyID3(file)
        audio['title']=AlbumInfo[0]
        audio['artist']=AlbumInfo[1]
        audio['album']=AlbumInfo[2]
        audio['date']=AlbumInfo[3][:4]
        audio['genre']=AlbumInfo[4]
        audio.save()

        audio=MP3(file, ID3=ID3)
        audio.tags.add(
            APIC(
            encoding=3,
            mime='image/jpg',
            type=3,
            desc=u'Cover',
            data=fd.read()
            )
        )
        audio.save()
        audio=ID3(file)
        audio['USLT']=(USLT(encoding=3, text=lyrics))
        audio.save()
        if AlbumInfo[0].find("(")!=-1 and AlbumInfo[0].find(")")!=-1:
            print(AlbumInfo[0][:AlbumInfo[0].find("(")])
            print(AlbumInfo[0][AlbumInfo[0].rfind(")")+1:])
            AlbumInfo[0]=AlbumInfo[0][:AlbumInfo[0].find("(")]\
                         +AlbumInfo[0][AlbumInfo[0].rfind(")")+1:]
        if AlbumInfo[1].find("(")!=-1 and AlbumInfo[1].find(")")!=-1:
            AlbumInfo[1]=AlbumInfo[1][:AlbumInfo[1].find("(")]\
                         +AlbumInfo[1][AlbumInfo[1].rfind(")")+1:]
        fileRoute="Music/"+AlbumInfo[0].strip()+"-"+AlbumInfo[1].strip()+".mp3"
        fileRoute=fileRoute.replace("?", "#")
        if not os.path.isfile(fileRoute):
            os.rename(file, fileRoute)

for file in files:
    print(link+os.path.basename(file)[1:-4])

    response=urllib.request.urlopen(link+os.path.basename(file)[1:-4])
    cnt+=1
    soup=bs4.BeautifulSoup(response, "html.parser")

    Info=soup.findAll(attrs={"class":"song_info clfix"})[0].findAll('dd')
    Song=soup.findAll(attrs={"class":"songname"})[0].text.replace("곡명", "").replace("19금", "").strip()
    Artist=Info[0].text.strip()
    Album=Info[1].text.strip()
    Date=Info[2].text.strip()
    Genre=Info[3].text.strip()
    lyrics=soup.findAll(attrs={"id":"d_video_summary"})[0]
    lyrics=str(lyrics).replace('<div class="lyric" id="d_video_summary" style="height:auto;"><!-- height:auto; 로 변경시, 확장됨 -->', "").replace("<br>", "\n").replace("</br>", "").replace("</div>", "").strip()
    AlbumImg=soup.findAll(attrs={"id":"songImgArea"})[0].img['src']

    saveTag(AlbumImg, [Song, Artist, Album, Date, Genre], file, lyrics)