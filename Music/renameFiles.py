__author__ = 'user'
import glob, os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, USLT
files=glob.glob("Music/*.mp3")
for file in files:
    print(os.path.basename(file)[0:-4])
    audio=EasyID3(file)
    print(audio['title'])
    print(audio['artist'])