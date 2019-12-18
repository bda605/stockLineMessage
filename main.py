from __future__ import print_function
import time
import schedule
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import mongodb
import linenotify

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code


# �קאּ�A���v�����e
token = ''
startmsg = '�ѻ��_�l����ɶ�:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
linenotify.lineNotifyMessage(token, msg=startmsg)


def job():
    # ����ɶ����աA�T�{�ɶ����b����  �Y�Q�T�{�O�_���]�Ƶ{    ���}�H�U���O
    # linenotify.lineNotifyMessage(token, msg='����ɶ�:' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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