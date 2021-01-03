import glob, os
import DataBase, FileDownload, MusicCoverUpdate, WebConnect
from mutagen.easyid3 import EasyID3


files=glob.glob("C:/Users/user/OneDrive/음악/*.mp3")
database=DataBase.DataBase()
database.deleteAll()
for file in files:
    audio=EasyID3(file)
    filename=os.path.basename(file)[:-4]
    title=(None if audio.get("title") is None else "".join(audio.get("title")))
    album=(None if audio.get("album") is None else "".join(audio.get("album")))
    artist=(None if audio.get("artist") is None else "".join(audio.get("artist")))
    date=(None if audio.get("date") is None else "".join(audio.get("date")))
    genre=(None if audio.get("genre") is None else "".join(audio.get("genre")))

    database.insert(title, album, artist, date, genre, filename)

database.showAll()
