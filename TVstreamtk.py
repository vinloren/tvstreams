#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import Tk,ttk,Frame,Listbox,Button,Label,Text,Scrollbar,BOTH,W,N,E,S,END
from os import system
from os import path
from urllib import request
import xml.etree.cElementTree as ET
import http, re, urllib, random, base64, time

player = "omxplayer -o hdmi "
#player = "mplayer "
baseurl = 'http://www.rai.tv/dl/RaiTV/videoWall/PublishingBlock-5566288c-3d21-48dc-b3e2-af7fbe3b2af8.xml'
agent	= "Mozilla/5.0 (X11; U; Linux i686; it; rv:1.9.0.6) Gecko/2009011912 Firefox/3.5.1"
scrambler = "hMrxuE2T8V0WRW0VmHaKMoFwy1XRc+hK7eBX2tTLVTw="
re_url	= "^http://(?P<host>[a-zA-Z0-9]*\.([a-zA-Z0-9]*\.)+[a-zA-Z0-9]*)(?P<path>/[\w\-\+\~\%\#\.\/]*)\?cont\=(?P<chanid>[\d\w]*)"
re_date = "^(?P<day>\d*)-(?P<month>\d*)-(?P<year>\d*)\s(?P<hour>\d*):(?P<minutes>\d*):(?P<seconds>\d*)"
url=None
name=None
mode=None
app = None
linkmode = 2
emittenti = []
lingue = []
lingua = ""
getDate = "";
tree = ET.ElementTree(file='channels.xml')
root = tree.getroot()

def addDir(name,url,mode):
        u="url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
        #print (str(1+len(emittenti))+"\tMediatype=Video: "+name)
        emittenti.append(u)
        ok=True
        return ok

def CATEGORY():
        req = request.Request("http://www.la7.tv/xml/epg/index.xml")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = request.urlopen(req)
        link=response.read().decode()
        response.close()
        link=link.replace('\t','').replace('\r\n','').replace('\n','').replace('" />','"/>')
        match=re.compile('<show channel="(.+?)" title="(.+?)" linkUrl="(.+?)<logo src="(.+?)"/>').findall(link)
        for buffer1, name,buffer2,thumb in match:
                #outfile = os.path.join(__settings__.getAddonInfo('path'),'resources','images',thumb.split('/')[-1])
                #if not os.path.isfile(outfile):
                #        urlretrieve(thumb, outfile)
                addDir(name.upper(),name,1)

def findDirettaLink2(name):
        name=name.replace(' ','')
        if name=='Rai4':
                name='RaiQuattro'
        if name=='RaiSport+':
                name='RaiSport'
        
        linkpage= 'http://acab.servebeer.com/tv-player/mitm/tvplayer_web.php?gruppo=RAI&canale='+name       
        print (linkpage)
        page=ReadWebPage(linkpage)
        link=InBetween(page,"writePlayer\('","'")
        return link

def xorBuffer(buffer, arg):
    output=''
    for ch in buffer:
        output += chr(ord(ch) ^ arg)
        return output

def scrambleString(inputString):
        N = random.randint(0,30)
        buff=xorBuffer(inputString,N)
        buff += ';'+str(N)
        #output=cypher(buff, scrambler)
        output = encode2(buff,scrambler)
        return output
        
def encode2(token, key):
    i = len(token)-1
    j = 0
    encoded = ""
    while i >= 0:
        enc = chr(ord(token[i]) ^ ord(key[j]))
        encoded = enc + encoded
        i -= 1
        j += 1
    return encoded
    
def encode3(token):
    return base64.encodestring(str.encode(token)).decode()


def addItem(name,url,mode,iconimage,mediatype,dur,folder=True):
        u="url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
        ok=True
        #print ("Url= "+u)
        emittenti.append(u)
        return ok

def InBetween(source,s1,s2):
        res=re.compile(s1+'(.+?)'+s2).findall(source)
        if res:
                return res[0]
        else:
                return ''

def ReadWebPage(url):
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; it; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6')
        req.add_header('Cache-Control', 'no-cache')
        response = request.urlopen(req)
        text=response.read().decode()
        text=text.replace('\x0a',' ')
        text=text.replace('\x0d','')
        response.close()
        #print ("text= "+text)
        return text

def PLAY(url,name):
        if linkmode==1:
                mmsurl=findDirettaLink2(name)
        else:
                mmsurl=mms(url,agent)
        try:
            print ("Playing "+mmsurl)
            system("%s %s" % (player, mmsurl))
        except:
            pass
        
       

def SHOWS():
        data = ReadWebPage(baseurl)
        sets=re.compile('<set.+?</set>').findall(data)
        for set in sets:
                name=InBetween(set,'name="','"')
                img='http://www.rai.tv' + InBetween(set,'<image>','</image>')
                vidUnits=re.compile('<videoUnit.+?</videoUnit>').findall(set)
                for vidUnit in vidUnits: #and name!='Rai Uno' and name!='Rai Due' and name !='Rai Tre' and name!='Diretta Miss Italia'
                        if vidUnit.find('type="RaiTv Diretta Full Video"')>-1 and name!='Diretta Miss Italia':
                                url=InBetween(vidUnit,'<url>','</url>')
                                addItem(name,url,2,img,'Video','',False)

def mms(stream, useragent=agent):
        match_url = re.match(re_url, stream).groupdict()
        host = match_url["host"] 
        path = match_url["path"]
        chan = match_url["chanid"]
        date_connection = http.client.HTTPConnection("videowall.rai.it")
        date_connection.putrequest("GET", "/cgi-bin/date")
        date_connection.putheader("User-Agent", agent)
        date_connection.putheader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        date_connection.putheader("Accept-Language", "it-it,it;q=0.8,en-us;q=0.5,en;q=0.3")
        #date_connection.putheader("Accept-Encoding", "gzip,deflate")
        #date_connection.putheader("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7")
        date_connection.putheader("Connection", "keep-alive")
        date_connection.putheader("Keep-Alive", "115")
        date_connection.endheaders()
        date_response = date_connection.getresponse().read()
        date_connection.close();
        date = date_response.strip()
        print ("Data: "+date.decode())
        global getDate
        getDate = date.decode()
        #date = bytes.decode(date_response[:len(date_response)-1])

        match_date = re.match(re_date, date.decode()).groupdict()
        day		= match_date["day"]
        month	= match_date["month"]
        year	= match_date["year"]
        hour	= match_date["hour"]
        minutes	= match_date["minutes"]
        seconds	= match_date["seconds"]
        rnd1 = str(random.randint(0, 1234))
        rnd2 = str(random.randint(0, 1234))
        tchan = chan
        token = year+";"+tchan+";"+day+"-"+month+"-"+rnd1+"-"+hour+"-"+minutes+"-"+seconds+"-"+rnd2
        print ('Token: '+token)
        ttAuth = encode3(scrambleString(token))
        print ('ttAuth: '+ttAuth)

        asx_connection = http.client.HTTPConnection(host)
        asx_connection.putrequest("POST", path+"?cont="+chan)
        asx_connection.putheader("User-Agent", agent)
        asx_connection.putheader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        asx_connection.putheader("Accept-Language", "it-it,it;q=0.8,en-us;q=0.5,en;q=0.3")
        asx_connection.putheader("Accept-Encoding", "gzip,deflate")
        asx_connection.putheader("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7")
        asx_connection.putheader("Connection", "keep-alive")
        asx_connection.putheader("Keep-Alive", "115")
        asx_connection.putheader("viaurl", "www.rai.tv")
        asx_connection.putheader("ttAuth", ttAuth)
        asx_connection.putheader("Content-Length","0")
        asx_connection.putheader("Content-Type","application/x-www-form-urlencoded")
        asx_connection.endheaders()
        asx_response = asx_connection.getresponse().read()
        asx_connection.close()
        asx = re.compile("\n").sub(" ", asx_response.decode())
        return re.match("^(.*)(?P<mms>mms://.*)\"", asx).groupdict()["mms"].strip()


#LA7 TV Videos
def SetVideoQuality(sURL, sQlty):
        if sQlty == "0":
                if sURL.find('_400.mp4') >= 0:
                        return sURL.replace('_400.mp4','_800.mp4')
                else:
                        return sURL
        if sQlty == "1":
                if sURL.find('_800.mp4') >= 0:
                        return sURL.replace('_800.mp4','_400.mp4')
                else:
                        return sURL


#LA7 TV Videos
def NormaliseName(sInput, sDate):
        sInput = sInput.replace('\\','').replace('-',' - ').replace('  ',' ').replace(' 20 ',' 20:00 ').upper()
        if sDate == "true":
                if sInput.find('-') >= 0:
                        aInput=sInput.split('-')
                        sInput=aInput[0]
        return sInput.strip()

#LA7 TV Videos
def CalculateDate(curDate, DatePos, sDate):
        if sDate == "true":
                StartDate=datetime.datetime(*(time.strptime(curDate, '%m/%d/%Y')[0:6]))
                vidDate=StartDate+datetime.timedelta(days=int(DatePos))
                return " ("+vidDate.strftime("%d %b %Y")+")"
        else:
                return ""

#LA7 TV Videos
def VIDEOLINKS(url):
        #getDate = xbmcplugin.getSetting(int( sys.argv[ 1 ] ),"display_date")
        #getQuality = "xbmcplugin.getSetting(int( sys.argv[ 1 ] ),"vid_quality")
        getQuality = '1'
        req = request.Request("http://www.la7.tv/xml/epg/index.xml")
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = request.urlopen(req)
        link=response.read().decode()
        response.close()
        link=link.replace('\t','').replace('\r\n','').replace('\n','').replace('" />','"/>')
        catblock=re.compile(' title="'+url+'" linkUrl="(.+?)</show>').findall(link)
        epgDate=re.compile('<epg startDate="(.+?)">').findall(link)
        match=re.compile('<item pos="(.+?)" linkUrl="(.+?)<img src="(.+?)"/> <video url="mp4:(.+?)"/>(.+?)<!\[CDATA\[(.+?)\]\]>').findall(str(catblock))
        for datepos,buffer1,thumb,url,buffer2,name in match:
                name = NormaliseName(name,getDate) + CalculateDate(epgDate[0],datepos,getDate)
                url = SetVideoQuality(url,getQuality)
                print (name,"rtmp://yalpvod.alice.cdn.interbusiness.it:1935/vod"+url) #+","+thumb)
                system("%s %s" % (player, "rtmp://yalpvod.alice.cdn.interbusiness.it:1935/vod"+url))
                break


fifo = "/var/log/mystdin"
if path.exists(fifo):
	system("rm "+fifo)
system("mkfifo "+fifo)

for elem in tree.iterfind('stream'):
    for attr in elem.iterfind('language'):
        if(attr.text not in lingue):
            lingue.append(attr.text)
            #print (len(lingue), attr.text)

lingue.sort()


class TVstream(Frame):
    area     = None
    emitlst = None
    langlst = None
    URL     = None
    
    def __init__(self,parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("TVstream manager")
        self.stytle = ttk.Style()
        self.pack(fill=BOTH, expand=1)        
        self.columnconfigure(0, weight=1, pad=2)
        self.columnconfigure(2, weight=1, pad=2)
        self.columnconfigure(4,  pad=7)
        #self.rowconfigure(3, weight=1)
        #self.rowconfigure(4, weight=1, pad=7)

        lbll = Label(self, text="Lingua")
        lbll.grid(row=0,column=0,sticky=W, pady=4, padx=5)

        lble = Label(self, text="Emittenti")
        lble.grid(row=0,column=2,sticky=W, pady=1, padx=5)

        global langlst
        scrollang = Scrollbar(self)
        langlst = Listbox(self,font='Arial 9',yscrollcommand=scrollang.set)
        scrollang.config(command = langlst.yview)
        
        for i in lingue:
            langlst.insert(END, i)
        langlst.focus_set()
        
        langlst.bind("<<ListboxSelect>>", self.onSelectLang)  
        langlst.grid(row=1,column=0, columnspan=2, padx=6,sticky=E+W+S+N)
        scrollang.grid(row=1,column=1, sticky=E+S+N)

        global emitlst
        scrollemit = Scrollbar(self)
        emitlst = Listbox(self,font='Arial 9',yscrollcommand=scrollemit.set)
        scrollemit.config(command = emitlst.yview )
        emitlst.bind("<<ListboxSelect>>", self.onSelectEmittente)
        emitlst.grid(row=1,column=2, columnspan=2, padx=5,sticky=E+W+S+N)
        scrollemit.grid(row=1,column=3,sticky=E+S+N)

        lbltxt = Label(self, text="Output log")
        lbltxt.grid(row=2,column=0, columnspan=3, sticky=W, pady=4, padx=5)
        
        global area
        area = Text(self,height=10,font='Arial 9')
        area.grid(row=3, column=0, columnspan=5, rowspan=1, padx=5, sticky=E+W+S+N)
        scrolltxt = Scrollbar(self)
        scrolltxt.config(command = area.yview)
        scrolltxt.grid(row=3,column=4, columnspan=1, rowspan=1, sticky=E+N+S)
        
        play = Button(self, text='Play', command=self.playUrl,
               bg='gray', fg='black')
        play.grid(row=1,column=4,padx=4,sticky=E+W)


    def onSelectEmittente(self, val):
        sender = val.widget
        idx = sender.curselection()
        global emittenti
        ind = list(idx)
        global URL
        try:
            URL = emittenti[int(ind[0])]
            target = URL.split('&')
            global area
            area.insert(END,'Ready to play '+target[0]+'\n')
            emittenti = []
        except:
            pass
        

    def onSelectLang(self, val):
        sender = val.widget
        idx = sender.curselection()
        global lingua, area,  emitlst
        lingua = sender.get(idx)
        area.insert(END,'Scelto lingua '+lingua+'\n')
        lang = lingua
        emitlst.delete(0,END)
        for elem in tree.iterfind('stream'):
            for attr in elem.iter():
                if(attr.tag == "language" and attr.text == lang):
                    #print(attr.tag, attr.text)
                    for lnk in elem.iterfind('link'):
                        #print(lnk.text)
                        for path in elem.iterfind('playpath'):
                            #print(path.text)
                            for title in elem.iterfind('title'):
                                u = "url="+lnk.text+"&mode="+str(3)+"&name="+urllib.parse.quote_plus(title.text)
                                #print (str(1+len(emittenti))+"\t"+title.text)
                                emittenti.append(u)
                                emitlst.insert(END,title.text) 
        if(lang == "Italian"):
            SHOWS()
            CATEGORY()
            emitlst.delete(0, END)
            for el in emittenti:
                params = el.split('&')
                namel = params[2].split('=')
                name=urllib.parse.unquote_plus(namel[1])
                emitlst.insert(END,name) 


    def playUrl(self):
        global URL,area
        params = URL.split('&')
        #print(params)
        try:
            urll = params[0].split('=')
            url=urllib.parse.unquote_plus(urll[1])
            #print(urll[0]+'='+url)
        except:
            pass
        try:
            namel = params[2].split('=')
            name=urllib.parse.unquote_plus(namel[1])
            #print(namel[0]+'='+name)
        except:
            pass
        try:
            model =  params[1].split('=')
            mode=int(model[1])
            #print(params[1])
        except:
            pass

        if mode==2:
            PLAY(str(url),name)
        elif mode==1:
            #area.insert(END,"Playing "+url+'\n')
            VIDEOLINKS(url)
        elif mode==3:
            for elem in tree.iterfind('stream'):
                for attr in elem.iter():
                    if(attr.tag == "title" and attr.text == name):
                        for link in elem.iterfind('link'):
                                url = link.text + " -W "
                                for lnk in elem.iterfind('swfUrl'):
                                    url += lnk.text + " -p "
                                    for pgurl in elem.iterfind('pageUrl'):
                                        url += pgurl.text
                                        for path in elem.iterfind('playpath'):
                                            #url += " -p "+path.text+" "
                                            for adv in elem.iterfind('advanced'):
                                                try:
                                                    url += " -y "+path.text+" "+adv.text + " -o /var/log/mystdin & "+player +' /var/log/mystdin </dev/stdin'
                                                except:
                                                    url += " -y "+path.text+" -o /var/log/mystdin & "+player +' /var/log/mystdin </dev/stdin'
                    				
            area.insert(END,"Playing "+url+'\n')
            system("%s %s" % ("rtmpdump --live -v -r ", url))
        
    
def main():
    root = Tk()
    root.geometry("480x360+20+20")
    global app 
    app = TVstream(root)
    root.mainloop()

if __name__ == '__main__':
    main() 

    
