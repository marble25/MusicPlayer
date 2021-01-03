__author__ = 'user'
import DownloaderMain, MusicPlay
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import os, sys, urllib.request, urllib.error, datetime, glob, csv
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

formClass=uic.loadUiType("MusicPlayer.ui")[0]

# Controller Model
class Controller:

    def __init__(self, view):
        # 네트워크 확인하기
        self.ping=self.checkPing()

        self.downloaderMain=DownloaderMain.DownloaderMain(self.ping)
        self.musicPlay=MusicPlay.MusicPlay(self, view)
        self.view=view

    # 선택된 음악을 플레이
    def playMusic(self, fileName, index):
        self.musicPlay.setSongs(self.songs)
        self.musicPlay.setSong(fileName)
        self.musicPlay.setCurrentIndex(index)
        self.musicPlay.daemon=True
        self.musicPlay.play()

    # Song Setter
    def setSongs(self, arg_songs=None):
        self.songs=list()

        if arg_songs is None:
            self.songs=self.songsOriginal

        elif arg_songs is not None:
            self.songs=arg_songs
            self.songsOriginal=arg_songs

        if not self.isDownloadedAll():
            self.view.showWarning(1)

    # Song Getter
    def getSong(self, index):
        if self.isDownloadedAll():
            fileName="C:/Users/user/OneDrive/음악/"+self.songs[index][5]+".mp3"

            audio=MP3(fileName, ID3=ID3)

            img=open('AlbumArt.jpg', 'wb')
            img.write(audio['APIC:Cover'].data)
            img.close()

            audio=ID3(fileName)
            lyrics=str(audio['USLT:None:\x00\x00\x00']).split("\n")

            song=dict()
            song['songName']=self.songs[index][0]
            song['albumName']=self.songs[index][1]
            song['artist']=self.songs[index][2]
            song['releaseDate']=str(self.songs[index][3])
            song['genre']=self.songs[index][4]
            song['fileName']=self.songs[index][5]
            song['lyrics']=lyrics

            return song

        return None

    # 네트워크 체크하기
    def checkPing(self):
        try:
            response=urllib.request.urlopen('http://www.google.com',timeout=3)
            return True
        except urllib.error.URLError as err: pass
        return False

    # Scene이 보여질 때, 리스트에 다 넣기
    def setTodayTopList(self):

        if self.checkPing(): # 네트워크 연결될 때
            self.songsOriginal=self.downloaderMain.getTop100List()
        else: # 네트워크 연결 안될 때
            self.songsData=self.downloaderMain.getTop100ListFromDatabase()
            self.songsOriginal=list()
            for song in self.songsData:
                songData=dict()
                songData['albumName']=song[1]
                songData['songName']=song[0]
                self.songsOriginal.append(songData)

        self.setSongs()
        return self.songsOriginal

    # 모두 다운로드되었는지 체크하기
    def isDownloadedAll(self):

        result=self.downloaderMain.dataBase.search(self.songsOriginal, mode=1)

        if result is None:
            return False

        self.songs=result
        return True

    # tab 2의 파일 다운로드
    def downloadSelectedFile(self, melonLink, youtubeLink):

        self.downloaderMain.downloadSelectedFile(melonLink, youtubeLink)

    # tab 1의 파일 다운로드
    def downloadFiles(self):

        (self.songs, downloadList)=self.downloaderMain.setAdditionalInfo(self.songsOriginal)
        self.downloaderMain.download(self.songs, downloadList)
        self.downloaderMain.updateTags(self.songs)
        self.setSongs()

    def pauseMusic(self):
        if self.musicPlay.player.playing:
            self.musicPlay.pause()
        else:
            self.musicPlay.resume()

    def randomSelect(self, value):
        self.musicPlay.isRandom=value

    def repeatSelect(self, value):
        self.musicPlay.isRepeat=value

    def volumeChange(self, value):
        self.musicPlay.volumeChange(int(value))

    def nextMusic(self):
        self.musicPlay.nextMusic()

    def prevMusic(self):
        self.musicPlay.prevMusic()

# View Model
class View(QMainWindow, formClass):

    def __init__(self):
        super().__init__()

        self.controller=Controller(self)
        self.setupUi(self)

        self.d=datetime.date.today()

        self.spinBox_Year.setValue(self.d.year)
        self.spinBox_Month.setValue(self.d.month)
        self.spinBox_Day.setValue(self.d.day)

        self.setTodayTopList()

        self.connect(self.button_DownloadTop100, SIGNAL("clicked()"), self.checkDownload)
        self.connect(self.button_DownloadFile, SIGNAL("clicked()"), self.downloadSelectedFile)
        self.connect(self.list_Top100, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.changeSong)
        self.connect(self.button_Play, SIGNAL("clicked()"), self.playMusic)
        self.connect(self.button_Next, SIGNAL("clicked()"), self.nextMusic)
        self.connect(self.button_Back, SIGNAL("clicked()"), self.prevMusic)
        self.connect(self.checkBox_Random, SIGNAL("stateChanged(int)"), self.randomSelectChange)
        self.connect(self.checkBox_Repeat, SIGNAL("stateChanged(int)"), self.repeatSelectChange)
        self.connect(self.slider_Volume, SIGNAL("valueChanged(int)"), self.volumeValueChange)
        self.connect(self.lineEdit_Find, SIGNAL("textChanged(QString)"), self.findMusic)
        self.connect(self.button_ListOK, SIGNAL("clicked()"), self.getPastList)

    # 오늘의 목록 저장하기
    def saveTodayTopList(self, songs):

        filename="logs/"+str(self.d.year)+"."+str(self.d.month)+"."+str(self.d.day)+".csv"
        files=glob.glob(filename)

        if len(files)!=0:
            return

        csv_file=open(filename, "w", encoding="UTF-8")
        cw=csv.writer(csv_file, delimiter=",")

        for song in songs:
            cw.writerow([song['songName'], ",".join(song['artists']), song['albumName']])

        csv_file.close()

        print("File Save Complete")

    # tab 1 - 1위부터 100위까지 세팅하기
    def setTodayTopList(self, songs=None):

        if songs is None:
            songs=self.controller.setTodayTopList()
        else:
            self.controller.setSongs(songs)

        self.list_Top100.clear()

        for i in range(0, 100):
            self.list_Top100.addItem(str(i+1)+" "+songs[i]['songName'])

        self.saveTodayTopList(songs)

    # tab 1 - 모두 다운로드되었는지 체크하기
    def checkDownload(self):

        if not self.controller.isDownloadedAll():
            self.controller.downloadFiles()

    # tab 1 - 리스트 아이템 선택될 때 재생하기
    def changeSong(self, Item):

        index=int(Item.text().split()[0])
        song=self.controller.getSong(index-1)
        self.changeSongInfo(song)
        self.controller.playMusic(song['fileName'], index-1)

    # tab 2 - 선택된 파일 다운로드하기
    def downloadSelectedFile(self):

        melonLink=self.lineEdit_MelonLink.text()
        youtubeLink=self.lineEdit_YoutubeLink.text()
        self.controller.downloadSelectedFile(melonLink, youtubeLink)

    # 태그 정보에 맞게 보여주기
    def changeSongInfo(self, song):

        pixmap=QPixmap("AlbumArt.jpg")
        self.label_AlbumArt.setPixmap(pixmap)
        self.label_AlbumArt.setScaledContents(True)
        os.remove("AlbumArt.jpg")

        self.label_Album.setText(song['albumName'])
        self.label_Artist.setText(song['artist'])
        self.label_Date.setText(song['releaseDate'])
        self.label_Genre.setText(song['genre'])

        self.label_Title.setText(song['songName'])

        self.list_Lyrics.clear()
        for lyric in song['lyrics']:
            self.list_Lyrics.addItem(lyric)

    def playMusic(self):
        self.controller.pauseMusic()

    def nextMusic(self):
        self.controller.nextMusic()

    def prevMusic(self):
        self.controller.prevMusic()

    def randomSelectChange(self, value):
        if str(value)=="2":
            self.controller.randomSelect(True)
        else:
            self.controller.randomSelect(False)

    def repeatSelectChange(self, value):
        if str(value)=="2":
            self.controller.repeatSelect(True)
        else:
            self.controller.repeatSelect(False)

    def volumeValueChange(self, value):
        self.controller.volumeChange(value)

    def getPastList(self):
        year=self.spinBox_Year.value()
        month=self.spinBox_Month.value()
        day=self.spinBox_Day.value()

        filename="logs/"+str(year)+"."+str(month)+"."+str(day)+".csv"
        print(filename)
        file=glob.glob(filename)

        if len(file)==0:
            self.showWarning(2)
            return

        else:
            csv_file=open(filename, "r", encoding="UTF-8")
            reader=csv.reader(csv_file)
            songs=list()

            for row in reader:
                if len(row)==0:
                    continue
                songs.append(dict({"songName": row[0], "artists" : row[1], "albumName" : row[2]}))

            self.setTodayTopList(songs)

    def findMusic(self, string):

        self.list_Top100.clear()
        songs=self.controller.songs
        for i in range(len(songs)):
            for info in songs[i]:
                if str(info).lower().find(string.lower()) != -1:
                    self.list_Top100.addItem(str(i+1)+" "+songs[i][0])
                    break

    def showWarning(self, mode):

        if mode==1:
            QMessageBox.about(self, "Warning", "다운로드가 완료되지 않았습니다.\n다운로드를 먼저 눌러주세요")
        elif mode==2:
            QMessageBox.about(self, "Warning", "해당 일자에 해당하는 파일이 없습니다")

    def closeEvent(self, event):
        self.controller.musicPlay.pause()
        os.kill(os.getpid(), 9)

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=View()
    window.show()
    app.exec_()