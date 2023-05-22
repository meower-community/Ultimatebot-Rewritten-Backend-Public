import traceback

#this holds the ctx and well, discord support

supportDiscord = ["Discord","Webhooks","Revower","revolt"]

class ctx:
    def __init__(self,auser,apost,aargs,acmd_prefix,acmd,adiscord,aclient,apo):
        self.user = auser
        self.post = apost

        if aargs == []:
            self.args = [None] * 20
        else: 
            for i in range(20):   
                aargs.append(None)
            self.args = aargs

        self.cmd_prefix = acmd_prefix
        self.cmd = acmd
        self.discord = adiscord
        self.client = aclient
        self.post_origin = apo

        def reply(msg):
            aclient.post("@" + self.user + " " + msg,to=apo)

        def post(msg):
            aclient.post(msg,to=apo)
            
        self.sendpost = post
        self.reply = reply

def support(msg, c, pf):
    try:
        if msg["u"] in supportDiscord:
            post = msg["p"].split(": ")
            user = post[0]
            post = " ".join(post[1:])
            if post.split(" ")[0] == pf:
                return ctx(
                    user,
                    post,
                    post.split(" ")[2:],
                    pf,
                    post.split(" ")[1],
                    True,
                    c,
                    msg["post_origin"]
                )
        else:
            if msg["p"].split(" ")[0] == pf:
                return ctx(
                    msg["u"],
                    msg["p"],
                    msg["p"].split(" ")[2:],
                    pf,
                    msg["p"].split(" ")[1],
                    False,
                    c,
                    msg["post_origin"]
                )
        return ctx
    except:
        print(traceback.format_exc())