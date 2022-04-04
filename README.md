# gabe

*Remastered* version of my original Discord bot, dodo. I might change the name of this if it gets to a point where I'm happy with it.


# How to run locally


# How to run on Heroku


# Explanation of Parts
Procfile - Sync with Heroku. `gabe.py` is the main "chatbot" file that launches the modules
    
    worker: python3 gabe.py

runetime.txt - Heroku will automatically assign a Python runtime if not specified. Adding this is optional and locks the instance at that version

    python-3.9.5

requirements.txt - Helpful Python file to install all dependencies via:

    $ pip install -r requirements.txt
