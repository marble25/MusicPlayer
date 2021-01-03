__author__ = 'user'
import sys, glob
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import os, random, threading, wave, pygame, time

form_class=uic.loadUiType("MusicPlayer.ui")[0]
class PlayThread(QThread):
    duration=0
    def __init__(self, duration):
        super().__init__()
        self.duration=duration
    def run(self):
        while pygame.mixer.music.get_busy():
            nowTime=pygame.mixer.music.get_pos()
            nowPos=(nowTime/self.duration/10)
            nowTimeText=str(int(nowTime/1000/60))+":"+str(int((nowTime/1000)%60))
            self.emit(SIGNAL("timeChange(QString, int)"),nowTimeText, int(nowPos))
            time.sleep(0.1)
        self.emit(SIGNAL("nextMusic()"))
    def quitMethod(self):
        self.terminate()
class Window(QMainWindow, form_class):
    thread=None
    files=None
    flag=False
    started=False
    duration=0
    def closeEvent(self, e):
        pygame.mixer.music.stop()
        print("End")
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.files=glob.glob("Music/*.mp3")
        self.setupUi(self)
        self.connect(self.lineEdit, SIGNAL("textChanged(QString)"), self.findMusic)
        self.connect(self.Button_Next, SIGNAL("clicked()"), self.nextMusic)
        self.connect(self.Button_Back, SIGNAL("clicked()"), self.nextMusic)
        self.connect(self.Button_Play, SIGNAL("clicked()"), self.playMusic)
        self.connect(self.MusicLists,
                     SIGNAL("itemDoubleClicked(QListWidgetItem *)"),
                     self.changeSong)
    def findMusic(self, Query):
        self.MusicLists.clear()
        for file in self.files:
            if str(file).lower().find(str(Query).lower())!=-1:
                self.MusicLists.addItem(os.path.basename(file).replace(".mp3", ""))
    def initMusic(self, file):
        audio=EasyID3(file)
        self.Text_Album.setText(audio['album'][0])
        self.Text_Artist.setText(audio['artist'][0])
        self.Text_Genre.setText(audio['genre'][0])
        self.Text_Date.setText(audio['date'][0])
        self.Text_Title.setText(audio['title'][0])

        audio=MP3(file, ID3=ID3)

        img=open('AlbumArt.jpg', 'wb')
        img.write(audio['APIC:Cover'].data)
        img.close()

        pixmap=QPixmap("AlbumArt.jpg")
        self.AlbumArt.setPixmap(pixmap)
        self.AlbumArt.setScaledContents(True)
        os.remove("AlbumArt.jpg")

        audio=ID3(file)
        lyrics=str(audio['USLT:None:\x00\x00\x00']).split("\n")
        self.Lyrics.clear()
        for lyric in lyrics:
            self.Lyrics.addItem(lyric)
    def timeChange(self, nowTimeText, nowPos):
        self.Text_Time_0.setText(nowTimeText)
        self.Slider.setValue(nowPos)
    def playMusic(self):
        if self.started:
            if not self.flag:
                print("StartPlaying")
                self.Button_Play.setText("||")
                pygame.mixer.music.unpause()
                self.flag=True
                return
            else:
                print("StopPlaying")
                self.Button_Play.setText("▶")
                pygame.mixer.music.pause()
                self.flag=False
                return
        if self.Text_Album.text()=="Album":
            return
        file="Music/"+self.Text_Title.text()+".mp3"

        if os.path.isfile("Music/temp.wav"):
            pygame.mixer.music.load("Music/temp1.wav")
            os.remove("Music/temp.wav")
        os.system('ffmpeg -i "'+file+'" Music/temp.wav')

        self.started=True
        self.flag=True
        self.Button_Play.setText("||")
        waveFile=wave.open("Music/temp.wav", "rb")
        print(waveFile.getframerate())

        pygame.mixer.quit()
        pygame.mixer.init(waveFile.getframerate(), -16, 1, 1024)
        frames=waveFile.getnframes()
        rate=waveFile.getframerate()
        self.duration=int(frames/float(rate))
        waveFile.close()
        pygame.mixer.music.load("Music/temp.wav")
        pygame.mixer.music.play()
        print("Success!!")
        self.Text_Time.setText(str(int(self.duration/60))+":"+str(int(self.duration%60)))
        self.thread=PlayThread(self.duration)
        self.connect(self.thread, SIGNAL("timeChange(QString, int)"), self.timeChange)
        self.connect(self.thread, SIGNAL("nextMusic()"), self.nextMusic)
        self.thread.start()
    def nextMusic(self):
        file=self.files[random.randrange(0, len(self.files))]
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if self.thread:
            self.thread.quitMethod()
        self.initMusic(file)
        self.started=False
        self.playMusic()
    def changeSong(self, Item):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        file="Music/"+QListWidgetItem(Item).text()+".mp3"
        if self.thread is not None:
            self.thread.quitMethod()
        self.initMusic(file)
        self.started=False
        self.playMusic()
    def listSongs(self):
        for file in self.files:
            self.MusicLists.addItem(os.path.basename(file).replace(".mp3", ""))
if __name__=="__main__":
    app=QApplication(sys.argv)
    myWindow=Window()
    myWindow.listSongs()
    myWindow.show()
    app.exec_()