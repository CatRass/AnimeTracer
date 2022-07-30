import os,re,json,time,urllib.request,threading
import tkinter
from tkinter import *
from tkinter import ttk
from mal import * # Library Bindings: https://github.com/darenliang/mal-api/tree/master/mal
from PIL import ImageTk, Image
from pypresence import Presence
import settings as settings

def startup():
    global username, animeAmount, hoursAmount, RPC
    try:
        json_file = open("userfile.json")
        data = json.load(json_file)
        json_file.close()

        username = data["username"]
        animeAmount = data["animeWatched"]
        hoursAmount = data["hoursWatched"]
        print("LOG: Loaded existing userfile.json")
    except:
        open("userfile.json", "w")
        def write_json(new_data, filename):
            with open(filename,'r+') as file:
                file.seek(0)
                json.dump(new_data, file, indent = 4)
        y = {"username": "User","animeWatched": 0,"hoursWatched": 0,"shows": []}
        write_json(y, 'userfile.json')
        print("LOG: No existing userfile.json, created new one")
        json_file = open("userfile.json")
        data = json.load(json_file)
        json_file.close()

        username = data["username"]
        animeAmount = data["animeWatched"]
        hoursAmount = data["hoursWatched"]

    try:
        os.mkdir("posters")
        print("LOG: Made directory '/posters/'")
    except:
        print("LOG: Directory '/posters/' already exists")
    global DiscordEnabled
    DiscordEnabled = True
    try:
        client_id = '977134880381083718'
        RPC = Presence(client_id)
        RPC.connect()
        RPC.update( details="=Developing=", state="Browsing for Anime",  large_image='logo', large_text='Work in progress image :p')
        print("LOG: Discord Connected")
    except:
        print("LOG: Unable to connect to Discord")
        DiscordEnabled=False
        pass
startup()

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
        self.nameLabel = Label(master, text="AnimeTracer", font=("Arial", 15))
        self.nameLabel.grid(column=0, row=0,padx=10, pady=5, sticky=W, columnspan=5)
        self.usernameLabel = Label(master, text=username,font=("Arial", 10))
        self.usernameLabel.grid(column=0, row=0, padx=self.nameLabel.winfo_reqwidth()+15, pady=5, sticky=W, columnspan=5)
        self.onlineLabel = Label(master, text=self.onlineText, font=("Arial", 10), fg=self.onlineColour)
        self.onlineLabel.grid(column=0, row=0,padx=self.nameLabel.winfo_reqwidth()+self.usernameLabel.winfo_reqwidth()+20, pady=5, sticky=W, columnspan=5)
        self.animeAmountLabel = Label(master, text="Anime Total: " + str(animeAmount),font=("Arial", 10))
        self.animeAmountLabel.grid(column=0, row=0,padx=self.nameLabel.winfo_reqwidth()+self.usernameLabel.winfo_reqwidth()+self.onlineLabel.winfo_reqwidth()+25, pady=5, sticky=W, columnspan=5)
        #Settings Button
        self.settingsButton = Button(master, text="Settings",font=("Arial", 10),command = lambda: settings.GUI("Settings",400,400))
        self.settingsButton.grid(column=0,row=0,sticky=E,padx=300)
# Search Elements
class searchBar(Frame):
    def __init__(self, master):
        #Label for Displaying Search Bar
        self.searchLabel= Label(master, text="Enter Anime Name")
        self.searchLabel.grid(column=0, row=1, pady=5, padx=5, sticky=NW, columnspan=2)
        #Search Bar
        self.animeSearchBar = Entry(master)
        self.animeSearchBar.grid(column=0, row=1, padx=self.searchLabel.winfo_reqwidth()+10, pady=5, ipadx=20, columnspan=2, sticky=NW)
        #Enter Button
        self.enterButton = Button(master, text="Enter")
        self.enterButton.grid(column=0, row=1, padx=self.searchLabel.winfo_reqwidth()+self.animeSearchBar.winfo_reqwidth()+55, pady=5, sticky=NW, columnspan=4)
# Display of Search Results
class searchResults(Frame):
    def __init__(self, master):
        #Anime Results List
        self.animeResults = Listbox(master, selectmode=SINGLE, width=35, height=20)
        self.animeResults.grid(column=0, row=2,padx=5, pady=5, sticky=NW)
        #Label for displaying Poster
        self.imageLabel = Label(master)
        self.imageLabel.grid(column=0,row=2, pady=5, padx=self.animeResults.winfo_reqwidth()+10, ipadx=110, ipady=150, sticky=NW)
        #Label for Anime Title
        self.titleLabel = Label(master, font=("Arial", 10))
        self.titleLabel.grid(column=0, row=2, sticky=NW, padx=self.animeResults.winfo_reqwidth()+240, pady=5, columnspan=1)
        #Label for Episode Details
        self.episodesLabel = Label(master, font=("Arial", 10))
        self.episodesLabel.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+240, pady=30, columnspan=1)
        #Label for Episode Length
        self.episodeLengthLabel = Label(master, font=("Arial", 10))
        self.episodeLengthLabel.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+240, pady=55, columnspan=1)
        #Button for adding shows
        self.addFileButton = Button(master, text="Add to List", state=DISABLED)
        self.addFileButton.grid(column=0, row=2,sticky=NW,padx=self.animeResults.winfo_reqwidth()+240, pady=105, columnspan=1)

# Main Application
class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        # All Required Elements of Application
        self.navBar = navBar(self)
        self.searchBar = searchBar(self)
        self.searchResults = searchResults(self)
        self.configure(bg='lightgray')

        # List Adding Function
        def addToList():
            with open('userfile.json','r+') as file:
                file_data = []
                file_data = json.load(file)
            def write_json(new_data, filename='userfile.json'):
                with open(filename,'r+') as file:
                    file_data = json.load(file)
                    file_data["shows"].append(new_data)
                    file.seek(0)
                    json.dump(file_data, file, indent = 4)
            y = {'name': animeName, 'totalEpisodes': animeEpisodes, 'episodeLength':  int(animeLength), 'episodesWatched': [], 'watched': False}

            global existingAnime
            existingAnime = False
            test=[]

            for result in file_data['shows']:
                test.append(result['name'])
            print(test)
            for i in range(0,len(test)):
                print(test[i])
                if test[i] == animeName:
                    existingAnime = True
            if existingAnime == True:
                pass
            else:
                write_json(y)

        # Scalping Function
        def AnimeTracer():
            def getSelect(event):
                def getSelectThreadFunc():
                    main.config(cursor="wait")
                    selection = self.searchResults.animeResults.curselection()
                    id = search.results[selection[0]].mal_id


                    global animeName, animeEpisodes, animeLength
                    animeName = Anime(search.results[selection[0]].mal_id).title_english
                    print("LOG: animeName = " + animeName)
                    if animeName == None:
                        animeName = str(search.results[selection[0]].title)
                        print("LOG: animeName changed to  " + animeName)

                    poster = Anime(id).image_url
                    posterName = "posters/" + str(animeName) + "_poster.jpg"
                    print("LOG: Saved show poster to: ", posterName)

                    episodes= "Episodes:" + str(search.results[selection[0]].episodes)
                    animeEpisodes = search.results[selection[0]].episodes
                    episodeLength = "Episode Length: " + str(Anime(id).duration)
                    animeLength = re.sub('\D', '', Anime(id).duration)
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
                            RPC.update( details="=Developing=", state=rpcAnimeName, large_image=poster, large_text=str(search.results[selection[0]].title))
                    else:
                        pass

                    self.searchResults.imageLabel.image = img

                    self.searchResults.titleLabel.config(text=animeName)
                    self.searchResults.episodesLabel.config(text=episodes)
                    self.searchResults.episodeLengthLabel.config(text=episodeLength)
                    #showSynopsisLabel.config(text=synopsis)
                    self.searchResults.addFileButton.config(state=ACTIVE, command=addToList)
                    main.config(cursor="")

                getSelectThread = threading.Thread(target=getSelectThreadFunc)
                getSelectThread.start()

            self.searchResults.animeResults.delete(0,END)
            print("LOG: Deleted Past Records")

            find = self.searchBar.animeSearchBar.get()
            search = AnimeSearch(find)

            if DiscordEnabled == True:
                RPC.update( details="=Developing=", state="Searching . . .",  large_image='logo', large_text='Work in progress image :p')
            else:
                print("LOG: Unable to connect to Discord")

            query = []

            def animeSearchFunction():
                main.config(cursor="wait")
                for i in range (0,10):
                        query.append(Anime(search.results[i].mal_id).title_english)
                        if query[i] == None:
                            query.pop(i)
                            query.append(search.results[i].title)
                        print("LOG: Currently at show: " + str(query[i]))

                main.config(cursor="")
                scroll_bar = Scrollbar(main)
                self.searchResults.animeResults.config(yscrollcommand = scroll_bar.set)
                self.searchResults.animeResults.bind('<Double-1>', getSelect)

                for i in range(0, len(query)):
                    self.searchResults.animeResults.insert(END, query[i])
                scroll_bar.config(command = self.searchResults.animeResults.yview )

            searchThread = threading.Thread(target=animeSearchFunction)
            searchThread.start()

        self.searchBar.enterButton.config(command = AnimeTracer)

if __name__ == "__main__":
    main = Tk()
    MainApplication(main).grid(row=0,column=0)
    main.title("AnimeTracer")
    main.geometry('700x400')
    main.resizable(False, False)
    main.mainloop()
