__author__ = 'user'
import sqlite3
import datetime

class DataBase:
    def __init__(self):
        self.con=sqlite3.connect("MusicList.db")
        self.cursor=self.con.cursor()
        self.preSearch()
        #self.cursor.execute("CREATE TABLE musicList (songName text ,albumName text ,artist text,releaseDate date ,genre text)")
        #self.cursor.execute("CREATE TABLE topList (songName text ,albumName text ,artist text)")
        #self.cursor.execute("CREATE TABLE executeLogs (date text)")

    def insert(self, songName, albumName, artist, releaseDate, genre, fileName):
        queryData=(songName, albumName, artist, releaseDate, genre, fileName)
        self.cursor.execute("INSERT INTO musicList VALUES (?, ?, ?, ?, ?, ?)", queryData)
        self.con.commit()
        print("INSERT COMPLETE")

    def insertTodayTop(self, songs):
        for song in songs:
            queryData=(song['songName'], song['albumName'], ', '.join(song['artists']))
            self.cursor.execute("INSERT INTO topList VALUES (?, ?, ?)", queryData)
            self.con.commit()
        print("INSERT TODAYTOP COMPLETE")

    def getTop100List(self):
        self.cursor.execute("SELECT * FROM topList")
        print("SHOW TOPLIST COMPLETE")
        return self.cursor.fetchall()

    def renewTop100List(self):
        self.cursor.execute("DELETE FROM topList")
        self.con.commit()
        print("DELETE TODAYTOP COMPLETE")

    def preSearch(self):
        self.cursor.execute("SELECT * FROM musicList")
        self.result=self.cursor.fetchall()

    def search(self, songs, mode):
        returnData=list()
        for song in songs:
            flag=False
            for song_2 in self.result:
                if song['songName']==song_2[0] and song['albumName']==song_2[1]:
                    if mode==1:
                        returnData.append(song_2)
                    flag=True
                    break

            if not flag:
                print("SOMETHING NOT FOUND")
                if mode==1:
                    return None
                else:
                    returnData.append(song)

        print("SEARCH COMPLETE")
        return returnData

    def delete(self, songName, albumName, artist):
        queryData=(songName, albumName, artist)
        self.cursor.execute("DELETE FROM musicList WHERE songName=? AND albumName=? AND artist=?",
                            queryData)
        print("DELETE COMPLETE")

    def showAll(self):
        self.cursor.execute("SELECT * FROM musicList")
        for fetch in self.cursor.fetchall():
            print(fetch)
        print("SHOW ALL COMPLETE")

    def deleteAll(self):
        self.cursor.execute("DELETE FROM musicList")
        self.con.commit()
        print("DELETE ALL DATA COMPLETE")

    def closeDB(self):
        self.con.close()