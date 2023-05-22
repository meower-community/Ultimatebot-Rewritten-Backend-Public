import threading
from Bot_Stuff import Client
from Bot_Stuff.setupm import setupmethod
from Bot_Stuff import discord_support

#TODO: idk, listener support for client and other client based stuff fijsdlfkj

class Bot:
  def __init__(self,user,psw,prefix="!",debug=False,server="wss://server.meower.org/",tb=False,testmode=True):
    self.user = user
    self.psw = psw

    self.testmode = testmode

    self.cmdsran = 0

    self.whitelisted = ["ping","baller"]

    self.bot = Client.client(user,psw,tb,debug,server)
    self.prefix = prefix
    self.VER = "1.7"

    self.bot.callback(self.onpost,"on_post")
    self.bot.callback(self.onlogin,"on_login")
    self.bot.callback(self.onmsg,"on_raw_msg")

    self.cmd_funcs = {}
    self.logincb = None
    self.msgcb = None

  def send_raw_packet(self,msg):
    self.bot.send_msg(msg)

  def post(self, msg):
    self.bot.post(msg)
  
  def onlogin(self):
    if not self.logincb == None:
      self.logincb[0]()

  def onmsg(self,msg):
    if not self.msgcb == None:
      self.msgcb[0](msg)
  
  def onpost(self, msg):
    ctx = discord_support.support(msg, self.bot, self.prefix)

    try:
      print(ctx.cmd)
    except:
      return
      
    if msg["u"] == "Webhooks":
      self.bot.post("Due to security reasons, the bot doesnt support webhooks", to=msg["post_origin"])
      return
    
    if msg["u"] == "AddiNoir" or msg["u"] == "AdddiNoir":
      ctx.reply("Is a Jerk")
      return

    if not ctx.cmd in self.whitelisted:
      if msg["post_origin"] == "home":
        ctx.reply("You cannot use this command in home.")
        return
    
    if ctx.cmd in self.cmd_funcs:
      self.cmdsran += 1
      print("New thread: CommandProcessThread_"+ctx.user+"_"+ctx.cmd+"_"+str(self.cmdsran))
      t = threading.Thread(target=self.cmd_funcs[ctx.cmd],args=(ctx,),name="CommandProcessThread_"+ctx.user+"_"+ctx.cmd+"_"+str(self.cmdsran))
      t.start()

  @setupmethod  
  def command(self, rule):
    self.cmd_funcs.update({rule.__name__:rule})

  @setupmethod
  def login(self, rule):
    self.logincb = [rule]

  @setupmethod
  def on_message(self, rule):
    self.msgcb = [rule]

  def start(self):
    self.bot.run()