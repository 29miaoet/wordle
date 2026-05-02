#tkinter, getpass, json, re, datetime, pydoc, signal, and sys are all built-in modules.
#You will have to install requests and bs4 if you are running the raw code.

#Included with python
import tkinter as tk
from tkinter import messagebox
from getpass import getpass
import json
import re
from datetime import date
import random
import pydoc
import sys
import os
import signal
#Installed manually, used solely for web scraping.
from bs4 import BeautifulSoup
import requests


#KeyboardInterrupt to exit gracefully.
def handle_ctrl_c(signum, frame):
    print("\n\033[31mKeyboardInterrupt caught! Exiting...\033[0m")
    sys.exit()


#This section initializes all the values and signals needed for the script to function.
signal.signal(signal.SIGINT, handle_ctrl_c)
alphabet = [chr(x) for x in range(97,123)]
word_cache = "words_alpha.txt"
word_pick_list = "words_alpha.txt"
help_page = "help.txt"
settings = "settings.ndjson"
script_dir = os.path.dirname(os.path.abspath(__file__))
word_cache, word_pick_list, help_page, settings = (
    os.path.join(script_dir, p) for p in (word_cache, word_pick_list, help_page, settings)
)

valid_wlen = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 31]
with open(settings, "r") as file:
    first_line = file.readline()
    second_line = file.readline()   
max_guesses = json.loads(first_line)
mode = json.loads(second_line)
max_guesses = {int(k): v for k, v in max_guesses.items()}




#This function checks to see if the word is in the file, simulates "grep".
def is_in(search_term,file_path):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if search_term == line:
                return True
        return False
                
                
                
#This function picks a random word.
def pick_random_word(file_path, wdlen = None):
    
    with open(file_path) as f:
        lines = f.readlines()
        
    if wdlen != None:
        wdlen = int(wdlen)
        words_of_length_n = [word.strip() for word in lines if len(word.strip()) == wdlen]
        random_word = random.choice(words_of_length_n)
        return(random_word)
    else:
        random_line = random.choice(lines).strip()
        return random_line


#This function checks if the entered word is valid.
def is_valid(word,wordlen):
    try:
        if not word.isalpha():
            print("\033[1;31mPlease enter letters only!\033[0m")
            return False
        word = word.lower()
        if len(word) != wordlen: 
            print(f"\033[1;31mWord must be {wordlen} letters!\033[0m")
            return False
            
        if is_in(word,word_cache):
            return True
        else:
            print("\033[1;31mNot a valid word!\033[0m")
            return False
            
            
    except ValueError:
        print("\033[1;31mInput format unsupported!\033[0m")
        return False
        
#This function checks if the entered word is valid for hard mode.
def valid_for_hard_mode(word,glist,ylist):
    if is_valid(word,len(word)):
        wordl = [char for char in word]
        wordslice = wordl[:]
        #Green must match
        for i in range(len(word)):
            if glist[i] != 0:
                if wordl[i] != glist[i]:
                    print("\033[1;31mWord rejected, hard mode!\033[0m")
                    return False
                else:
                    wordl[i] = 0

            
        #Must have yellow
        for i in range(len(word)):
            if ylist[i] != 0:
                if ylist[i] not in wordslice:
                    print("\033[1;31mWord rejected, hard mode!\033[0m")
                    return False
                else:
                    wordslice.remove(ylist[i])
                

    return True
        
#This function contains the actual code to play wordle.
def play_wordle(rlword):
    
    rllist = [char for char in rlword]
    length = len(rlword)

    for j in range(max_guesses[(length)]):
        gsword = input("Enter guess word: ")
        if gsword.lower() == "/quit":
            break
        while not is_valid(gsword,length):
            gsword = input("Enter guess word: ")
            if gsword.lower() == "/quit":
                break
        if gsword.lower() == "/quit":
            break
        if j >= 1:
            if mode["hard_mode"]:
                while not valid_for_hard_mode(gsword,glist,ylist):
                    gsword = input("Enter guess word: ")
                    if gsword.lower() == "/quit":
                        break
            else:
                while not is_valid(gsword,length):
                    gsword = input("Enter guess word: ")
                    if gsword.lower() == "/quit":
                        break
                
        gsword = gsword.lower()
        gslist = [char for char in gsword]
        wdpool = rllist[:]
        markedlist = [0 for i in range(length)]
        ylist = markedlist[:]
        glist = markedlist[:]
        correct = 0
        for i in range(length):
            if gslist[i] == rlword[i]:
                markedlist[i] = "\033[1;32m" + gslist[i] + "\033[0m"
                glist[i] = gslist[i]
                wdpool.remove(gslist[i])
                correct += 1
        for i in range(length):
            if gslist[i] in wdpool and markedlist[i] == 0:
                markedlist[i] = "\033[1;33m" + gslist[i] + "\033[0m"
                ylist[i] = gslist[i]
                wdpool.remove(gslist[i])
        for i in range(length):
            if markedlist[i] == 0:
                markedlist[i] = gslist[i]
        for el in markedlist:
            print(el, sep = "", end = "")
        print()
        if correct == length:
            print("\n\033[1;32mYou Won!\033[0m")
            print("Total guesses: ", j+1, "\n")
            return True

    print("\n\033[1;31mYou Lost!\033[0m")
    print(f"\033[1;31mThe word was: {rlword}\033[0m\n")
    return False
    


# Web Scraper
#==================================================================================#
def get_wordle_answer(target_date=None):

    if target_date is None:
        target_date = date.today()
    

    slug = target_date.strftime("wordle-today-answer-%B-%d-%Y").lower()
    url = f"https://mashable.com/article/{slug}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=headers).text
    
    soup = BeautifulSoup(html, "html.parser")
    
    scripts = soup.find_all("script", type="application/ld+json")
    
    for script in scripts:
        try:
            data = json.loads(script.string)
        except:
            continue
        
        if data.get("@type") == "NewsArticle":
            article = data.get("articleBody", "")

            match = re.search(
                r'solution to today.*?is\.*\s*([A-Z]{5})',
                article
            )
            
            if match:
                return match.group(1).lower()
    
    raise Exception(f"Answer not found for {target_date}")
    
    
#==================================================================================#

#This function prompts the user to choose a difficulty.
def choose_mode():
    global max_guesses
    max_guesses = {1: 5, 2: 5, 3: 5, 4: 5, 5: 6, 6: 7, 7: 8, 8: 8, 9: 9, 10: 9, 11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 13, 18: 13, 19: 14, 20: 14, 21: 15, 22: 15, 23: 16, 24: 16, 25: 17, 27: 18, 28: 18, 29: 19, 31: 20}
    while True:
        print("Welcome to the settings panel, if you wish to skip any settings, simply press \"s\".\n")
        print("1  2  3  4  5  6  7  8  9  10")
        print("^                           ^")
        print("\033[32mEasiest\033[0m               \033[31mHardest\033[0m")
        rating = input("Enter the difficulty you want (6 is standard) : ")
        if rating.lower() == "s":
            break
        try:
            rating = int(rating)
            if 1 <= rating <= 10:
                max_guesses = dict(zip(max_guesses.keys(), map(lambda x: x + (7-rating), max_guesses.values())))
                break
            else:
                print("\033[31mValue not in accepted range.\033[0m")
        except ValueError:
            print("\033[31mInvalid input!\033[0m")
    while True:
        modeanswer = input("Hard mode?(y/n): ").lower()
        if modeanswer == "y":
            mode["hard_mode"] = True
            break
        elif modeanswer == "n":
            mode["hard_mode"] = False
            break
        elif modeanswer == "s":
            break
        else:
            print("\033[31mInvalid input!\033[0m")
            continue
            
    with open(settings, "w") as file:
        file.write(json.dumps(max_guesses) + "\n")
        file.write(json.dumps(mode) + "\n")



#This function prompts the user to choose a method of playing wordle.
class choose_wordle:
    def __init__(self):
        self.standardfont = ("TkDefaultFont", "14")
    def gen_rand(self):
        def get_input():
            number = entrybox.get()
            try:
                number = int(number)
                if not 0 < number < 31:
                    number = None
            except ValueError:
                number = None
            word = pick_random_word(word_pick_list, number)
            play_wordle(word)
            entry.mainloop()


        menu.destroy()
        entry = tk.Tk()
        entry.grid_rowconfigure([0,1,2], weight=1)
        entry.grid_columnconfigure(0, weight=1)
        label = tk.Label(entry, text="Pick a word length", font=self.standardfont)
        entrybox = tk.Entry(entry, font=self.standardfont)
        enter_button = tk.Button(entry, text="Enter", command=get_input, font=self.standardfont)
        label.grid(row=0, column=0, sticky="nsew")
        entrybox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        enter_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
    def make_wordle(self):
        def get_input_and_validate():
            word = your_word.get()
            try:
                if not word.isalpha():
                    messagebox.showwarning("Invalid Word", "Please enter letters only!")
                elif not is_in(word, word_cache):
                    messagebox.showwarning("Invalid Word", "Not a valid word!")
                else:
                    play_wordle(word)
            except ValueError:
                messagebox.showwarning("Invalid Word!", "Unsupported format!")


        menu.destroy()
        prompt = tk.Tk()
        prompt.grid_rowconfigure([0,1,2], weight=1)
        prompt.grid_columnconfigure(0, weight=1)
 
        label = tk.Label(prompt, text="Enter your word", font=self.standardfont)
        your_word = tk.Entry(prompt, font=self.standardfont)
        enter_button = tk.Button(prompt, text="Enter", command=get_input_and_validate, font=self.standardfont)
        label.grid(row=0, column=0, sticky="nsew")
        your_word.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        enter_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")




        
menuredirect = choose_wordle()
#word = choose_wordle()
#choose_mode()
#print(f"You have {max_guesses[len(word)]} guesses.")
#play_wordle(word)
button_font = ("Segoe UI", "14")
name_font = ("Segoe UI", "18", "bold")

menu = tk.Tk()
menu.grid_rowconfigure([0,1,2,3,4,5], weight=1)
menu.grid_columnconfigure(0, weight=1)

gen_random = tk.Button(menu, text="Generate a random word", command=menuredirect.gen_rand)
make_wordle = tk.Button(menu, text="Make your own wordle", command=menuredirect.make_wordle)
real_wordle = tk.Button(menu, text="Play the NY Times wordle")
how2play = tk.Button(menu, text="How to play")
settings = tk.Button(menu, text="Settings")
qt = tk.Button(menu, text="Quit the program")
name = tk.Label(menu, text="Wordle", font=name_font)

name.grid(row=0, column=0, sticky="nsew")
i = 1
for item in (gen_random, make_wordle, real_wordle, how2play, settings, qt):
    item.config(font=button_font)
    item.grid(row=i, column=0, sticky="nsew", padx=10)
    i += 1

menu.mainloop()






