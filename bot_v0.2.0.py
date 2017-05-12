#coding=utf8
import requests
import json, re
import itchat
from itchat.content import *

'''
0.2.0版本
功能：
6.群聊成员入群提醒
5.群聊被@时智能回复
4.匹配群聊关键字 搜 ，调用bing搜素API
3.自动接受加好友请求
2.私聊智能回复
1.匹配群聊关键字 说 ，然后回复接受到的消息
'''

bing_url = 'https://api.cognitive.microsoft.com/bing/v5.0/search'
KEY = '8edce3ce905a4c1dbb965e6b35c3834d'

# 图灵机器人
def get_tuling_res(msg):
    # 构造了要发送给服务器的数据
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
        return r.get('text')
    # 防止服务器无响应导致程序异常，用try-except捕获
    except:
        return u'我不和你私聊！'

# 自动接受加好友
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg(u'很高兴认识你！', msg['RecommendInfo']['UserName'])

# 智能私聊
@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    defaultReply = u'我不和你私聊！'
    reply = get_tuling_res(msg['Text'])
    nick_name = msg['FromUserName']
    user_info = itchat.search_friends(userName=nick_name)
    if user_info:
        nick_name = user_info[u'NickName']
    print('%s:%s'%(nick_name,msg['Text']))
    return reply or defaultReply

# 入群提醒
@itchat.msg_register(NOTE, isGroupChat=True)
def group_join_note(msg):
    if u'邀请' in msg['Content'] or u'invited' in msg['Content']:
        str = msg['Content'];
        pos_start = str.find('"')
        pos_end = str.find('"',pos_start+1)
        inviter = str[pos_start+1:pos_end]
        rpos_start = str.rfind('"')
        rpos_end = str.rfind('"',0, rpos_start)
        invitee = str[(rpos_end+1) : rpos_start]
        itchat.send_msg(u"@%s 欢迎来到本群[微笑]，感谢%s邀请。\r\n在本群发送【说+想说的话】即可重复你说的话" % (invitee,inviter), msg['FromUserName'])

# 群聊监控
@itchat.msg_register(TEXT, isGroupChat = True)
def groupchat_reply(msg):
    room_name = itchat.search_chatrooms(userName=msg[u'FromUserName'])
    print(u"来自-%s-群聊消息|%s:%s"%(room_name[ u'NickName'],msg['ActualNickName'],msg['Text']))

    # 群聊中被@时回复
    if msg['isAt']:
            itchat.send(get_tuling_res(msg['Text']), msg[u'FromUserName'])

    # 匹配说关键字
    if(re.match(u'^说', msg['Text'])):
        itchat.send_msg(msg['Text'].replace(u'说', ''),msg[u'FromUserName'])
    # 匹配bing搜素
    elif(re.match(u'^搜', msg['Text'])):
        headers = {'Ocp-Apim-Subscription-Key': '1fbc3fc588734cf68715f530235a8abf'}
        payload = {'q': msg['Text'].replace(u'搜', ''), 'count': 3, 'offset':0, 'mkt':'zh-CN'}
        r = requests.get(bing_url,headers=headers,params=payload)
        #print(r.url)
        if(r.status_code == 200):
            #print(r.text)
            #res_str = r.json()['webPages']['value']
            res_dic = json.loads(r.text)
            res_str = ''
            for i in res_dic['webPages']['value']:
                #print(i['name'])
                res_str = res_str + i['name'] + i['url'] + "\r\n"

            itchat.send_msg(res_str, msg[u'FromUserName'])
        else:
            itchat.send_msg(u'没找到哦～',msg[u'FromUserName'])

itchat.auto_login(hotReload=True,enableCmdQR=True)

itchat.run(debug=True)
