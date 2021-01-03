__author__ = 'user'
import glob, os
import urllib.request
from shutil import move
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT

class MusicCoverUpdate:
    path="C:/Users/user/OneDrive/음악/▣*.mp3"
    def __init__(self, songs):
        self.files=glob.glob(self.path)
        self.songs=songs

    def changeTags(self):
        for song in self.songs:
            for file in self.files:
                if os.path.basename(file)[1:-4]==str(song['songId']):
                    audio=EasyID3(file)
                    audio['title']=song['songName'].translate(str.maketrans('.?:$}', "#####"))
                    audio['artist']=", ".join(song['artists'])
                    audio['album']=song['albumName'].translate(str.maketrans('.?:$}', "#####"))
                    audio['date']=song['releaseDate']
                    audio['genre']=song['genre']
                    audio.save()

                    fd=urllib.request.urlopen(song['albumImg'])
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
                    audio['USLT']=(USLT(encoding=3, text=song['lyrics']))
                    audio.save()
                    move(file, "C:/Users/user/OneDrive/음악/"+song['songName'].translate(str.maketrans('.?:$}', "#####"))+"-"+", ".join(song['artists'])+".mp3")
                    break
