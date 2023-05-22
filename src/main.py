import dotenv
from os import environ as env
print("Load Actual libs")

from Bot_Stuff import Bot
dowelcomemsgs = True

dotenv.load_dotenv()
print("Load Dotenv")

c = Bot.Bot(env["BOT_USERNAME"],env["BOT_PASSWORD"],prefix=f"@{env['BOT_USERNAME']}",debug=True,tb=False,testmode=False)
print("Load Client")
 
@c.command
def ping(ctx):
    ctx.reply("Pong! Latency (Bit inaccurate sometimes): "+c.bot.wss.latency+" Seconds")

@c.command
def baller(ctx):
    ctx.reply("DID SOMEONE SAY [BALLER: https://media.tenor.com/vR1roTDEUPcAAAAC/roblox-baller.gif]")

@c.login
def onlogin():
    print("login")

print("Start Client")
c.start()
