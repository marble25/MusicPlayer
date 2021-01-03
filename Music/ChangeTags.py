import glob, urllib.request, urllib.parse, bs4

if __name__=="__main__":
    folder="C:/Users/user/OneDrive/음악"
    files=glob.glob(folder+"/*.mp3")
    for file in files:
        while True:
            startindex=file.find("[")
            if startindex==-1:
                break
            endindex=file.find("]")
            if endindex==-1:
                endindex=len(file)-4
            file=file.replace(file[startindex: endindex+1], "")
        file=file.replace("&amp;", "")
        file=file.replace("-", " ")
        file=file.replace("_", " ")
        file=file.replace("MV", "")
        if file[26]=="0":
            endindex=27
            while True:
                if file[endindex]=="." or\
                    file[endindex]==" " or\
                    file[endindex]=="-":
                    break
                endindex+=1
            file=file.replace(file[26:endindex+1], "")
        fileBuffer=""
        while True:
            startindex=file.find("(")
            if startindex==-1:
                break
            endindex=file.find(")")
            if endindex==-1:
                endindex=len(file)-4
            file=file.replace(file[startindex:endindex+1], "")
        print(file)
        url=urllib.request.urlopen("https://www.melon.com/search/total/index.htm?q="
                                   +urllib.parse.quote(file[26:-4])+"&section=&ipath=srch_form")
        soup=bs4.BeautifulSoup(url, "html.parser")
        print(soup.findAll(attrs={"class":"fc_gray"})[0]['title'])
