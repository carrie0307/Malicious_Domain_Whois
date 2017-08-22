# coding:utf-8
from __future__ import division
from bs4 import BeautifulSoup
from time import sleep
import urllib2
import threading
import Queue
import jieba.analyse
import word
import fenci
import socket
socket.setdefaulttimeout(6) 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


lottery_words = open('../fenci/fenci_res/words/赌博words.txt', 'r').readlines()
sexy_words = open('../fenci/fenci_res/words/色情words.txt', 'r').readlines()
words_list = [lottery_words, sexy_words]

domain_q = Queue.Queue()
content_q = Queue.Queue()
res_q = Queue.Queue()


def select_domain():
    global domain_q
    file = open('temp', 'r')
    lines = file.readlines()
    file.close()
    lines = list(set(lines))
    for line in lines:
        domain_q.put(line.strip())
    print "domains got !\n"


def download_htmlpage(domain):
    url = 'http://' + domain
    # print url
    try:
        res = urllib2.urlopen(url)
        html = res.read()
        soup = BeautifulSoup(html, 'lxml')
        content = word.pre_deal(str(soup))
        if content == '':
            return ['-8', domain, False]
        return [content, domain, True]
    except Exception, e:
        message = str(e)
        if message == '<urlopen error [Errno -5] No address associated with hostname>':
            # print '域名无关联地址 ...'
            content = '-1'
        elif message == '<urlopen error [Errno 22] Invalid argument>':
            # print '域名错误 ... '
            content = '-2'
        elif message == '<urlopen error timed out>':
           #  print '请求超时 ...'
            content = '-3'
        elif message == 'HTTP Error 400: Bad Request':
            # print 'HTTP 400错误 ...'
            content = '-4'
        elif message == 'HTTP Error 502: Bad Gateway':
            # print 'HTTP 502错误 ...'
            content = '-5'
        elif message == 'timed out':
           #  print '请求超时 ...'
            content = '-3'
        elif message == '<urlopen error [Errno -3] Temporary failure in name resolution>':
            # print 'Wrong ...'
            content = '-6'
        else:
            content = '-7'
        return [content, domain, False]


def judge_type(content, domain, flag):
    res = []
    global res_q
    if flag == True:
        state = '1'
        keywords = jieba.analyse.extract_tags(content, topK=5)
        keywords = str(','.join(keywords))
        length = len(fenci.cut_string(content))
        for i in range(len(words_list)):
            words = words_list[i]
            num = 0
            count = 0
            theme_words = []
            for item in words:
                item = item.strip()
                if item in content:
                    theme_words.append(item)
                    num = num + content.count(item)
                    count = count + 1
            rate = num / length
            themewords = ','.join(theme_words)
            res.append((count, rate, themewords))
        # 赌博 0/色情 1, res[][0]: count, res[][1]: rate, res[][2]: themewords
        if res[0][0] > res[1][0]:
            area = '赌博'
            count = res[0][0]
            rate = res[0][1]
        else:
            area = '色情'
            count = res[1][0]
            rate = res[1][1]
        if count > 4 or rate > 0.1:
            print domain + '\t' + area
            res_q.put([domain, area])
    else:
        state = content
        keywords = '--'
        themewords = '--'
        grade = 0
        area = '--'
        return [domain, state, keywords, themewords, grade, area]


def html_downloader():
    global domain_q
    global contet_q
    while True:
        try:
            domain = domain_q.get(timeout=300)
            content, domain, flag = download_htmlpage(domain)
            content_q.put([content, domain, flag])
        except Queue.Empty:
            return


def deal_with_html():
    global content_q
    while True:
        try:
            content, domain, flag = content_q.get(timeout=100)
            judge_type(content, domain, flag)
           #  res_q.put([domain, state, keywords, themewords, grade, area])
        except Queue.Empty:
            return




if __name__ == '__main__':
    select_domain()
    download_td = []
    deal_td = []
    for _ in range(10):
        download_td.append(threading.Thread(target=html_downloader))
    for td in download_td:
        td.start()

    for _ in range(2):
        deal_td.append(threading.Thread(target=deal_with_html))
    for td in deal_td:
        td.start()
    for td in deal_td:
        td.join()
    string = ''
    while not res_q.empty():
        domain, area = res_q.get()
        string = string + domain + '\t' + area + '\n'
    w_file = open('judge_res.txt', 'w')
    w_file.write(string)
    w_file.close()
