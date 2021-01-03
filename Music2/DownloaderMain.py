import glob, os, threading
import DataBase, FileDownload, MusicCoverUpdate, WebConnect
import time

class DownloaderMain:

    def __init__(self, networkConnection=True):

        # Class 변수 설정
        if networkConnection:
            self.webConnectMelonAPI=WebConnect.WebConnectByMelonAPI()
            self.webConnectMelonPage=WebConnect.WebConnectByMelonPage()
            self.webConnectYoutubeAPI=WebConnect.WebConnectByYoutubeAPI()

        self.dataBase=DataBase.DataBase()

    # MELON API에서 가져오기
    def getTop100List(self):
        songs=self.webConnectMelonAPI.setListFromAPI()
        self.dataBase.renewTop100List()
        self.dataBase.insertTodayTop(songs)
        return songs

    # Database에서 가져오기
    def getTop100ListFromDatabase(self):
        songs=self.dataBase.getTop100List()
        return songs

    def setAdditionalInfo(self, songs):

        downloadList=list(songs)

        # 데이터베이스와 비교 작업
        result=self.dataBase.search(songs, mode=2)

        # 추가 정보 넣기
        songs=self.webConnectMelonPage.setListFromPage(downloadList)
        return (songs, downloadList)

    def download(self, songs, downloadList):

        # 비디오 찾기
        songs=self.webConnectYoutubeAPI.searchVideo(downloadList)

        # 파일 다운로드
        for song in songs:
            while threading.activeCount()>5:
                time.sleep(1)

            fileDownloader=FileDownload.FileDownload()
            fileDownloader.setSong(song)
            fileDownloader.start()

        # thread 기다리기
        while threading.activeCount()>1:
            time.sleep(1)

        print("DOWNLOAD COMPLETE")

    def downloadSelectedFile(self, melonLink, youtubeLink):
        songId=str(melonLink).replace("http://www.melon.com/song/detail.htm?songId=", "")
        song=self.webConnectMelonPage.setSongFromPage(songId)
        songs=list()
        songs.append(song)

        if youtubeLink=="":
            songs=self.webConnectYoutubeAPI.searchVideo(songs)
            song=songs[0]
        else:
            videoId=str(youtubeLink).replace("https://www.youtube.com/watch?v=", "")
            song['videoId']=videoId

        fileDownloader=FileDownload.FileDownload(name="FileDownload")
        fileDownloader.setSong(song)
        fileDownloader.start()

        flag=False
        while threading.activeCount()>1:
            time.sleep(1)
            for thread in threading.enumerate():
                if thread.name=="FileDownload":
                    flag=True
                    break

            if not flag:
                break

            flag=False

        songs=list()
        songs.append(song)

        self.updateTags(songs)

    def updateTags(self, songs):

        # TAG 업데이트
        musicCoverUpdater=MusicCoverUpdate.MusicCoverUpdate(songs)
        musicCoverUpdater.changeTags()

        # DB 업데이트
        for song in songs:
            self.dataBase.insert(song['songName'].translate(str.maketrans('?', "#")), song['albumName'].translate(str.maketrans('.?:$}', "#####")), ', '.join(song['artists'])
                            ,song['releaseDate'], song['genre'], song['songName'].translate(str.maketrans('.?:$}', "#####"))+"-"+', '.join(song['artists']))

        print("TAG UPDATE COMPLETE")

if __name__=="__main__":
    downloader=DownloaderMain()
    songs=downloader.getTop100List()
    (songs, downloadList)=downloader.setAdditionalInfo(songs)
    #downloader.download(songs, downloadList)
    downloader.updateTags(songs)