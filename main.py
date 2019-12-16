# ���JLineBot�һݭn���M��
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import mongodb
import re
import time
import schedule
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import linenotify


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('')
# Channel Secret
handler = WebhookHandler('')
# Your User Id
line_bot_api.push_message('', TextSendMessage(text='�A�i�H�}�l�F'))

# �קאּ�A���v�����e
token = ''
startmsg = '�ѻ��_�l����ɶ�:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
linenotify.lineNotifyMessage(token, msg=startmsg)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# �T���ǻ��϶�
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id  
    usespeak = str(event.message.text)  
    if re.match('[0-9]{4}[<>][0-9]', usespeak):   
        mongodb.write_user_stock_fountion(stock=usespeak[0:4], bs=usespeak[4:5], price=usespeak[5:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak[0:4] + '�w�g�x�s���\'))
        return 0
    elif re.match('�R��[0-9]{4}', usespeak):   
        mongodb.delete_user_stock_fountion(stock=usespeak[2:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak + '�w�g�R�����\'))
        return 0

def job():
    #����ɶ����աA�T�{�ɶ����b����  �Y�Q�T�{�O�_���]�Ƶ{    ���}�H�U���O
    #linenotify.lineNotifyMessage(token, msg='����ɶ�:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data = mongodb.show_user_stock_fountion()
    for i in data:
        stock = i['stock']
        bs = i['bs']
        price = i['price']
        url = 'https://tw.stock.yahoo.com/q/q?s=' + stock
        list_req = requests.get(url)
        soup = BeautifulSoup(list_req.content, "html.parser")
        getstock = soup.findAll('b')[1].text  # �̭��Ҧ���r���e
        if float(getstock):
            if bs == '<':
                if float(getstock) < price:
                    get = stock + '(�i�R�i)������G' + getstock
                    linenotify.lineNotifyMessage(token, get)

            else:
                if float(getstock) > price:
                    get = stock + '(�i��X)������G' + getstock
                    linenotify.lineNotifyMessage(token, get)
        else:
            linenotify.lineNotifyMessage(token, msg='��������D���`')


# �P�_�@�줭  �x�Ѷ}��ɶ��d��ɶ� �}��ɶ����W�E�I-�U�Ȥ@�I�b
start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:00', '%Y-%m-%d%H:%M')
end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '13:30', '%Y-%m-%d%H:%M')
now_time = datetime.datetime.now()
weekday = datetime.datetime.now().weekday()
if weekday >= 0 and weekday <= 4:
    if now_time > start_time and now_time < end_time:
        second_5_j = schedule.every(10).seconds.do(job)

# �L�a�j��
while True:
    schedule.run_pending()
    time.sleep(1)
# �D�{��
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

