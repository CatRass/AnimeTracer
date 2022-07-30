import os
import re
import json
import time
import tkinter
import threading
from mal import * # Library Bindings: https://github.com/darenliang/mal-api/tree/master/mal
from tkinter import *
import urllib.request
from PIL import ImageTk, Image
from tkinter import ttk
from pypresence import Presence

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

def GUI(title, guiWidth, guiHeight):

    global main, animeResults, titleLabel, episodesLabel, episodeLengthLabel, imageLabel, onlineLabel,  animeSearchBar, addFileButton, showSynopsisLabel

    main = Tk()

    main.title(title)
    main.configure(bg='lightgray')
    main.minsize(guiWidth,guiHeight)
    main.maxsize(guiWidth,guiHeight)

    if DiscordEnabled == True:
        onlineColour = "green"
        onlineText = "• Discord Online"
    else:
        onlineColour = "red"
        onlineText = "• Discord Offline"

    main.rowconfigure(0, weight=4)

    nameLabel = Label(main, text="AnimeTracer", font=("Arial", 15))
    nameLabel.grid(column=0, row=0,padx=10, pady=5, sticky=W, columnspan=5)
    usernameLabel = Label(main, text=username,font=("Arial", 10))
    usernameLabel.grid(column=0, row=0, padx=nameLabel.winfo_reqwidth()+15, pady=5, sticky=W, columnspan=5)
    onlineLabel = Label(main, text=onlineText, font=("Arial", 10), fg=onlineColour)
    onlineLabel.grid(column=0, row=0,padx=nameLabel.winfo_reqwidth()+usernameLabel.winfo_reqwidth()+20, pady=5, sticky=W, columnspan=5)
    animeAmountLabel = Label(main, text="Anime Total: " + str(animeAmount),font=("Arial", 10))
    animeAmountLabel.grid(column=0, row=0,padx=nameLabel.winfo_reqwidth()+usernameLabel.winfo_reqwidth()+onlineLabel.winfo_reqwidth()+25, pady=5, sticky=W, columnspan=5)
    settingsButton = Button(main, text="Settings",font=("Arial", 10),command = lambda: settings.GUI("Settings",400,400))
    settingsButton.grid(column=0,row=0,sticky=E,padx=300)


    animeResults = Listbox(main, selectmode=SINGLE, width=35, height=20)
    animeResults.grid(column=0, row=2,padx=5, pady=5, sticky=NW)

    imageLabel = tkinter.Label()
    imageLabel.grid(column=0,row=2, pady=5, padx=animeResults.winfo_reqwidth()+10, ipadx=110, ipady=150, sticky=NW)
    titleLabel = Label(main, font=("Arial", 10))
    titleLabel.grid(column=0, row=2, sticky=NW, padx=animeResults.winfo_reqwidth()+240, pady=5, columnspan=1)
    episodesLabel = Label(main, font=("Arial", 10))
    episodesLabel.grid(column=0, row=2,sticky=NW,padx=animeResults.winfo_reqwidth()+240, pady=30, columnspan=1)
    episodeLengthLabel = Label(main, font=("Arial", 10))
    episodeLengthLabel.grid(column=0, row=2,sticky=NW,padx=animeResults.winfo_reqwidth()+240, pady=55, columnspan=1)
    addFileButton = Button(main, text="Add to List", state=DISABLED)
    addFileButton.grid(column=0, row=2,sticky=NW,padx=animeResults.winfo_reqwidth()+240, pady=105, columnspan=1)

    searchLabel= Label(main, text="Enter Anime Name")
    searchLabel.grid(column=0, row=1, pady=5, padx=5, sticky=NW, columnspan=2)
    animeSearchBar = tkinter.Entry(main)
    animeSearchBar.grid(column=0, row=1, padx=searchLabel.winfo_reqwidth()+10, pady=5, ipadx=20, columnspan=2, sticky=NW)
    enterButton = tkinter.Button(main, text="Enter", command = AnimeTracer).grid(column=0, row=1, padx=searchLabel.winfo_reqwidth()+animeSearchBar.winfo_reqwidth()+55, pady=5, sticky=NW, columnspan=4)

    main.mainloop()

def AnimeTracer():
    def getSelect(event):
        def getSelectThreadFunc():
            main.config(cursor="wait")
            selection = animeResults.curselection()
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
                imageLabel.config(image=None)
                img = ImageTk.PhotoImage(Image.open(posterName.replace(":", "")))
                imageLabel.config(image=img)
                imageLabel.grid(ipadx=0,ipady=0)
                print("LOG: Found show poster on Harddrive")
            except:
                imageLabel.config(image=None)
                urllib.request.urlretrieve(str(poster), posterName.replace(":", ""))
                img = ImageTk.PhotoImage(Image.open(posterName.replace(":", "")))
                imageLabel.config(image=img)
                imageLabel.grid(ipadx=0,ipady=0)
                print("LOG: Found show poster found Online")
            if DiscordEnabled == True:
                    RPC.update( details="=Developing=", state=rpcAnimeName, large_image=poster, large_text=str(search.results[selection[0]].title))
            else:
                pass

            imageLabel.image = img

            titleLabel.config(text=animeName)
            episodesLabel.config(text=episodes)
            episodeLengthLabel.config(text=episodeLength)
            #showSynopsisLabel.config(text=synopsis)
            addFileButton.config(state=ACTIVE, command=addToList)
            main.config(cursor="")

        getSelectThread = threading.Thread(target=getSelectThreadFunc)
        getSelectThread.start()

    animeResults.delete(0,END)
    print("LOG: Deleted Past Records")

    find = animeSearchBar.get()
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
        animeResults.config(yscrollcommand = scroll_bar.set)
        animeResults.bind('<Double-1>', getSelect)

        for i in range(0, len(query)):
            animeResults.insert(END, query[i])
        scroll_bar.config(command = animeResults.yview )

    searchThread = threading.Thread(target=animeSearchFunction)
    searchThread.start()

def addToList():
    def write_json(new_data, filename='userfile.json'):
        with open(filename,'r+') as file:
            file_data = json.load(file)
            file_data["shows"].append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent = 4)
    y = {'name': animeName, 'totalEpisodes': animeEpisodes, 'episodeLength':  int(animeLength), 'episodesWatched': [], 'watched': False}
    print("LOG: Added " + animeName + " to userfile.json")
    write_json(y)

AnimeTracerThread = threading.Thread(target=GUI, args=("AnimeTracer", 700,400,))
AnimeTracerThread.start()
