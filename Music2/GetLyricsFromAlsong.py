__author__ = 'user'
import urllib.request
import re
import xml.etree.ElementTree as ET

title="거기서거기"
artist="다이나믹듀오"

url="http://lyrics.alsong.net"
suburl='/alsongwebservice/service1.asmx'
headers = {'Content-Type': 'text/xml; charset=UTF-8'}
query = '<?xml version="1.0" encoding="UTF-8"?><SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:ns2="ALSongWebServer/Service1Soap" xmlns:ns1="ALSongWebServer" xmlns:ns3="ALSongWebServer/Service1Soap12"><SOAP-ENV:Body><ns1:GetResembleLyric2><ns1:stQuery><ns1:strTitle>'\
        +title+'</ns1:strTitle><ns1:strArtistName>'+artist+'</ns1:strArtistName><ns1:nCurPage>0</ns1:nCurPage></ns1:stQuery></ns1:GetResembleLyric2></SOAP-ENV:Body></SOAP-ENV:Envelope>'

dict_time=dict()

query=query.encode('UTF-8')
req=urllib.request.Request(url+suburl, data=query, headers=headers)
with urllib.request.urlopen(req) as response:
    string_original = response.read().decode('utf-8')

    print(string_original)
    root=ET.fromstring(string_original)
    element_groups=root[0][0][0]

    for element in element_groups:
        title_element=element[2].text
        lyrics_element=element[3].text
        artist_element=element[4].text
        album_element=element[5].text

        print(title_element)
        if title_element != title or artist_element != artist:
            continue

        string_new = lyrics_element.replace('[', '^^^^^^\r\n[').replace("<br>", "")
        string_temp = re.findall('\[(.*?)\](.*?)\^\^\^\^\^\^', string_new)

        for i in range(len(string_temp)):
            if string_temp[i][0]=='00:00:00':
                continue

            dict_time[string_temp[i][0]]=string_temp[i][1].strip()

        break

