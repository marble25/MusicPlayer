__author__ = 'user'
import pyglet
import random
from PyQt4.QtCore import QThread

class MusicPlay(QThread):

    songs=None
    isRandom=False
    isRepeat=False
    volume=50
    currentIndex=0
    fileRoute="C:/Users/user/OneDrive/음악"
    player=pyglet.media.Player()

    def __init__(self, controller, view):
        super().__init__()
        self.controller=controller
        self.view=view

    def setSongs(self, songs):
        self.songs=songs

    def setSong(self, file):

        self.file=pyglet.media.load(filename=self.fileRoute+"/"+file+".mp3")
        self.player.delete()
        self.player=pyglet.media.Player()
        self.player.on_eos=self.on_eos
        self.player.queue(self.file)
        self.player.play()
        self.player.volume=self.volume/100.0

    def play(self):
        pyglet.app.run()

    def setCurrentIndex(self, currentIndex):
        self.currentIndex=currentIndex

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.play()

    def volumeChange(self, value):
        self.volume=value
        self.player.volume=value/100.0

    def nextMusic(self):

        if not self.isRepeat:

            if self.isRandom:
                self.currentIndex=random.randrange(0, 100)

            else:
                self.currentIndex=(self.currentIndex+1)%100

        self.setSong(self.songs[self.currentIndex][5])
        song=self.controller.getSong(self.currentIndex)
        self.view.changeSongInfo(song)

    def prevMusic(self):

        if self.isRandom:
            self.currentIndex=random.randrange(0, 100)

        else:
            self.currentIndex-=1

        if self.currentIndex<0:
            self.currentIndex=99

        self.setSong(self.songs[self.currentIndex][5])
        song=self.controller.getSong(self.currentIndex)
        self.view.changeSongInfo(song)

    def on_eos(self):
        self.nextMusic()