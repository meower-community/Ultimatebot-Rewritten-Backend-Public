import json
import threading
import time
import websocket
import sys

# Takes websocket app and creates internal callbacks
# Bare bones, only to make load easier
# Basically just cl but only the websocket wrapper part

debugmode_G = False

# A printing function that will print a message ONLY if debugging is enabled
def debugprint(msg):
    global debugmode_G
    if debugmode_G:
        print("DEBUG:" + str(msg))

class Wrapper:

    # Initalize websocket with callbacks
    def __init__(self,server,callbacks,tb,debug=False,autore=False):
        global debugmode_G
        self.callbacks = callbacks
        self.VER = "1.2"
        self.latency = "Not recorded yet"
        self.pingwaitunix = 0
        self.server = server
        debugmode_G = debug
        self.autore = autore
        if tb:
            websocket.enableTrace(True)
        self.disconnect = False
        self.packetqueue = []
        self.wsapp = websocket.WebSocketApp(server,on_open=self.on_open,on_error=self.onerror,on_message=self.on_message,on_close=self.on_close)

    # Called from client, runs websocket
    def run(self):
        wst = threading.Thread(target=self.wsapp.run_forever)
        wst.start()
        ping = threading.Thread(target=self.ping)
        ping.start()

    def ping(self):
        time.sleep(10)
        while True:
            debugprint("Ping server")
            self.pingwaitunix = time.time()
            if not self.disconnect:
                try:
                    self.wsapp.send(json.dumps({"cmd": "ping", "val":""}))
                except Exception as e:
                    debugprint("Ping had error")
            time.sleep(10)

    # Called from client, sends a packet to the server.
    def send(self,msg):
        ex = ["{'cmd': 'direct', 'val': {'cmd': 'set_chat_state', 'val': {'chatid': 'livechat', 'state': 101}}, 'listener': 'typing_indicator'}"]
        if not msg in ex:
            debugprint("Sending: "+str(msg))

        if not self.disconnect:
            self.wsapp.send(json.dumps(msg))
        else:
            self.packetqueue.append(json.dumps(msg))

    # Connection callback binding.
    def on_open(self,wsapp):
        self.callbacks["on_open"]()

    def close(self):
        self.wsapp.close()

    # Packet callback binding.
    def on_message(self,wsapp,msg):
        if json.loads(msg)["cmd"] == "ping":
            if json.loads(msg)["val"] == "I:100 | OK":
                self.latency = str(f'{time.time() - self.pingwaitunix:3.2f}')
                    
        self.callbacks["on_message"](json.loads(msg))

    def onerror(self, ws, error):
        debugprint(error)

    # Disconnection callback binding.
    def on_close(self,wsapp,a,a2):
        if not self.autore: # If autoreconnect is not enabled, return the function.
            debugprint("Autoreconnect is not enabled")
            return
        
        debugprint("Restarted The bot. Reason (I suppose): "+str(a)+" "+str(a2)) # Debug check
        self.disconnect = True # Make sure to redirect send function
        self.callbacks["on_close"](a,a2) #

        self.wsapp = websocket.WebSocketApp(self.server,on_open=self.on_open,on_error=self.onerror,on_message=self.on_message,on_close=self.on_close)
        self.run()

        self.disconnect = False
        time.sleep(12)

        debugprint(self.packetqueue)

        for i in self.packetqueue:
            self.wsapp.send(i)
            time.sleep(1.5)

        self.packetqueue = []
