import time
import traceback
from Bot_Stuff import ws_wrapper

import requests

def getip():
    ret = requests.get('https://api.meower.org/ip')
    return ret.text

# Does all of the other stuff for the client
# Simple wrapper to make bot dev easier

debugmode_G = False

# A printing function that will print a message ONLY if debugging is enabled
def debugprint(msg):
    global debugmode_G
    if debugmode_G:
        print("DEBUG:" + msg)

class client:
    # Initalize the meower client with a user, password, debug and server
    def __init__(self,user,psw,tb,debug=False,server="wss://server.meower.org/"):
        # Ws wrapper call
        self.wss = ws_wrapper.Wrapper(
            server,
            {
                "on_open":self.on_connect,
                "on_message":self.on_msg,
                "on_close":self.on_disconnect
            },
            tb,
            debug
        )
        self.tb = tb
        # Globalize args
        self.user = user
        self.psw = psw
        self.debug = debug
        self.VER = "1.0.5"
        # Callbacks
        self.cbs = {
            "on_login":None,
            "on_raw_msg":None,
            "on_post":None,
            "on_disconnect":None # Entirely useless (at least right now)
        }
        global debugmode_G
        debugmode_G = self.debug
        self.ip = str(getip()) # Gets IP
        self.listeners = [] # Useless. May become something later on.
        self.authed = False # Check for auth

    # The running function for the client.
    def run(self):
        time.sleep(0.5) # delay for loading purposes
        self.wss.run() # Literally just the call from the ws wrapper
    
    # Callback binding.
    def callback(self, func, cb):
        try:
            self.cbs[cb] = func # Takes function and adds to the cb dict
            debugprint("Binded callback "+cb+".")
        except:
            debugprint("Error while binding callback or callback invaild. Traceback Error:\n"+traceback.format_exc())

    # Posting msgs for group chats and home
    def post(self, msg, to="home"):
        """
            Post to group chat or home

            the client doesnt store the last command message, 
            since thats a bot framework thing.
        """

        if len(msg) > 1999:
            msg = msg[0:1999]

        if to == "home":
            self.wss.send({
                "cmd": "direct",
                "val": {
                    "cmd": "post_home",
                    "val": msg
                },
                "listener": "post_home"
            })
        else:
            self.wss.send({
                "cmd": "direct",
                "val": {
                    "cmd": "post_chat",
                    "val": {
                        "p": msg,
                        "chatid": to
                    }
                },
                "listener": "post_chat"
            })

    # Raw wss send (with some more support)
    def send_msg(self, val, listener=None):
        if not listener == None:
            self.wss.send({
                "cmd": "direct",
                "val": val,
                "listener": listener
            })
            self.listeners.append(listener)
        else:
            self.wss.send({
                "cmd": "direct",
                "val": val
            })

    #Callback Function for Calling Callbacks
    def call_cb(self, cb, arg1=None):
        if not self.cbs[cb] == None:
            if not arg1 == None:
                debugprint("called "+cb+" with arg")
                self.cbs[cb](arg1)
            else:
                debugprint("called "+cb+" without arg")
                self.cbs[cb]()
        else:
            debugprint("The " + cb + " callback Isnt binded.")

        # Not abstraction, more for error checking.

    # Connection CB
    def on_connect(self):
        wss = self.wss

        time.sleep(2)

        wss.send({"cmd": "direct","val":{"cmd": "ip","val": self.ip}})
        time.sleep(1)
        wss.send({"cmd": "direct","val":{"cmd": "type","val": "py"}})
        time.sleep(1)
        wss.send({"cmd": "direct","val": "meower", "listener": "send_tkey"})
        time.sleep(0.8)
        self.wss.send({
                "cmd": "direct",
                "val":
                {
                    "cmd": "authpswd",
                    "val":{
                        "username":self.user,
                        "pswd":self.psw
                    }
                },
                "listener":"auth"
            })
        time.sleep(2)
        self.authed = True
        self.call_cb("on_login")

    """def listen_for_msg(self,msg):
        print(msg)"""      

    # Okay im no longer commenting anything
    def on_msg(self, msg):
        debugprint("FROM CLIENT: " + str(msg))

        """if msg["listener"] == "send_tkey":
            print("got tkey")
            time.sleep(4)"""

        if msg["cmd"] == "pmsg":
            if not msg["val"] == "I:500 | Bot":
                if not msg["val"] == "I: 100 | Bot":
                    self.wss.send({
                        "cmd": "pmsg",
                        "val": "I:500 | Bot",
                        "id": msg["origin"]
                    })

        self.call_cb("on_raw_msg", msg)
            
        if self.authed:
            if "post_origin" in msg["val"].keys():
                if not msg["val"]["u"] == self.user:
                    self.call_cb("on_post", msg["val"])
                # call home post
            #self.listen_for_msg(msg["val"])

        """if msg["val"]["mode"] == "auth":
            debugprint("auth")
            self.authed = True
            self.call_cb("on_login")"""


    def on_disconnect(self,a1,a2):
        pass