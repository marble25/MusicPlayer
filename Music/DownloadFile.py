__author__ = 'user'
import subprocess, os, urllib.request
from Music import MainFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT

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
if __name__=="__main__":
    while True:
        link="https://www.melon.com/song/detail.htm?songId=4296990"
        link=input("Link?")
        getmusic=MainFile.GetMusic()
        AlbumInfo=getmusic.getSongbyId(link)
        AlbumInfo=list(AlbumInfo)
        subprocess.call('youtube-dl -o "'+"/Music/file"+'.%(ext)s" --extract-audio --audio-format mp3 '+"https://www.youtube.com"+getmusic.getYoutubeLink(AlbumInfo[0], AlbumInfo[1]))
        lyrics=AlbumInfo[7]
        filename="Music/file.mp3"

        saveTag(AlbumInfo[8], AlbumInfo, filename, lyrics)
        #os.remove("Music/file.mp3")