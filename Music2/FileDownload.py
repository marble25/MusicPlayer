__author__ = 'user'
import threading, subprocess
class FileDownload(threading.Thread):
    youtubeLink="https://www.youtube.com/watch?v="
    path="C:/Users/user/OneDrive/음악/▣"

    def setSong(self, song):
        self.song=song

    def run(self):
        subprocess.call('youtube-dl --no-playlist -o "'+self.path+
                        str(self.song['songId'])+
                        '.%(ext)s" --extract-audio --audio-format mp3 '
                        +self.youtubeLink+str(self.song['videoId']))