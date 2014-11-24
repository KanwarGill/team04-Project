##Voyage
Voyage currently has 2 components:
* __Web Server__ is capable of editing and displaying all the stored data as well as scopes you will provide to _Explorer_, through your favorite browser. 
* __Explorer__ searches the web using scopes given through to the _Web Server_ and goes for exploring for you. It will automatically store all relevant informations found on the way, so that you can show all the loot through _Web Server_.

##Team ACME

Username  |Name | Email
--------------|-------------------|--------------------------
sunakujira1 | Yuya Iwabuchi | yuya.iwabuchi@gmail.com
sughandj | Jai Sughand | jaisughand@gmail.com
wangx173 | Xiang Wang | rogerxiang.wang@gmail.com
kbridge | Kyle Bridgemohansingh | bsingh.kyle@gmail.com
ryanbelt | Ryan Pan | ryanbelt1993129@hotmail.com

##Requirement

* [Python 2.7.x](https://www.python.org/downloads/release/python-278/) 

##Installation
####Method 1: Through tkinter
* Download, extract the `master` then execute on terminal `python gui.py`
* click `Install` in the pop up GUI.
* Done!

####Method 2: Through terminal
* Download, extract the `master` then execute on terminal `python setup.py` 
* Done!

If any problem occurs, please contact one of us on the email address listed above.

##Usage: Web Server
####Method 1: Through tkinter
* Execute on terminal `python gui.py` then click `Run Server`
* `Stop Server` to stop the server

####Method 2: Through terminal
* Execute on terminal `python Frontend/manage.py runserver`
* Ctr-C to stop the server

Go to http://127.0.0.1:8000/admin


__Login Credentials:__
* User: acme
* Password: cscc01

##Usage: Explorers
####Articles
* To Check Status: `cd src; python executer.py article status; cd ..`
* To Run: `cd src; python executer.py article run; cd ..`
* To Pause: `cd src; python executer.py article pause; cd ..`
* To Stop: `cd src; python executer.py article stop; cd ..`

####Tweets:
* To Check Status: `cd src; python executer.py twitter status; cd ..`
* To Run: `cd src; python executer.py twitter run; cd ..`
* To Pause: `cd src; python executer.py twitter pause; cd ..`
* To Stop: `cd src; python executer.py twitter stop; cd ..`

##Task Board
Our Task Board and Assignment progress is on [Trello](https://trello.com/b/Y08lMCXy/cscc01-acme)

USER: **acmeteam4@gmail.com** Password: **acmeteam4**

In My Boards click **CSCC01-ACME** to see the progress

##Website

Our website is located at team04-Project\Website\index.html

It is organized with all the work in the every Phase so far
