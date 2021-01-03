__author__ = 'user'
import sys, glob, os, random, time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import operator, pyglet, csv

files=list() # Get All Files
fileInfoList=list() # List of All Files contains Title, Singer, Year
filesByTop=list() # List sorted by Melon Top 100
filesByABC=list() # List sorted by ABC
filesByYear=list() # List sorted by Year
filesBySinger=list() # List sorted by Singer
filesByYearDict=dict() # Dict binded to Year
musiclists=list() # Current Playing List

fileRoute="C:/Users/user/OneDrive/음악" # The Folder which contains all of the musics
infoFolderRoute="D:/Grade_2/PyCharmProjects/Test/Music/Music/Info" # The Folder of informations
formClass=uic.loadUiType("MusicPlayer2.ui")[0] # UI

'''
 * This is the class of ProgressBar
 * This is moved by QThread
 * Emits Signal every 0.2 seconds that notify the change of time
'''
class MusicProgressBar(QThread):
    player=None
    isRunning=False
    def run(self):
        while True:
            time.sleep(0.2)
            self.emit(SIGNAL("timeChanged(int)"), int(self.player.time))
            if self.player.time==0:
                self.isRunning=False
                time.sleep(1)
                print(self.player.playing)
                if not self.player.playing:
                    self.emit(SIGNAL("FileEnded"))
                    break
    def __init__(self, player):
        super().__init__()
        self.player=player

'''
 * This is the class of Playing Musics
 * This only play music in QThread
'''
class MusicPlay(QThread):
    file=None
    player=None
    progressBar=None
    def setVolume(self, volume):
        self.player.volume=volume*0.01
    def fileEnded(self):
        self.emit(SIGNAL("nextMusic()"))
    def timeChanged(self, time):
        self.emit(SIGNAL("timeChanged(int)"), time)
    def run(self):
        self.player.play()
    def selectFile(self, file):
        self.file=pyglet.media.load(file)
        self.player.next()
        self.player.queue(self.file)
        if self.progressBar:
            self.progressBar.quit()
        self.progressBar=MusicProgressBar(self.player)
        self.connect(self.progressBar, SIGNAL("timeChanged(int)"), self.timeChanged)
        self.connect(self.progressBar, SIGNAL("FileEnded"), self.fileEnded)
        self.progressBar.start()
    def pause(self):
        self.player.pause()
    def resume(self):
        self.player.play()
    def __init__(self):
        super().__init__()
        self.player=pyglet.media.Player()

class Window(QMainWindow, formClass):
    '''
    * Variables
    '''

    currentIndex=0
    currentFile=None
    currentMusicPlayClass=None
    duration=0
    '''
    * Menu Bars
    '''
    def showUpFolder(self):
        print("Open Folder")
        os.startfile(fileRoute)
    def showUpInfoFolder(self):
        print("Open Info Folder")
        os.startfile(infoFolderRoute)
    def downloadFiles(self):
        print("Download Top 100 Files")
        os.system("python MainFile.py")

    def updateTags(self):
        print("Update Tags")
        self.saveFileToLists()

    def updateFiles(self):
        global files
        print("Update Files")
        files=glob.glob(fileRoute+"/*.mp3")
        self.updateTags()
    '''
    * Methods
    '''
    def changeVolume(self, volume):
        self.currentMusicPlayClass.setVolume(volume)

    def searchMusic(self, query):
        global filesByTop
        global filesByABC
        global filesByYear
        global filesBySinger
        global filesByYearDict

        currentList=None
        List=None
        if self.Tap_List.currentIndex()==0:
            currentList=self.ChartList
            List=filesByTop
        elif self.Tap_List.currentIndex()==1:
            currentList=self.ABCList
            List=filesByABC
        elif self.Tap_List.currentIndex()==2:
            currentList=self.SingerList
            List=filesBySinger
        elif self.Tap_List.currentIndex()==3:
            currentList=self.YearList
            List=filesByYearDict[self.Combo_Year.currentText()].find(query)
        List=List.find(query)
        self.currentList.clear()
        for file in self.files:
            if str(file).lower().find(str(query).lower())!=-1:
                self.MusicLists.addItem(os.path.basename(file).replace(".mp3", ""))

    def changeSong(self, song):
        # variables
        global filesByTop
        global filesByABC
        global filesBySinger
        global filesByYearDict
        global musiclists

        print(self.Tap_List.currentIndex())
        print(song.text())

        if self.Tap_List.currentIndex()==0:
            print("Melon Top 100")
            musiclists=filesByTop.copy()
            self.currentIndex=self.ChartList.currentRow()
        elif self.Tap_List.currentIndex()==1:
            print("ABC")
            musiclists=filesByABC.copy()
            self.currentIndex=self.ABCList.currentRow()
        elif self.Tap_List.currentIndex()==2:
            print("Singer")
            musiclists=filesBySinger.copy()
            self.currentIndex=self.SingerList.currentRow()
        elif self.Tap_List.currentIndex()==3:
            print("Year")
            musiclists=filesByYearDict[self.Combo_Year.currentText()].copy()
            self.currentIndex=self.YearList.currentRow()

        self.playMusic()
    def nextMusic(self):
        global musiclists
        if self.Check_Random.isChecked():
            self.currentIndex=random.randint(0, musiclists.__len__()-1)
        else:
            self.currentIndex+=1
            if self.currentIndex==musiclists.__len__():
                self.currentIndex=0
        self.playMusic()

    def prevMusic(self):
        global musiclists
        if self.Check_Random.isChecked():
            self.currentIndex=random.randint(0, musiclists.__len__()-1)
        else:
            self.currentIndex-=1
            if self.currentIndex==-1:
                self.currentIndex=musiclists.__len__()-1
        self.playMusic()

    def pauseMusic(self):
        if self.currentMusicPlayClass.player.playing:
            self.Button_Play.setText("▶")
            self.currentMusicPlayClass.pause()
        else:
            self.Button_Play.setText("||")
            self.resumeMusic()

    def setUpAlbumText(self, file):
        audio=EasyID3(file)
        self.Text_Album.setText(audio['album'][0])
        self.Text_Artist.setText(audio['artist'][0])
        self.Text_Genre.setText(audio['genre'][0])
        self.Text_Date.setText(audio['date'][0])
        self.Text_Title.setText(audio['title'][0])

        audio=MP3(file, ID3=ID3)
        img=open('AlbumArt.jpg', 'wb')
        for key in audio.keys():
            if str(key).count("APIC")!=0:
                img.write(audio[key].data)
                break
        img.close()

        pixmap=QPixmap("AlbumArt.jpg")
        self.AlbumArt.setPixmap(pixmap)
        self.AlbumArt.setScaledContents(True)
        os.remove("AlbumArt.jpg")

        self.Lyrics.clear()
        if('USLT:None:\x00\x00\x00' in audio.keys()):
            lyrics=str(audio['USLT:None:\x00\x00\x00']).split("\n")
            for lyric in lyrics:
                self.Lyrics.addItem(lyric)

    def playMusic(self):
        global musiclists
        global files
        global fileInfoList

        self.setUpAlbumText(files[musiclists[self.currentIndex][0]])

        self.currentFile=files[musiclists[self.currentIndex][0]]

        self.currentMusicPlayClass.selectFile(self.currentFile)
        self.currentMusicPlayClass.start()
        self.Button_Play.setText("||")

        mp3file=MP3(self.currentFile)
        self.duration=int(mp3file.info.length)
        self.Text_Time.setText(str(int(mp3file.info.length/60))+":"+str(int(mp3file.info.length%60)))

    def resumeMusic(self):
        if self.currentFile and self.currentMusicPlayClass:
            self.currentMusicPlayClass.resume()

    def setTime(self, time):
        self.Text_Time_0.setText(str(int(time/60))+":"+str(int(time%60)))
        self.Slider.setValue(int(time/self.duration*100))

    def changeYear(self):
        global filesByYearDict
        print(self.Combo_Year.currentText())
        self.YearList.clear()
        for file in filesByYearDict[self.Combo_Year.currentText()]:
            self.YearList.addItem(file[1]+"-"+file[2])
    '''
    * init
    '''
    def loadTop100(self):
        global filesByTop
        global files
        print("Load Chart Top 100 in .csv")
        file=open("D:/Grade_2/PyCharmProjects/Test/Music/Music/Info/MelonTop100.csv", encoding="UTF-8")
        reader=csv.reader(file)
        for row in reader:
            if row == []:
                continue
            for i in range(files.__len__()-1):
                if os.path.basename(files[i])==row[0]+".mp3":
                    filesByTop.append([i, row[0]])
                    break
        file.close()

    def saveFilesToList(self): # Get All Files in Folder
        # variables
        global files
        global fileInfoList

        files=glob.glob(fileRoute+"/*.mp3")
        for i in range(files.__len__()):
            audio=EasyID3(files[i])
            print(files[i])
            temp=list([i, audio['title'][0], audio['artist'][0], audio['date'][0]])
            fileInfoList.append(temp)
        self.saveToList()

    def saveToList(self):
        global fileInfoList
        global filesByABC
        global filesByYear
        global filesBySinger

        filesByABC=fileInfoList.copy()
        filesByYear=fileInfoList.copy()
        filesBySinger=fileInfoList.copy()

        filesByABC.sort(key=operator.itemgetter(0))
        filesBySinger.sort(key=operator.itemgetter(1))
        filesByYear.sort(key=operator.itemgetter(2))

        self.bindByYears()

    def bindByYears(self):
        global filesByYear
        global filesByYearDict

        for i in range(filesByYear.__len__()):
            if not filesByYear[i][3] in filesByYearDict:
                filesByYearDict[filesByYear[i][3]]=list()
            filesByYearDict[filesByYear[i][3]].append(filesByYear[i])

        self.initUI()

    def initUI(self):
        # variables
        global filesByABC
        global filesByYear
        global filesBySinger
        global filesByYearDict
        global filesByTop

        print("Init UI")
        self.loadTop100()

        for key in sorted(filesByYearDict, reverse=True):
            self.Combo_Year.addItem(key)
        self.Combo_Year.setCurrentIndex(-1)

        for file in filesByTop:
            self.ChartList.addItem(file[1])

        for file in filesByABC:
            self.ABCList.addItem(file[1]+"-"+file[2])

        for file in filesBySinger:
            self.SingerList.addItem(file[2]+"-"+file[1])

        self.OpenFolder.triggered.connect(self.showUpFolder) # Open Music Folder
        self.Download.triggered.connect(self.downloadFiles) # Download Top 100 Files
        self.OpenInfoFolder.triggered.connect(self.showUpInfoFolder) # Show Up Info Folder
        self.TagUpdate.triggered.connect(self.updateTags) # Update Tags
        self.FileUpdate.triggered.connect(self.updateFiles) # Update Files

        self.connect(self.ChartList, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),
                     self.changeSong)
        self.connect(self.ABCList, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),
                     self.changeSong)
        self.connect(self.SingerList, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),
                     self.changeSong)
        self.connect(self.YearList, SIGNAL("itemDoubleClicked(QListWidgetItem *)"),
                     self.changeSong)
        self.connect(self.Combo_Year, SIGNAL("currentIndexChanged(int)"),
                     self.changeYear)

        self.connect(self.Button_Back, SIGNAL("clicked()"), self.prevMusic)
        self.connect(self.Button_Next, SIGNAL("clicked()"), self.nextMusic)
        self.connect(self.Button_Play, SIGNAL("clicked()"), self.pauseMusic)

        self.show()

        self.currentMusicPlayClass=MusicPlay()
        self.connect(self.Volume, SIGNAL("valueChanged(int)"), self.changeVolume)
        self.connect(self.currentMusicPlayClass, SIGNAL("timeChanged(int)"), self.setTime)
        self.connect(self.currentMusicPlayClass, SIGNAL("nextMusic()"), self.nextMusic)
        self.connect(self.lineEdit, SIGNAL("textChanged(QString)"), self.searchMusic)
    def __init__(self):
        super().__init__()
        self.setupUi(self) # Set UI

        self.saveFilesToList()
        self.show()


if __name__=="__main__":
    app=QApplication(sys.argv)
    window=Window()
    app.exec_()