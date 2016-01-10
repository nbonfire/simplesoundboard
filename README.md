simplesoundboard
================

A simple soundboard server to be run on an HTPC with a web interface. Getting to be not-so-simple now that we've added midi input, tags, user logins, and entrance music.

Requires: pygame, plus use pip to install packages from requirements.txt

 

1) Create a virtualenv called flask

virtualenv flask

2) use that to install the contents of requirements.txt with pip (source flask\bin\activate;pip install -r requirements.txt)

3) install pygame into the flask folder

4) init the DB

dbcontrol.py db init

dbcontrol.py db migrate

dbcontrol.py db upgrade
