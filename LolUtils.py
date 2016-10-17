# -*- coding:utf-8 -*-
"""
LolUtils helps you to find information on who you are playing against, and who you are playing with.
This application can search an User's champion Mastery, tier,etc, and can automatically get tier and champion mastery data on each summoner's champion in battle.
LolUtils is designed as a Desktop Application, to be run alongside the League of Legends client.
"""
################################################################################
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Combobox
import request_oop,win32gui,threading,time,sys,_thread,zipfile,os,shelve,championfilecreator,championfilereader,json
from request import NoUserError,NoGameError,TechnicalError,getSummonerTiers
from urllib.request import urlopen,urlretrieve,Request
from urllib.error import HTTPError
from PIL import Image,ImageTk

global root,lolheight,APIKEY

def getAPIKey():
    q = Request('http://dashadower-1.appspot.com/lolutils')
    q.add_header('LolUtils', '43535')
    a = urlopen(q).read().decode("utf-8")
    return a
def setpos():
    hwnd = getPVPWindowLocation()


    root.geometry("400x%d+%d+%d"%(lolheight,hwnd[2],hwnd[1]))
    root.update()
def getPVPWindowLocation():
    hwnd = win32gui.FindWindow(None,"PVP.Net 클라이언트")
    if hwnd: return win32gui.GetWindowRect(hwnd)
    else:return 0
def terminate():
    root.destroy()
    sys.exit(0)







def clearscreen():
    for child in root.winfo_children():
        child.destroy()
def searchagain():
    clearscreen()


    menu = Frame(root)
    menu.pack(side=TOP,fill=X)
    Button(menu,text="Exit",command=terminate).pack(side=RIGHT)
    Button(menu,text="Update Position",command=setpos).pack(side=RIGHT)

    Button(menu,text="Manage Database",command=lambda:championfilereader.ChampionListEditor("Toplevel")).pack(side=RIGHT)
    MainScreen(root)
def searchhandler(region,uname):
    clearscreen()
    username = uname.get()
    regionvar = region.get()

    try:
        sid = request_oop.Summoner(username,request_oop.RiotAPI(regionvar,APIKEY))
    except NoUserError:
        showerror("LolUtils","No such username, %s"%(username))
        searchagain()
    else: UserInfoScreen(root).search(username,regionvar)

def restart(sid):
    for child in root.winfo_children():
        child.destroy()
    usertier = sid.getTier()
    Label(root,text=usertier).pack()
    Button(root,text="Get In game info",command=lambda:getingameinfo(sid)).pack(side=LEFT)



def getddragonversion():
    url = "http://www.dashadower-1.appspot.com/ddragon"
    data = str(urlopen(url).read().decode("utf-8")).rstrip()
    return data

def gameclock(itvar,tvar,wvar):
    while wvar.get():
        time.sleep(1)
        ctime = itvar.get()
        itvar.set(ctime+1)




        mins = divmod(itvar.get(),60)[0]
        sec = str(divmod(itvar.get(),60)[1]).rjust(2,"0")

        tvar.set("%d:%s"%(mins,sec))
    print("gameclock exit")
def getingameinfo(sid):
    try:
        gamedata = request_oop.Game(sid,request_oop.RiotAPI(sid.Region,APIKEY))
    except:
        showerror("LolUtils","Summoner is not in a game")
    else:
        clearscreen()


        Label(root,text="Blue Team").grid(row=0,column=0)
        Label(root,text=gamedata.QueueType).grid(row=0,column=1)
        Label(root,text="Red Team").grid(row=0,column=2)
        Label(root,textvariable=ctimevar).grid(row=0,column=3)
def getlivegame_handler(summoner):
    Summoner = summoner
    try:
        Gamedata = request_oop.Game(Summoner,request_oop.RiotAPI(Summoner.Region,APIKEY))
    except NoGameError:
        showerror("LolUtils","Summoner is not in a game")
    except TechnicalError:
        showerror("LolUtils","TechnicalError")
        searchagain()
    else:
        LiveGameInfoScreen(Gamedata,Summoner)
class LiveGameInfoScreen(Frame):
    def __init__(self,gdata,summoner):
        clearscreen()
        self.master = root
        Frame.__init__(self,self.master)
        self.Gamedata = gdata
        self.Summoner = summoner
        self.menu = Frame(self)
        self.menu.pack(side=TOP,fill=X)
        Button(self.menu,text="Exit",command=terminate).pack(side=RIGHT)
        Button(self.menu,text="Update Position",command=setpos).pack(side=RIGHT)
        Button(self.menu,text="Search Again",command=self.research).pack(side=RIGHT)
        self.pack(expand=YES,fill=BOTH)
        self.createwidgets()
    def onMasteryScroll(self,event):
        self.PlayerCanvas.configure(scrollregion=self.PlayerCanvas.bbox("all"),width=200,height=200)

    def createwidgets(self):
        clearscreen()
        self.master = root
        Frame.__init__(self,self.master)

        self.menu = Frame(self)
        self.menu.pack(side=TOP,fill=X)
        Button(self.menu,text="Exit",command=terminate).pack(side=RIGHT)
        Button(self.menu,text="Update Position",command=setpos).pack(side=RIGHT)
        Button(self.menu,text="Search Again",command=self.research).pack(side=RIGHT)
        self.pack(expand=YES,fill=BOTH)


        self.seconds = IntVar()
        self.seconds.set(int(self.Gamedata.Duration))
        self.ctimevar = StringVar()
        self.ctimevar.set("00:00")
        self.workvar = BooleanVar()
        self.workvar.set(True)
        print(self.seconds.get())
        _thread.start_new_thread(gameclock,(self.seconds,self.ctimevar,self.workvar))

        self.InfoFrame = Frame(self,bd=4,relief=SUNKEN)
        self.InfoFrame.pack(fill=X,side=TOP)
        Label(self.InfoFrame,text=self.Summoner.SummonerName).pack()
        if self.Gamedata.QueueType == "RANKED": self.Queuetype = "랭크"
        elif self.Gamedata.QueueType == "NORMAL": self.Queuetype = "일반"
        elif self.Gamedata.QueueType == "BOT": self.Queuetype = "봇전"
        elif self.Gamedata.QueueType == "CUSTOM": self.Queuetype = "사용자 설정"
        if self.Gamedata.mapId == 11:
            Label(self.InfoFrame,text="소환사의 협곡 - %s"%(self.Queuetype)).pack(side=LEFT)
        elif self.Gamedata.mapId == 10:
            Label(self.InfoFrame,text="뒤틀린 숲").pack(side=LEFT)
        elif self.Gamedata.mapId == 8:
            Label(self.InfoFrame,text="수정의 상처").pack(side=LEFT)
        elif self.Gamedata.mapId == 12:
            Label(self.InfoFrame,text="칼바람 나락").pack(side=LEFT)

        Label(self.InfoFrame,textvariable=self.ctimevar).pack(side=RIGHT)



        self.PlayerCanvas = Canvas(self,bd=4,relief=SUNKEN)
        self.PlayerCanvasScrollbar = Scrollbar(self,orient=HORIZONTAL,command=self.PlayerCanvas.xview)
        self.PlayerCanvas.configure(xscrollcommand=self.PlayerCanvasScrollbar.set)

        self.PlayerCanvas.pack(side=TOP,expand=YES,fill=BOTH)
        self.PlayerCanvasScrollbar.pack(side=BOTTOM,anchor=S,fill=X)
        self.PlayerFrame = Frame(self.PlayerCanvas)
        self.PlayerCanvas.create_window((0,0),window=self.PlayerFrame,anchor='nw')
        self.PlayerFrame.bind("<Configure>",self.onMasteryScroll)



        Label(self.PlayerFrame,text="Blue Team",fg="#0000FF",bd=5,relief=RAISED).grid(row=0,column=0)
        Label(self.PlayerFrame,text="").grid(row=0,column=1)
        Label(self.PlayerFrame,text="Red Team",fg="#FF0000",bd=5,relief=RAISED).grid(row=0,column=2)
################################################################################
        self.Blueteam = []
        self.Redteam = []
        db = shelve.open("champions")
        self.Blue_tierdata = getSummonerTiers(self.Gamedata.BluePlayers,self.Summoner.Region,self.Summoner.APIKey)

        for players in self.Blue_tierdata: #([("4234235234","User1"),...],[("41414124","User2"),...])

            Username = players[1] #User1
            #SummonerData = request_oop.Summoner(Username,self.Summoner.API)
            try:
                League,Tier = players[2].split("-") #"BRONZE-V"
            except ValueError: League,Tier = "UNRANKED",""

            for data in self.Gamedata.BlueChampions: #([("4234235234","User1","51"),...],[("41414124","User2","105"),...])
                if data[0] == players[0]: #"425234" == "5235325"
                    ChampionId = data[2]  #"51"
                    break

            for objects in db:

                if str(db[objects]["id"]) == ChampionId:

                    ChampionName = db[str(objects)]["kr"]
                    ChampionKey = str(objects)

            self.Blueteam.append([players[0],players[1],League,Tier,ChampionName,ChampionKey])

        #champion
        self.Red_tierdata = getSummonerTiers(self.Gamedata.RedPlayers,self.Summoner.Region,self.Summoner.APIKey)
        for players in self.Red_tierdata: #([("4234235234","User1"),...],[("41414124","User2"),...])

            Username = players[1] #User1
            #SummonerData = request_oop.Summoner(Username,self.Summoner.API)
            try:
                League,Tier = players[2].split("-") #"BRONZE-V"
            except ValueError: League,Tier = "UNRANKED",""

            for data in self.Gamedata.RedChampions: #([("4234235234","User1","51"),...],[("41414124","User2","105"),...])
                if data[0] == players[0]: #"425234" == "5235325"
                    ChampionId = data[2]  #"51"
                    break

            for objects in db:

                if str(db[objects]["id"]) == ChampionId:

                    ChampionName = db[str(objects)]["kr"]
                    ChampionKey = str(objects)
            self.Redteam.append([players[0],players[1],League,Tier,ChampionName,ChampionKey])

        self.Blue_offset = 1
        self.ddragoncdn = "http://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s.png"
        self.ddragonversion = getddragonversion()
        for players in self.Blueteam:
            myFrame = Frame(self.PlayerFrame,bd=4,relief=SUNKEN)
            myFrame.grid(row=self.Blue_offset,column=0)

            Label(myFrame,text=players[1]).grid(row=0,column=0)
            Label(myFrame,text="%s %s"%(players[2],players[3])).grid(row=1,column=0)
            Label(myFrame,text="Mastery").grid(row=2,column=0)
            if not os.path.isfile(os.getcwd()+"\\images\\%s.png"%(str(players[5]))):
                urlretrieve(self.ddragoncdn%(str(self.ddragonversion).strip(),str(players[5])),os.getcwd()+"\\images\\%s.png"%(str(players[5])))
            champphoto = Image.open(os.getcwd()+"\\images\\%s.png"%(str(players[5])))
            imageobject = ImageTk.PhotoImage(champphoto)
            photolabel = Label(myFrame,image=imageobject)
            photolabel.image = imageobject
            photolabel.grid(row=0,column=1,rowspan=3)
            self.Blue_offset += 1


        self.Red_offset = 1
        for players in self.Redteam:
            myFrame = Frame(self.PlayerFrame,bd=4,relief=SUNKEN)
            myFrame.grid(row=self.Red_offset,column=2)

            Label(myFrame,text=players[1]).grid(row=0,column=0)
            Label(myFrame,text="%s %s"%(players[2],players[3])).grid(row=1,column=0)
            Label(myFrame,text="Mastery").grid(row=2,column=0)
            if not os.path.isfile(os.getcwd()+"\\images\\%s.png"%(str(players[5]))):
                urlretrieve(self.ddragoncdn%(str(self.ddragonversion).strip(),str(players[5])),os.getcwd()+"\\images\\%s.png"%(str(players[5])))
            champphoto = Image.open(os.getcwd()+"\\images\\%s.png"%(str(players[5])))
            imageobject = ImageTk.PhotoImage(champphoto)
            photolabel = Label(myFrame,image=imageobject)
            photolabel.image = imageobject
            photolabel.grid(row=0,column=1,rowspan=3)
            self.Red_offset += 1



        #Cant create champion mastery per player due to quota limits
        """self.Blueteam = []
        self.Redteam = []
        db = shelve.open("champions")
        for players in self.Gamedata.BluePlayers:
            Username = players[1]
            SummonerData = request_oop.Summoner(Username,self.Summoner.API)
            League,Tier = Summoner.getTier()
            for data in self.Gamedata.BlueChampions:
                if data[0] == players[0]:
                    ChampionId = data[2]
            self.Blueteam.append([players[1],League,Tier,ChampionId])

        for players in self.Gamedata.RedPlayers:
            Username = players[1]
            SummonerData = request_oop.Summoner(Username,self.Summoner.API)
            League,Tier = Summoner.getTier()
            for data in self.Gamedata.RedChampions:
                if data[0] == players[0]:
                    ChampionId = data[2]
            self.Redteam.append([players[1],League,Tier,ChampionId,SummonerData])


        self.Blue_offset = 0
        for players in self.Blueteam:
            myFrame = Frame(self.PlayerFrame,bd=4,relief=SUNKEN)
            myFrame.grid(row=self.Blue_offset,column=0)

            Label(myFrame,text=players[0]).grid(row=0,column=0)
            Label(myFrame,text="%s %s"%(players[1],players[2])).grid(row=1,column=0)

            clevel,cpoints = players[4].getChampionData(players[3]).split()

            for vars in db:
                if vars["id"] == players[3]:
                    championname = vars["kr"]
            Label(myFrame,text="%s Lv.%s %s점"%(championname,clevel,cpoints)).grid(row=2,column=0)"""

    def endclock(self):
        self.workvar.set(False)
    def research(self):
        self.endclock()
        searchagain()

class UserInfoScreen(Frame):
    def __init__(self,master):
        clearscreen()
        Frame.__init__(self,master)
        self.master = master
        self.menu = Frame(self)
        self.menu.pack(side=TOP,fill=X)
        Button(self.menu,text="Exit",command=terminate).pack(side=RIGHT)
        Button(self.menu,text="Update Position",command=setpos).pack(side=RIGHT)
        Button(self.menu,text="Search Again",command=searchagain).pack(side=RIGHT)
        self.pack(expand=YES,fill=BOTH)
    def search(self,username,region):
        self.username = username
        self.region = region
        try:
            self.Summoner = request_oop.Summoner(self.username,request_oop.RiotAPI(self.region,APIKEY))
        except NoUserError:
            showerror("LolUtils","No such user")
            restart()
        except TechnicalError:
            showerror("LolUtils","Unable to get info from server. Please try again")
        else:

            self.league,self.tier = self.Summoner.getTier().split("-")
            self.createwidgets()
    def createwidgets(self):
        Label(self,text=self.username).pack(side=TOP,fill=X)

        self.userinfopanel = Frame(self,bd=4,relief=SUNKEN)
        self.userinfopanel.pack(side=TOP,fill=X)
        Label(self.userinfopanel,text="%s %s"%(self.league,self.tier)).pack(side=LEFT)

        self.imagename = self.league.lower() if self.league != "UNRANKED" else "provisional"
        #self.tierphoto = PhotoImage(file=os.getcwd()+"\\images\\base_icons\\%s.png"%(self.imagename))
        self.tierphoto = Image.open(os.getcwd()+"\\images\\base_icons\\%s.png"%(self.imagename))
        self.tierphotoobject = ImageTk.PhotoImage(self.tierphoto)
        Label(self.userinfopanel,image=self.tierphotoobject).pack(side=RIGHT,anchor=NE)
        Button(self,text="Get Live Game",command=lambda:getlivegame_handler(self.Summoner)).pack(fill=X)
        Label(self,text="챔피언 숙련도").pack(fill=X)

        self.MasteryCanvas = Canvas(self,bd=4,relief=SUNKEN)
        self.MasteryCanvasScrollbar = Scrollbar(self,orient=VERTICAL,command=self.MasteryCanvas.yview)
        self.MasteryCanvas.configure(yscrollcommand=self.MasteryCanvasScrollbar.set)
        self.MasteryCanvasScrollbar.pack(side=RIGHT,anchor=E,fill=Y)
        self.MasteryCanvas.pack(side=TOP,expand=YES,fill=BOTH)
        self.MasteryFrame = Frame(self.MasteryCanvas)
        self.MasteryCanvas.create_window((0,0),window=self.MasteryFrame,anchor='nw')
        self.MasteryFrame.bind("<Configure>",self.onMasteryScroll)

        self.MostChampions = self.Summoner.getMostChampionData(8)

        self.ddragonversion = str(getddragonversion())
        self.ddragoncdn = "http://ddragon.leagueoflegends.com/cdn/%s/img/champion/%s.png"
        db = shelve.open("champions")

        offset=0

        for items in self.MostChampions:

            for keys in db:
                if db[keys]["id"] == items[0]:
                    self.MasteryFrame.columnconfigure(offset, weight=1)
                    self.MasteryFrame.rowconfigure(offset, weight=1)
                    if not os.path.isfile(os.getcwd()+"\\images\\%s.png"%(str(keys))):
                        urlretrieve(self.ddragoncdn%(str(self.ddragonversion).strip(),str(keys)),os.getcwd()+"\\images\\%s.png"%(str(keys)))
                    dataframe = Frame(self.MasteryFrame,bd=4,relief=RAISED)
                    dataframe.grid(row=offset,column=0,sticky=E+W+N+S,columnspan=2)


                    Label(dataframe,text=db[keys]["kr"]).grid(row=0,column=0)
                    Label(dataframe,text="Level %s"%(items[1])).grid(row=1,column=0)
                    Label(dataframe,text="Points %s"%(items[2])).grid(row=2,column=0)
                    champphoto = Image.open(os.getcwd()+"\\images\\%s.png"%(str(keys)))
                    imageobject = ImageTk.PhotoImage(champphoto)
                    photolabel = Label(dataframe,image=imageobject)
                    photolabel.image = imageobject
                    photolabel.grid(row=0,column=1,rowspan=3)
                    offset += 1

                    break
        db.close()
    def onMasteryScroll(self,event):
        self.MasteryCanvas.configure(scrollregion=self.MasteryCanvas.bbox("all"),width=200,height=200)
class MainScreen(Frame):
    def __init__(self,master):
        Frame.__init__(self,master,bd=4,relief=SUNKEN)
        self.master = master
        self.pack(expand = YES,fill=BOTH)
        self.createwidgets()
    def createwidgets(self):
        self.summonersearch = StringVar()
        self.summonersearch.set("소환사 이름 입력")

        self.region = StringVar()
        self.region.set("kr")
        self.choices = ['kr', 'na', 'eune', 'euw','jp', 'lan','las','oce','ru','tr']

        Grid.rowconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

        self.optionbox = Combobox(self,textvariable=self.region)
        self.optionbox.config(state="readonly")
        self.optionbox["values"] = self.choices
        self.optionbox.current(0)
        self.optionbox.pack(side=LEFT)

        self.summonersearch = StringVar()
        self.summonersearch.set("소환사 이름 입력")
        Button(self,text="검색",command=lambda:searchhandler(self.region,self.summonersearch)).pack(side=RIGHT)
        Entry(self,textvariable=self.summonersearch).pack(fill=X,side=RIGHT)
    def close(self):
        self.destroy()

def getupdate():
    hostname =urlopen("http://www.dashadower-1.appspot.com/updateinfo")
    url = str(hostname.read().decode("utf-8")).rstrip()
    data = json.loads(url)
    if float(data["version"]) > VERSION:
        showinfo("LolUtils","새로운 버전이 있습니다. http://dashadower-1.appspot.com/lolutils에서 다운받으세요.")


def downloadtiericons():

    os.mkdir(os.getcwd()+"\\images")
    hostname =urlopen("http://www.dashadower-1.appspot.com/tiericons")
    url = str(hostname.read().decode("utf-8")).rstrip()

    file_name,hook = urlretrieve(url,os.getcwd()+"\\images\\tiericons.zip")
    with zipfile.ZipFile(os.getcwd()+'\\images\\tiericons.zip', "r") as z:
        z.extractall(os.getcwd()+"\\images")
    os.remove(str(os.getcwd()+"\\images\\tiericons.zip").replace("\\","/"))

if __name__ == "__main__":
    APIKEY = getAPIKey()
    VERSION = 1.0
    root = Tk()
    root.title("LolUtils")
    if not os.path.isfile("champions.dir"):
        try:
            championfilecreator.recreate_dynamic()
        except HTTPError:
            showerror("LolUtils","데이터베이스를 다운로드할수 없었습니다. 잠시후 다시 시도해주세요")
            root.destroy()
            sys.exit()

    if not win32gui.FindWindow(None,"PVP.Net 클라이언트"):
        showerror("LolUtils","오류:현제 리그 오브 레전드 클라이언트가 실행되어 있지 않습니다. 먼저 실행해주세요")
        terminate()
    lolheight = getPVPWindowLocation()[3]-getPVPWindowLocation()[1]
    #root.overrideredirect(1)
    if not os.path.exists(os.getcwd()+"\\images"):
        try:
            downloadtiericons()
        except HTTPError:
            showerror("LolUtils","이미지를 다운로드할수 없었습니다. 잠시후 다시 시도해주세요")
            root.destroy()
            sys.exit(0)

    root.title("LolUtils")
    root.geometry("400x%d+%d+%d"%(lolheight,getPVPWindowLocation()[2],getPVPWindowLocation()[1]))
    root.resizable(0,0)
    menu = Frame(root)
    menu.pack(side=TOP,fill=X)
    Button(menu,text="Exit",command=terminate).pack(side=RIGHT)
    Button(menu,text="Update Position",command=setpos).pack(side=RIGHT)

    Button(menu,text="Manage Database",command=lambda:championfilereader.ChampionListEditor("Toplevel")).pack(side=RIGHT)
    MainScreen(root)

    """summonersearch = StringVar()
    summonersearch.set("소환사 이름 입력")
    region = StringVar()
    region.set("kr")
    choices = ['kr', 'na', 'eune', 'euw','jp', 'lan','las','oce','ru','tr']

    searchframe = Frame(root,bd=4,relief=SUNKEN)
    searchframe.pack(expand=YES,fill=X)
    Grid.rowconfigure(searchframe, 0, weight=1)
    Grid.columnconfigure(searchframe, 0, weight=1)
    optionbox = Combobox(searchframe,textvariable=region)
    optionbox.config(state="readonly")
    optionbox["values"] = choices
    optionbox.current(0)
    optionbox.pack(side=LEFT)
    Button(searchframe,text="Search",command=search).pack(side=RIGHT)
    Entry(searchframe,textvariable=summonersearch).pack(fill=X,side=RIGHT)"""



    root.mainloop()