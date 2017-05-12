#coding=utf8
import re
import itchat
from itchat.content import *

'''
0.0.1版本
功能：
1.匹配群聊关键字 说 ，然后回复接受到的消息
'''

# 群聊监控
@itchat.msg_register(TEXT, isGroupChat = True)
def groupchat_reply(msg):
    room_name = itchat.search_chatrooms(userName=msg[u'FromUserName'])
    print(u"来自-%s-群聊消息|%s:%s"%(room_name[ u'NickName'],msg['ActualNickName'],msg['Text']))

    # 匹配说关键字
    if(re.match(u'^说', msg['Text'])):
        itchat.send_msg(msg['Text'].replace(u'说', ''),msg[u'FromUserName'])

    if(re.match(u'^搜', msg['Text'])):
        itchat.send_msg(u'电影名xxx',msg[u'FromUserName'])

itchat.auto_login(hotReload=True,enableCmdQR=True)

itchat.run(debug=True)
