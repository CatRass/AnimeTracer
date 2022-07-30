import os,re,json,time,urllib.request,threading,tkinter,sys
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from mal import * #Library Bindings: https://github.com/darenliang/mal-api/episodeTable/master/mal
from mal import config
from AnilistPython import Anilist  #Library Wiki: https://github.com/ReZeroE/AnilistPython/wiki#anime-overview
from PIL import ImageTk, Image
from pypresence import Presence
from requests.exceptions import Timeout

config.TIMEOUT = 1

global anilist
anilist = Anilist()
def statsLoad():
    global username, animeAmount, hoursAmount
    json_file = open("userfile.json")
    data = json.load(json_file)
    json_file.close()

    username = data["username"]
    animeAmount = data["animeWatched"]
    hoursAmount = data["hoursWatched"]
    print("LOG: Loaded existing userfile.json")
def startup():
    global RPC, DiscordEnabled,RPCTime
    DiscordEnabled = True

    # Json Loader
    try:
        statsLoad()
    except:
        open("userfile.json", "w")
        def write_json(new_data, filename):
            with open(filename,'r+') as file:
                file.seek(0)
                json.dump(new_data, file, indent = 4)
        y = {"username": "User","animeWatched": 0,"hoursWatched": 0,"Shows": []}
        write_json(y, 'userfile.json')
        print("LOG: No existing userfile.json, created new one")
        statsLoad()

    # Poster Loader
    try:
        os.mkdir("posters")
        print("LOG: Made directory '/posters/'")
    except:
        print("LOG: Directory '/posters/' already exists")

    # Discord Loader
    try:
        client_id = '977134880381083718'
        RPC = Presence(client_id)
        RPC.connect()
        RPCTime = time.time()
        RPC.update( details="=Developing=", state="Starting...",  large_image='logo', large_text='Totally not stolen icon')
        print("LOG: Discord Connected")
    except:
        print("LOG: Unable to connect to Discord, passing")
        DiscordEnabled=False
        pass
startup()

#Code from: https://stackoverflow.com/q/20399243/12884111
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
#===============================

#   === Application Elements ===
# Top Nav Bar Elements
class navBar(Frame):

    if DiscordEnabled == True:
        onlineColour = "green"
        onlineText = "• Discord Online"
    else:
        onlineColour = "red"
        onlineText = "• Discord Offline"

    def __init__(self, master):
        #Label for displaying name
        self.nameLabel = Label(master, text="AnimeTracer", font=("Arial bold", 15))
        self.nameLabel.grid(column=0, row=0,padx=10, pady=5, sticky=W, columnspan=5)
        self.usernameLabel = Label(master, text=username,font=("Arial", 10))
        self.usernameLabel.grid(column=0, row=0, padx=self.nameLabel.winfo_reqwidth()+15, pady=5, sticky=W, columnspan=5)
        self.onlineLabel = Label(master, text=self.onlineText, font=("Arial", 10), fg=self.onlineColour)
        self.onlineLabel.grid(column=0, row=0,padx=self.nameLabel.winfo_reqwidth()+self.usernameLabel.winfo_reqwidth()+20, pady=5, sticky=W, columnspan=5)
        self.animeAmountLabel = Label(master, text="Anime Total: " + str(animeAmount),font=("Arial", 10))
        self.animeAmountLabel.grid(column=0, row=0,padx=self.nameLabel.winfo_reqwidth()+self.usernameLabel.winfo_reqwidth()+self.onlineLabel.winfo_reqwidth()+25, pady=5, sticky=W, columnspan=5)
        #Settings Button
        # self.settingsButton = Button(master, text="Settings",font=("Arial", 10),command = lambda: settings.GUI("Settings",400,400))
        # self.settingsButton.grid(column=0,row=0,sticky=E,padx=300)
# Search Elements
class searchBar(Frame):
    def __init__(self, master):
        #Label for Displaying Search Bar
        self.searchLabel= Label(master, text="Enter Anime Name")
        self.searchLabel.grid(column=0, row=1, pady=5, padx=5, sticky=NW, columnspan=2)
        #Search Bar
        self.animeSearchBar = Entry(master)
        self.animeSearchBar.grid(column=0, row=1, padx=self.searchLabel.winfo_reqwidth()+10, pady=5, ipadx=20, columnspan=2, sticky=W)
        #Enter Button
        self.enterButton = Button(master, text="Enter")
        self.enterButton.grid(column=0, row=1, padx=self.searchLabel.winfo_reqwidth()+self.animeSearchBar.winfo_reqwidth()+55, pady=5, sticky=NW, columnspan=4)
        #Search Bar
        self.returnToLists = Button(master, text="Return to Lists")
        self.returnToLists.grid(column=0, row=1, padx=self.enterButton.winfo_reqwidth()+self.searchLabel.winfo_reqwidth()+self.animeSearchBar.winfo_reqwidth()+60, pady=5, columnspan=3, sticky=NW)
# Display of Search Results
class searchResults(Frame):
    def __init__(self, master):

        clicked = StringVar()
        # initial menu text
        clicked.set( "List to Add To" )

        #Anime Results List
        self.animeResults = Listbox(master, selectmode=SINGLE, width=35, height=20)
        self.animeResults.grid(column=0, row=2,padx=5, pady=5, sticky=NW)
        #Label for displaying Poster
        self.imageLabel = Label(master)
        self.imageLabel.grid(column=0,row=2, pady=5, padx=self.animeResults.winfo_reqwidth()+10, ipadx=110, ipady=150, sticky=NW)
        #Label for Anime Title
        self.titleLabel = Label(master, font=("Arial bold", 10))
        self.titleLabel.grid(column=0, row=2, sticky=NW, padx=self.animeResults.winfo_reqwidth()+250, pady=5, columnspan=1)
        #Label for Episode Details
        self.episodesLabel = Label(master, font=("Arial", 10))
        # self.episodesLabel.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+250, pady=30, columnspan=1)
        #Label for Episode Length
        self.episodeLengthLabel = Label(master, font=("Arial", 10))
        # self.episodeLengthLabel.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+250, pady=55, columnspan=1)
        #Dropdown List Menu
        self.drop = ttk.Combobox(master, textvariable="List to Add To" )
        self.drop.configure(state=DISABLED)
        self.drop.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+250, pady=105, columnspan=3)
        #Button for adding shows
        self.addFileButton = Button(master, text="Add to List", state=DISABLED)
        self.addFileButton.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+250, pady=135, columnspan=1)
# Class for Displaying userfile List contents
class listDisplay(Frame):
    def __init__(self, master):

        columns = ('show_name', 'episodes_watched', 'total_episodes','next_episode')
        self.episodeTable = ttk.Treeview(master, columns=columns, show='headings')

        self.episodeTable.column("episodes_watched",anchor=CENTER, stretch=NO, width=120)
        self.episodeTable.column("total_episodes",anchor=CENTER, stretch=NO, width=120)
        self.episodeTable.column('next_episode',anchor=CENTER, stretch=NO, width=120)

        self.episodeTable.grid(column=0,row=1)
        self.episodeTable.heading('show_name', text='Show Name')
        self.episodeTable.heading('episodes_watched', text='Episodes Watched')
        self.episodeTable.heading('total_episodes', text='Amount of Episodes')
        self.episodeTable.heading('next_episode', text='Next Episode')
        self.episodeTable.bind('<Motion>', 'break')

        self.listSelect = ttk.Combobox(master, textvariable="List to Add To" )
        self.listSelect.configure(state="readonly")
        self.listSelect.grid(column=0, row=2,sticky=NW,padx=5, pady=5, columnspan=3)

        self.deleteListButton = Button(master,text="Delete List")
        self.deleteListButton.grid(column=0,row=2,sticky=NW,padx=5, pady=self.listSelect.winfo_reqheight()+5)

        self.addShowButton = Button(master,text="Add Show to List")
        self.addShowButton.grid(column=0,row=2,sticky=NE,padx=5, pady=5)
# Displays show info
class showDisplay(Frame):
    def __init__(self, master):

        self.progressBar = ttk.Progressbar(master, orient=HORIZONTAL, mode = 'determinate')

        master.columnconfigure(1, weight=4)
        self.showName = Label(master,font=("Arial", 15),wraplengt=350,justify=LEFT)
        self.listName = Label(master,font=("Arial", 10))
        self.listChangeOption = ttk.Combobox(master,state="readonly")
        #self.listChangeButton = Button(master,text="Change List")

        self.posterLabel = Label(master)
        self.posterLabel.grid(column=0,row=1, pady=5, padx=10)

        self.backButton = Button(master,text="Back")
        self.backButton.grid(column=1,row=1,sticky=S)

        self.episodesFrame = LabelFrame(master,text="Episodes")
        self.episodesFrame.grid(column=1,row=1,sticky=SW)
        self.episodesScrollBox= ScrolledText(self.episodesFrame, width=16, height=8,bg='whitesmoke',state=DISABLED)
        self.episodesScrollBox.pack(side=TOP)

        self.episodesSelectFrame = Frame(self.episodesFrame)
        self.episodesSelectFrame.pack()
        self.episodeRange = Text(self.episodesSelectFrame, width=15, height=1)
        self.episodeRange.pack(side=LEFT)
        self.episodeRangeSelect = Button(self.episodesSelectFrame, text="Enter")
        self.episodeRangeSelect.pack(side=RIGHT)

        self.markAllAsWatched = Button(self.episodesFrame,text="Mark All As Watched")
        self.markAllAsWatched.pack()
        self.saveEpisodes = Button(self.episodesFrame, text="Save Preferences")
        self.saveEpisodes.pack()

        self.checkboxes_dictionary={}


        # self.episodesFrame = ttk.Labelframe(master,text='Episodes', width=100, height=50)
        # self.episodesFrame.grid(column=0,row=1)
#   ===============================

#   === Application Popups ===
# Window for a popup that creates a new list
class createNewListPopup(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        top.title("")
        top.geometry('200x70')
        top.resizable(False, False)

        self.Label=Label(top,text="Enter the name of your new list:")
        self.Label.pack()
        self.Entry=Entry(top)
        self.Entry.pack()
        self.Button=Button(top,text='Ok')
        self.Button.pack()

    def cleanup(self):
        self.value=self.Entry.get()
        self.top.destroy()
#   ===============================

#   === Application Windows ===
# Main Application
class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        # All Required Elements of Application
        self.navBar = navBar(self)
        self.searchBar = searchBar(self)
        self.searchResults = searchResults(self)
        #self.configure(bg='lightgray')

        # List Adding Function
        def addToList(listName):
            global existingAnime
            currentShows=[]

            def showAdder(var):
                with open('userfile.json','r+') as file:
                    file_data = []
                    file_data = json.load(file)
                def write_json(new_data, filename='userfile.json'):
                    with open(filename,'r+') as file:
                        file_data = json.load(file)
                        file_data[var].append(new_data)
                        file.seek(0)
                        json.dump(file_data, file, indent = 4)
                y = {'name': animeName,'englishName':animeNameEnglish, 'totalEpisodes': animeEpisodes, 'episodeLength':  int(animeLength), 'episodesWatched': [],'timeSpent':0, 'watched': False}

                existingAnime = False

                for result in file_data[var]:
                    currentShows.append(result['name'])
                for i in range(0,len(currentShows)):
                    print("LOG: Current Shows: {}".format(currentShows[i]))
                    if currentShows[i] == animeName:
                        existingAnime = True

                if existingAnime == True:
                    print("LOG: Anime {} already added, passing".format(animeName))
                    pass
                else:
                    print("LOG: Anime {} not already added. Adding.".format(animeName))
                    write_json(y)

            if listName == "Create New List":
                print("LOG: Creating New List")
                self.listCreate = createNewListPopup(self)
                def getListName():
                    newListName = self.listCreate.Entry.get()
                    self.listCreate.top.destroy()
                    try:
                        showAdder(newListName)
                    except:
                        with open('userfile.json','r+') as file:
                            file_data = []
                            file_data = json.load(file)
                        def write_json(new_data, filename):
                            with open(filename,'r+') as file:
                                file.seek(0)
                                json.dump(new_data, file, indent = 4)
                        file_data.update({newListName:[]})
                        y = file_data
                        write_json(y, 'userfile.json')
                    showAdder(newListName)
                self.listCreate.Button.config(command=getListName)
            elif listName == "Pick a List":
                return
            else:
                try:
                    showAdder(listName)
                except:
                    with open('userfile.json','r+') as file:
                        file_data = []
                        file_data = json.load(file)
                    def write_json(new_data, filename):
                        with open(filename,'r+') as file:
                            file.seek(0)
                            json.dump(new_data, file, indent = 4)
                    file_data.update({listName:[]})
                    y = file_data
                    write_json(y, 'userfile.json')
                showAdder(listName)
        # Scalping Function
        def AnimeTracer(event):
            global query

            # Searches for Anime using mal-api
            def animeSearchFunction():
                self.searchBar.animeSearchBar.config(state=DISABLED)
                #main.config(cursor="wait")
                for i in range (0,10):
                        query.append(Anime(search.results[i].mal_id).title)
                        print("LOG: Currently at show: {}".format(str(query[i])))

                main.config(cursor="")

                self.searchBar.animeSearchBar.config(state="normal")

                main.config(cursor="")

                scroll_bar = Scrollbar(main)
                self.searchResults.animeResults.config(yscrollcommand = scroll_bar.set)
                self.searchResults.animeResults.bind('<Double-1>', getSelect)
                self.searchResults.animeResults.bind('<Return>', getSelect)

                for i in range(0, len(query)):
                    self.searchResults.animeResults.insert(END, query[i])
                scroll_bar.config(command = self.searchResults.animeResults.yview )
                self.bell()
            # Retrieves information for selected animeResult
            def getSelect(getSelect):
                def getSelectThreadFunc():
                    try:
                        #main.config(cursor="wait")
                        selection = self.searchResults.animeResults.curselection()
                        print("LOG: retrieving details for: {} with AnilistPython".format(search.results[selection[0]].title))
                        show = anilist.get_anime(search.results[selection[0]].title)
                        id = search.results[selection[0]].mal_id


                        global animeName, animeEpisodes, animeLength,animeNameEnglish
                        animeName = str(show['name_romaji'])
                        if show['name_english'] != None:
                            animeNameEnglish = str(show['name_english'])
                        else:
                            animeNameEnglish = str(animeName)
                        print("LOG: animeName = {}".format(str(animeName)))

                        poster = show['cover_image']
                        posterName = "posters/" + str(animeName) + "_poster.png"

                        try:
                            episodes= "Episodes:" + str(show['next_airing_ep']['episode'])
                            animeEpisodes = show['next_airing_ep']['episode']
                        except:
                            episodes= "Episodes:" + str(show["airing_episodes"])
                            animeEpisodes = show["airing_episodes"]

                        episodeLength = "Episode Length: " + str(Anime(id).duration)
                        try:
                            rawDuration = str(Anime(id).duration)
                            time = rawDuration.split(" hr. ")
                            time[1] = time[1].replace(" min.","")
                            minuteTime = int(time[0])*60+int(time[1])
                        except:
                            minuteTime = re.sub('\D', '', Anime(id).duration)
                        animeLength = minuteTime
                        synopsis =  Anime(id).synopsis

                        rpcAnimeName = "Browsing: "+ animeName

                        try:
                            self.searchResults.imageLabel.config(image=None)
                            img = ImageTk.PhotoImage(Image.open(posterName.replace(":", "")))
                            self.searchResults.imageLabel.config(image=img)
                            self.searchResults.imageLabel.grid(ipadx=0,ipady=0)
                            print("LOG: Found show poster on Harddrive")
                        except:
                            self.searchResults.imageLabel.config(image=None)
                            opener = urllib.request.build_opener()
                            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                            urllib.request.install_opener(opener)
                            urllib.request.urlretrieve(str(poster), posterName.replace(":", ""))
                            img = ImageTk.PhotoImage(Image.open(posterName.replace(":", "")))
                            self.searchResults.imageLabel.config(image=img)
                            self.searchResults.imageLabel.grid(ipadx=0,ipady=0)
                            print("LOG: Found show poster found Online")
                            print("LOG: Saved show poster to: {}".format(posterName))
                        if DiscordEnabled == True:
                            try:
                                RPC.update( details="=Developing=", state=rpcAnimeName, large_image=poster, large_text=str(search.results[selection[0]].title),start=RPCTime,buttons=[{"label": "GitHub", "url": "https://www.github.com/CatRass"}])
                            except:
                                pass
                        else:
                            pass

                        self.searchResults.imageLabel.image = img

                        self.searchResults.titleLabel.config(text=animeName,wraplengt=250,justify=LEFT)
                        self.searchResults.episodesLabel.config(text=episodes)
                        self.searchResults.episodeLengthLabel.config(text=episodeLength)

                        self.searchResults.titleLabel.grid(column=0, row=2, sticky=NW, padx=self.searchResults.animeResults.winfo_reqwidth()+250, pady=5, columnspan=1)
                        self.searchResults.episodesLabel.grid(column=0, row=2,sticky=NW,padx=self.searchResults.animeResults.winfo_reqwidth()+250, pady=self.searchResults.titleLabel.winfo_reqheight()+10, columnspan=1)
                        self.searchResults.episodeLengthLabel.grid(column=0, row=2,sticky=NW,padx=self.searchResults.animeResults.winfo_reqwidth()+250, pady=self.searchResults.titleLabel.winfo_reqheight()+self.searchResults.episodesLabel.winfo_reqheight()+10, columnspan=1)
                        #showSynopsisLabel.config(text=synopsis)

                        self.searchResults.drop.config(state="readonly")
                        fileObject = open("userfile.json", "r")
                        jsonContent = fileObject.read()
                        aList = json.loads(jsonContent)
                        bList = list(aList.keys())
                        bList.pop(0)
                        bList.pop(0)
                        bList.pop(0)
                        bList.append("Create New List")
                        print(bList)
                        self.searchResults.drop['values'] = (bList)

                        if self.searchResults.drop.get() == "":
                            self.searchResults.drop.set("Pick a List")
                        else:
                            pass

                        self.searchResults.addFileButton.config(state=ACTIVE, command=lambda:addToList(self.searchResults.drop.get()))
                        main.config(cursor="")

                    except:
                        print("LOG: Anime doesn't exist on Anilist.")
                        print("LOG: retrieving details for: '{}' with mal-api".format(search.results[selection[0]].title))
                        #main.config(cursor="wait")
                        selection = self.searchResults.animeResults.curselection()
                        id = search.results[selection[0]].mal_id

                        animeNameEnglish = str(Anime(search.results[selection[0]].mal_id).title_english)
                        if animeNameEnglish == None:
                            animeName = str(search.results[selection[0]].title)
                            animeNameEnglish = animeName
                        else:
                            animeName = str(search.results[selection[0]].title)
                        print("LOG: animeName = {}".format(str(animeName)))

                        poster = Anime(id).image_url
                        posterName = "posters/{}_poster.jpg".format(str(animeName))
                        print("LOG: Saved show poster to: {}".format(posterName))

                        episodes= "Episodes:{}".format(str(search.results[selection[0]].episodes))
                        animeEpisodes = search.results[selection[0]].episodes
                        episodeLength = "Episode Length: {}".format(str(Anime(id).duration))
                        try:
                            rawDuration = str(Anime(id).duration)
                            time = rawDuration.split(" hr. ")
                            time[1] = time[1].replace(" min.","")
                            minuteTime = int(time[0])*60+int(time[1])
                        except:
                            minuteTime = re.sub('\D', '', Anime(id).duration)
                        animeLength = minuteTime
                        synopsis =  Anime(id).synopsis

                        rpcAnimeName = "Browsing: "+ animeName

                        try:
                            self.searchResults.imageLabel.config(image=None)
                            img = ImageTk.PhotoImage(Image.open(posterName.replace(":", "")))
                            self.searchResults.imageLabel.config(image=img)
                            self.searchResults.imageLabel.grid(ipadx=0,ipady=0)
                            print("LOG: Found show poster on Harddrive")
                        except:
                            self.searchResults.imageLabel.config(image=None)
                            urllib.request.urlretrieve(str(poster), posterName.replace(":", ""))
                            img = ImageTk.PhotoImage(Image.open(posterName.replace(":", "")))
                            self.searchResults.imageLabel.config(image=img)
                            self.searchResults.imageLabel.grid(ipadx=0,ipady=0)
                            print("LOG: Found show poster found Online")
                        if DiscordEnabled == True:
                                RPC.update( details="=Developing=", state=rpcAnimeName, large_image=poster, large_text=str(search.results[selection[0]].title),start=RPCTime,buttons=[{"label": "GitHub", "url": "https://www.github.com/CatRass"}])
                        else:
                            pass

                        self.searchResults.imageLabel.image = img

                        self.searchResults.titleLabel.config(text=animeName,wraplengt=250,justify=LEFT)
                        self.searchResults.episodesLabel.config(text=episodes)
                        self.searchResults.episodeLengthLabel.config(text=episodeLength)

                        self.searchResults.titleLabel.grid(column=0, row=2, sticky=NW, padx=self.searchResults.animeResults.winfo_reqwidth()+250, pady=5, columnspan=1)
                        self.searchResults.episodesLabel.grid(column=0, row=2,sticky=NW,padx=self.searchResults.animeResults.winfo_reqwidth()+250, pady=self.searchResults.titleLabel.winfo_reqheight()+10, columnspan=1)
                        self.searchResults.episodeLengthLabel.grid(column=0, row=2,sticky=NW,padx=self.searchResults.animeResults.winfo_reqwidth()+250, pady=self.searchResults.titleLabel.winfo_reqheight()+self.searchResults.episodesLabel.winfo_reqheight()+10, columnspan=1)

                        self.searchResults.drop.config(state="readonly")
                        fileObject = open("userfile.json", "r")
                        jsonContent = fileObject.read()
                        aList = json.loads(jsonContent)
                        bList = list(aList.keys())
                        bList.pop(0)
                        bList.pop(0)
                        bList.pop(0)
                        bList.append("Create New List")
                        print(bList)
                        self.searchResults.drop['values'] = (bList)

                        if self.searchResults.drop.get() == "":
                            self.searchResults.drop.set("Pick a List")
                        else:
                            pass

                        self.searchResults.addFileButton.config(state=ACTIVE, command=lambda:addToList(self.searchResults.drop.get()))
                        main.config(cursor="")

                getSelectThread = threading.Thread(target=getSelectThreadFunc)
                getSelectThread.start()
            # Attempts to find English titles using AnilistPython
            def romajiTranslator(event):
                index = self.searchResults.animeResults.curselection()
                show = anilist.get_anime(query[index[0]])
                if show['name_english'] == None:
                    print("LOG: No English name found for: {}".format(show['name_romaji']))
                    return
                else:
                    print("LOG: English name found for: '{}': '{}'".format(show['name_romaji'],show['name_english']))
                    self.searchResults.animeResults.delete(index[0],index[0])
                    self.searchResults.animeResults.insert(index[0], show['name_english'])

            # Thread that allows for animeSearchFunction to run in the background while cursor loads
            try:
                searchThread = threading.Thread(target=animeSearchFunction)
            except Timeout:
                print("LOG: !!Timeout occurred!!")
                main.config(cursor="")
                self.bell()
                searchThread.join()
                return

            self.searchResults.animeResults.delete(0,END)
            print("LOG: Deleted Past Records")

            find = self.searchBar.animeSearchBar.get()
            # Validation for empty search term
            if find == "":
                print("LOG: User attempted to search an empty term. Notifying now")
                messagebox.showwarning(title="Error: Invalid Input", message="You have attempted to search for an empty search term.\nPlease type the anime name into the search box.")
                pass
            else:
                print("LOG: Searching mal-api with search term: '{}'".format(find))
                search = AnimeSearch(find)

                if DiscordEnabled == True:
                    try:
                        RPC.update( details="=Developing=", state="Searching: {}".format(find),  large_image='logo', large_text='Totally not stolen icon',start=RPCTime,buttons=[{"label": "GitHub", "url": "https://www.github.com/CatRass"}])
                    except:
                        pass
                else:
                    print("LOG: Unable to connect to Discord, passing")

                query = []

                searchThread.start()
                self.searchResults.animeResults.bind('<space>',romajiTranslator)

        self.searchBar.animeSearchBar.bind('<Return>',AnimeTracer)

        if DiscordEnabled == True:
            try:
                RPC.update( details="=Developing=", state="Browsing for Anime",  large_image='logo', large_text='Totally not stolen icon',start=RPCTime,buttons=[{"label": "GitHub", "url": "https://www.github.com/CatRass"}])
            except:
                pass
        else:
            print("LOG: Unable to connect to Discord, passing")

        def screenTransition():
            global addToListName
            addToListName = self.searchResults.drop.get()
            for widgets in main.winfo_children():
                  widgets.destroy()
            TrackerApplication(main).grid(row=0,column=0)
        self.searchBar.returnToLists.config(command=screenTransition)
        self.searchBar.enterButton.config(command = lambda:AnimeTracer(None))
# Tracker Application
class TrackerApplication(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.navBar = navBar(self)
        self.listDisplay = listDisplay(self)

        if DiscordEnabled == True:
            try:
                RPC.update( details="=Developing=", state="Inspecting Anime Lists",  large_image='logo', large_text='Totally not stolen icon',start=RPCTime,buttons=[{"label": "GitHub", "url": "https://www.github.com/CatRass"}])
            except:
                pass
        else:
            print("LOG: Unable to connect to Discord, passing")

        # Function that loads initial table from the list "Shows"
        def tableLoader(listName):
            fileObject = open("userfile.json", "r")
            jsonContent = fileObject.read()
            allLists = list(json.loads(jsonContent).keys())

            for i in range(0,3):
                allLists.pop(0)

            allLists.append("Create New List")
            self.listDisplay.listSelect['values'] = (allLists)
            self.listDisplay.listSelect.set(str(listName))

            json_file = open("userfile.json")
            data = json.load(json_file)
            for e in ["username", 'animeWatched','hoursWatched']:
                data.pop(e)

            tableRow = []
            for n in range(0, len(data[listName])):

                try:
                    if data[listName][n]["episodesWatched"][-1]+1 > data[listName][n]["totalEpisodes"]:
                        nextEpisode = "Completed"
                    else:
                        nextEpisode = data[listName][n]["episodesWatched"][-1]+1
                except:
                    nextEpisode = 1

                tableRow.append((f'{data[listName][n]["englishName"]}', f'{len(data[listName][n]["episodesWatched"])}', f'{data[listName][n]["totalEpisodes"]}', f'{nextEpisode}'))
            for element in tableRow:
                self.listDisplay.episodeTable.insert('', END, values=element)
        #Function that changes the table content depending on selected list
        def tableChanger(event):
            if self.listDisplay.listSelect.get() == "Create New List":
                print("LOG: Creating New List")
                self.listCreate = createNewListPopup(self)
                def getListName():
                    newListName = self.listCreate.Entry.get()
                    self.listCreate.top.destroy()

                    with open('userfile.json','r+') as file:
                        file_data = []
                        file_data = json.load(file)
                    def write_json(new_data, filename):
                        with open(filename,'r+') as file:
                            file.seek(0)
                            json.dump(new_data, file, indent = 4)
                    file_data.update({newListName:[]})
                    y = file_data
                    write_json(y, 'userfile.json')
                    tableLoader(newListName)
                    tableChanger(newListName)
                self.listCreate.Button.config(command=getListName)
                return
            print("LOG: Current List will be changed to: {}".format(self.listDisplay.listSelect.get()))
            for item in self.listDisplay.episodeTable.get_children():
                self.listDisplay.episodeTable.delete(item)
            tableLoader(self.listDisplay.listSelect.get())
        # Deletes Current Selected Lists
        def listDeleter():
            self.bell()
            def confirmationPopup():
                popupWindow = messagebox.askquestion('Warning: Delete List "{}"'.format(self.listDisplay.listSelect.get()),'Are you sure you want to delete this list?\nThis action is irreversible',icon = 'warning')
                if popupWindow == 'yes':
                   self.listDisplay.listSelect.get()
                   with open('userfile.json','r+') as file:
                       file_data = []
                       file_data = json.load(file)
                       file.close()
                   with open('userfile.json','w+') as file:
                       del file_data[self.listDisplay.listSelect.get()]
                       file.seek(0)
                       json.dump(file_data,file,indent=4)
                   tableLoader("Shows")
                   tableChanger(0)
                else:
                    pass
            confirmationPopup()

        try:
            tableLoader(addToListName)
        except:
            fileObject = open("userfile.json", "r")
            jsonContent = fileObject.read()
            showArray = list(json.loads(jsonContent).keys())
            for i in range(0,3):
                showArray.pop(0)

            tableLoader(showArray[0])

        def showEditorTransition(event):
            try:
                global item,listName
                item = self.listDisplay.episodeTable.selection()[0]
                print("LOG: Selected self.listDisplay.episodeTable item with ID: {}".format(item))
                print("LOG: Selected item has name: {}".format(self.listDisplay.episodeTable.item(item, 'values')[0]))
                global showDisplay_ShowName,showDisplay_ListName,showDisplay_episodesAmount
                showDisplay_ShowName = self.listDisplay.episodeTable.item(item, 'values')[0]
                showDisplay_ListName = self.listDisplay.listSelect.get()
                showDisplay_episodesAmount = self.listDisplay.episodeTable.item(item, 'values')[2]

                for widgets in main.winfo_children():
                      widgets.destroy()

                ShowEditorApplication(main).grid(row=0,column=0)

            except IndexError: # In the case of user double clicking the Column Names
                print("LOG: User clicked on a non-show space within  self.listDisplay.episodeTable. Passing.")

        self.listDisplay.listSelect.bind('<<ComboboxSelected>>', tableChanger)
        self.listDisplay.episodeTable.bind("<Double-1>", showEditorTransition)
        self.listDisplay.addShowButton.config(command = lambda:MainApplication(main).grid(row=0,column=0))
        self.listDisplay.deleteListButton.config(command = listDeleter)
# Editor for Show Progress
class ShowEditorApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.navBar = navBar(self)
        self.showDisplay = showDisplay(self)

        # Function for all prerequisite JSON data retrievals
        def jsonVariableRetrieval():
            global userfileKeys,data
            jsonShowsVar = open("userfile.json")
            data = json.load(jsonShowsVar)
            for e in ["username", 'animeWatched','hoursWatched']:
                data.pop(e)

            jsonKeysVar = open("userfile.json", "r")
            jsonContent = jsonKeysVar.read()
            userfileKeys = list(json.loads(jsonContent).keys())

            for i in range(0,3):
                userfileKeys.pop(0)
        # Function for all grid roganisation
        def gridOrganiser():
            self.showDisplay.episodesFrame.config(text="Total Episodes: {}".format(showDisplay_episodesAmount))
            self.showDisplay.showName.config(text=showDisplay_ShowName)
            self.showDisplay.listName.config(text="In list: "+showDisplay_ListName)
            self.showDisplay.progressBar.config(length=self.showDisplay.showName.winfo_reqwidth())

            self.showDisplay.progressBar.grid(column=1,row=1,sticky=NW)
            self.showDisplay.showName.grid(padx=5,column=1,row=1,sticky=NW,pady=self.showDisplay.progressBar.winfo_reqheight())
            self.showDisplay.listName.grid(padx=5,column=1,row=1,sticky=NW,pady=self.showDisplay.showName.winfo_reqheight()+self.showDisplay.progressBar.winfo_reqheight())
            self.showDisplay.listChangeOption.grid(padx=5,column=1,row=1,sticky=NW,pady=self.showDisplay.showName.winfo_reqheight()+self.showDisplay.progressBar.winfo_reqheight()+self.showDisplay.listName.winfo_reqheight())


            # userfileKeys.append("Create New List")
            self.showDisplay.listChangeOption.set(str(showDisplay_ListName))
            self.showDisplay.listChangeOption['values'] = (userfileKeys)
        # Function for finding index of show in respective list
        def keyIndexing():
            # Creates a list of each show in list by index in dictionary
            indexedList = {x : data[showDisplay_ListName][x] for x in range(len(data[showDisplay_ListName]))}
            # Finds index of show in dictionary
            for i in range(0,len(indexedList)):
                global indexInList
                if indexedList[i]['englishName'] == str(showDisplay_ShowName):
                    indexInList = i
                    print("LOG: showDisplay_ShowName: '{}' is at index: {}".format(showDisplay_ShowName,indexInList))
                else:
                    pass
        # Function for retrieving poster from /posters/
        def posterRetrieval():
            try:
                self.posterName = str("Posters/{}_poster.png").format(data[showDisplay_ListName][indexInList]['name']).replace(":", "")
                self.showDisplay.posterLabel.config(image=None)
                self.poster = ImageTk.PhotoImage(Image.open(self.posterName))
                self.showDisplay.posterLabel.config(image=self.poster)
                self.showDisplay.posterLabel.grid(ipadx=0,ipady=0)
                print("LOG:  Opened poster found through AniList")
            except:
                self.posterName = str("Posters/{}_poster.jpg").format(data[showDisplay_ListName][indexInList]['name']).replace(":", "")
                self.showDisplay.posterLabel.config(image=None)
                self.poster = ImageTk.PhotoImage(Image.open(self.posterName))
                self.showDisplay.posterLabel.config(image=self.poster)
                self.showDisplay.posterLabel.grid(ipadx=0,ipady=0)
                print("LOG: Opened poster found through mal-api")
        # Function for generating all episode checkboxes
        def episodeSelectionGeneration():
            # This code was created with the help of stackoverflow user "Daniele" in thread:
            # https://stackoverflow.com/q/72760862/12884111
            for alignment in range(1,int(showDisplay_episodesAmount)+1):
                self.showDisplay.checkboxes_dictionary[alignment]=ttk.Checkbutton(self.showDisplay.episodesScrollBox, text="Episode: {}".format(alignment), command= markEpisodeAsWatched)

                if len(data[showDisplay_ListName][indexInList]["episodesWatched"]) == 0: # In case there are no episodes watched
                    self.showDisplay.checkboxes_dictionary[alignment].state(['!alternate'])
                # elif len(data[showDisplay_ListName][indexInList]["episodesWatched"]) == 1: # In case there is one episode watched
                #     self.showDisplay.checkboxes_dictionary[data[showDisplay_ListName][indexInList]["episodesWatched"][0]].state(['selected'])
                #     self.showDisplay.checkboxes_dictionary[alignment].state(['!alternate'])
                else:
                    for i in range(0,len(data[showDisplay_ListName][indexInList]["episodesWatched"])):
                        if data[showDisplay_ListName][indexInList]["episodesWatched"][i] == alignment:
                            self.showDisplay.checkboxes_dictionary[alignment].state(['selected'])
                        else:
                            self.showDisplay.checkboxes_dictionary[alignment].state(['!alternate'])

                self.showDisplay.checkboxes_dictionary[alignment].pack(fill=NONE)
                self.showDisplay.episodesScrollBox.window_create('end', window=self.showDisplay.checkboxes_dictionary[alignment])
                self.showDisplay.episodesScrollBox.insert('end', '\n')

        jsonVariableRetrieval()
        gridOrganiser()
        keyIndexing()

        def backToTrackerApplication():
            statsLoad()
            for widgets in main.winfo_children():
                  widgets.destroy()
            TrackerApplication(main).grid(row=0,column=0)
        def markAllAsWatched():
            for alignment in range(1,int(showDisplay_episodesAmount)+1):
                self.showDisplay.checkboxes_dictionary[alignment].state(['selected'])
            self.showDisplay.markAllAsWatched.config(command=markAllAsUnwatched, text="Mark All As Unwatched")
        def markAllAsUnwatched():
            for alignment in range(1,int(showDisplay_episodesAmount)+1):
                self.showDisplay.checkboxes_dictionary[alignment].state(['!selected'])
            self.showDisplay.markAllAsWatched.config(command=markAllAsWatched, text="Mark All As Watched")
        def markEpisodeAsWatched():
            global episode
            with open('userfile.json','r+') as file:
                file_data = []
                file_data = json.load(file)
                #print(file_data)
            for i in range(1,int(showDisplay_episodesAmount)+1):
                if self.showDisplay.checkboxes_dictionary[i].state() == ('active', 'focus', 'selected', 'hover'):
                    print("LOG: Activity at {}; selected".format(i))
                    episode = i
                elif self.showDisplay.checkboxes_dictionary[i].state() == ('active', 'focus', 'hover'):
                    print("LOG: Activity at {}; unselected".format(i))
                    episode = i

            episodeStatus = self.showDisplay.checkboxes_dictionary[episode].state()
        def saveEpisodesToFile():
            global checkboxStates, episodeStates

            checkboxStates = []
            episodeStates = []

            for i in range(1,len(self.showDisplay.checkboxes_dictionary)+1):
                self.showDisplay.checkboxes_dictionary[i].state(['!focus'])
                checkboxStates.append(self.showDisplay.checkboxes_dictionary[i].state())

            for i in range(0,len(checkboxStates)):
                try:
                    len(checkboxStates[i][0])
                    episodeStates.append(i+1)
                except:
                    pass

            print(episodeStates)

            with open('userfile.json','r+') as file:
                file_data = json.load(file)
                del file_data[showDisplay_ListName][indexInList]['episodesWatched']
                file_data[showDisplay_ListName][indexInList]['episodesWatched'] = episodeStates
                if len(file_data[showDisplay_ListName][indexInList]['episodesWatched']) == int(showDisplay_episodesAmount):
                    if file_data[showDisplay_ListName][indexInList]['watched'] == True:
                        pass
                    else:
                        file_data[showDisplay_ListName][indexInList]['watched'] = True
                        file_data['animeWatched'] += 1
                del file_data[showDisplay_ListName][indexInList]['timeSpent']
                file_data[showDisplay_ListName][indexInList]['timeSpent'] = file_data[showDisplay_ListName][indexInList]['episodeLength']*len(file_data[showDisplay_ListName][indexInList]['episodesWatched'])
                print("LOG: Minutes spent watching '{}' = {}".format(showDisplay_ShowName,file_data[showDisplay_ListName][indexInList]['timeSpent']))
                print("LOG: Hours spent watching '{}' = {}".format(showDisplay_ShowName,file_data[showDisplay_ListName][indexInList]['timeSpent']/60))
                file.seek(0)
                json.dump(file_data, file, indent=4)
                file.truncate()
            for widgets in main.winfo_children():
                  widgets.destroy()
            ShowEditorApplication(main).grid(row=0,column=0)
        def changeList(event):
            changedList = self.showDisplay.listChangeOption.get()
            if changedList == showDisplay_ListName:
                return
            # elif changedList == "Create New List":
            #     self.listCreate = createNewListPopup(self)
            #     changedList = self.listCreate.Entry.get()
            #     with open('userfile.json','r+') as file:
            #         file_data = json.load(file)
            #         data = file_data[showDisplay_ListName][indexInList]
            #         del file_data[showDisplay_ListName][indexInList]
            #         file_data[changedList].append(data)
            #         print("LOG: Moved {} to list {}".format(showDisplay_ShowName, changedList))
            #         file.seek(0)        # <--- should reset file position to the beginning.
            #         json.dump(file_data, file, indent=4)
            #         file.truncate()     # remove remaining part
            else:
                with open('userfile.json','r+') as file:
                    file_data = json.load(file)
                    data = file_data[showDisplay_ListName][indexInList]
                    del file_data[showDisplay_ListName][indexInList]
                    file_data[changedList].append(data)
                    print("LOG: Moved {} to list {}".format(showDisplay_ShowName, changedList))
                    file.seek(0)        # <--- should reset file position to the beginning.
                    json.dump(file_data, file, indent=4)
                    file.truncate()     # remove remaining part

        self.showDisplay.saveEpisodes.config(command=saveEpisodesToFile)
        self.showDisplay.backButton.config(command=backToTrackerApplication)
        self.showDisplay.markAllAsWatched.config(command=markAllAsWatched)
        self.showDisplay.progressBar['value'] = (len(data[showDisplay_ListName][indexInList]['episodesWatched'])/data[showDisplay_ListName][indexInList]['totalEpisodes'])*100

        posterRetrieval()

        if DiscordEnabled == True:
            try:
                RPC.update( details="=Developing=", state="Inspecting: {}".format(showDisplay_ShowName),  large_image='logo', large_text='Totally not stolen icon',start=RPCTime,buttons=[{"label": "GitHub", "url": "https://www.github.com/CatRass"}])
            except:
                pass
        else:
            print("LOG: Unable to connect to Discord, passing")

        episodeSelectionGeneration()

        #Creates tooltip for explaining how to scroll
        CreateToolTip(self.showDisplay.episodesFrame, "To scroll down or up, please put mouse \n in area between scroll bar and checkbox text.\n This is a bug that needs to be fixed. Thanks!")
        self.showDisplay.listChangeOption.bind('<<ComboboxSelected>>', changeList)
#   ============================

def on_closing():
    print("LOG: Closing Window...")
    try:
        RPC.close()
        print("LOG: Discord RPC Connection Closed")
    except:
        pass
    main.destroy()
    print("LOG: Window Closed")
# The Function 'resource_path' is not my own code.
# This function is provided by the creator of PyInstaller, the Python to Exe compiler I use.
# resource_path() allows for the addition of external files, such as my favicon to be compiled into the 'one file' format.
# It is necessary to compile without any errors.
# Code obtained from: https://nitratine.net/blog/post/issues-when-using-auto-py-to-exe/#the-one-file-resource-wrapper
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
if __name__ == "__main__":
    main = Tk()
    TrackerApplication(main).grid(row=0,column=0)
    main.title("AnimeTracer")
    main.geometry('700x400')
    main.resizable(False, False)
    main.protocol("WM_DELETE_WINDOW", on_closing)
    #photo = PhotoImage(file=resource_path("favicon.png"))  DISABLED DUE TO ERROR: X Error of failed request:  BadLength (poly request too large or internal Xlib length error)
    #main.iconphoto(False, photo)                           DISABLED DUE TO ERROR: X Error of failed request:  BadLength (poly request too large or internal Xlib length error)
    main.mainloop()
