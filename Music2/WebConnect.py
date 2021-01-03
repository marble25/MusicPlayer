__author__ = 'user'
import requests, json, bs4, urllib.request, re
from apiclient.discovery import build

class WebConnectByMelonAPI:
    APIurl="http://apis.skplanetx.com/melon/charts/todaytopsongs?version=1&page=1&count=100"
    headers={'appKey' : ""}

    def __init__(self):
        self.r=requests.get(self.APIurl, headers=self.headers)
        self.jsonFile=self.r.text

        print("WEB CONNECT(MELON API) COMPLETE")

    def setListFromAPI(self): # Melon API에서 가져오기
        data=json.loads(self.jsonFile)
        orData=data['melon']['songs']['song']

        songs=list()

        for song in orData:
            songDict=dict()
            songDict['songId']=song['songId']
            songDict['songName']=song['songName']

            artistList=list()
            for artist in song['artists']['artist']:
                artistList.append(artist['artistName'])

            songDict['artists']=artistList

            songDict['albumName']=song['albumName']
            songDict['currentRank']=song['currentRank']
            songs.append(songDict)

        print("MELON API PARSING COMPLETE")

        return songs

class WebConnectByMelonPage:
    melonurl="https://www.melon.com/song/detail.htm?songId="

    def setSongFromPage(self, songId): # 추가 다운로드시 사용
        song=dict()
        song['songId']=songId

        tempInfo=self.bs4Parsing(song)

        song['releaseDate']=tempInfo[0]
        song['genre']=tempInfo[1]
        song['albumImg']=tempInfo[2]
        song['lyrics']=tempInfo[3]
        song['songName']=tempInfo[4]
        song['artists']=tempInfo[5]
        song['albumName']=tempInfo[6]

        print("MELON PAGE PARSING COMPLETE")
        return song

    def setListFromPage(self, songs): # Melon Page에서 가져오기
        for song in songs:
            tempInfo=self.bs4Parsing(song)

            song['releaseDate']=tempInfo[0]
            song['genre']=tempInfo[1]
            song['albumImg']=tempInfo[2]
            song['lyrics']=tempInfo[3]

        print("MELON PAGE PARSING COMPLETE")
        return songs

    def bs4Parsing(self, song):
        request=urllib.request.urlopen(self.melonurl+str(song['songId']))
        soup=bs4.BeautifulSoup(request, "html.parser")

        title=soup.find("p", {"class":"songname"}).text.replace("곡명", "").strip()

        songInfos=soup.find("dl", {"class":"song_info clfix"})

        span_artists=songInfos.findAll("dd")[0].findAll("span")
        artists=list()
        for artist in span_artists:
            if len(artist.text)!=0:
                artists.append(artist.text)

        album=songInfos.findAll("dd")[1].text

        releaseDate=songInfos.findAll("dd")[2].text[:4]

        genre=songInfos.findAll("dd")[3].text

        albumImg=soup.findAll(attrs={"id":"songImgArea"})[0].img['src']

        lyricsOrinText=str(soup.find("div", attrs={"id":"d_video_summary"})).replace("<br>", "\n")
        p=re.compile("(<.*>)*")
        lyrics=p.sub("", lyricsOrinText).strip()

        print("SOUP PARSING COMPLETE")
        return (releaseDate, genre, albumImg, lyrics, title, artists, album)

class WebConnectByYoutubeAPI:
    API_KEY = ""
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def searchVideo(self, songs):
        for song in songs:
            # 쿼리에서 괄호 제거
            p=re.compile("\(([^{}]+)\)")
            songName=p.sub("", song['songName']).strip()
            query="audio "+songName.replace("`", "'")+" "+" ".join(song['artists'])
            print(query)

            youtube = build(
              self.YOUTUBE_API_SERVICE_NAME,
              self.YOUTUBE_API_VERSION,
              developerKey=self.API_KEY
            )
            search_response=youtube.search().list(
              q=query,
              part="id,snippet",
              type="음악",
              maxResults=25
            ).execute()
            song=self.parseJson(search_response['items'], song)

            if not 'videoId' in song:
                query=songName+" "+" ".join(song['artists'])
                search_response=youtube.search().list(
                  q=query,
                  part="id,snippet",
                  type="음악",
                  maxResults=25
                ).execute()
                song=self.parseJson(search_response['items'], song)
            print(song)
        return songs

    def parseJson(self, search_response, song):

        for video in search_response:
            # 비디오가 아닐 경우 필터링
            if video['id']['kind']!="youtube#video":
                continue

            # 비디오 타이틀을 소문자화
            video_title=video['snippet']['title'].lower().replace(" ", "")
            video_id=video['id']['videoId']
            p=re.compile("\(([^{}]+)\)")
            songName=p.sub("", song['songName'].lower()).strip().replace(" ", "")

            # audio와 lyrics, artist가 query에 포함된 것 찾기
            if video_title.find(songName.replace("`", "'"))!=-1:

                if video_title.find("mv")!=-1 or video_title.find("m/v")!=-1:
                    continue
                if video_title.find("karaoke")!=-1 or video_title.find("mr")!=-1:
                    continue
                if video_title.find("live")!=-1 or video_title.find("라이브")!=-1:
                    continue
                if video_title.find("cover")!=-1:
                    continue
                if video_title.find("teaser")!=-1:
                    continue


                flag=True
                for artist in song['artists']:
                    artistName=p.sub("", artist.lower()).strip().replace(" ", "")
                    if video_title.find(artistName)==-1:
                        flag=False
                        break

                if flag:
                    song['videoId']=video_id
                    return song

        #차선책
        if not 'videoId' in song:
            for video in search_response:
                # 비디오가 아닐 경우 필터링
                if video['id']['kind']!="youtube#video":
                    continue

                # 비디오 타이틀을 소문자화
                video_title=video['snippet']['title'].lower().replace(" ", "")
                video_id=video['id']['videoId']
                p=re.compile("\(([^{}]+)\)")
                songName=p.sub("", song['songName'].lower()).strip().replace(" ", "")

                print(video_title)
                print(songName)
                # audio와 lyrics, artist가 query에 포함된 것 찾기
                if video_title.find(songName.replace("`", "'"))!=-1:
                    song['videoId']=video_id
                    return song

        # 차차선책
        if not 'videoId' in song:
            for video in search_response:
                # 비디오가 아닐 경우 필터링
                if video['id']['kind']!="youtube#video":
                    continue

                video_id=video['id']['videoId']

                print(video_title)
                print(songName)

                song['videoId']=video_id
                return song

        return song
