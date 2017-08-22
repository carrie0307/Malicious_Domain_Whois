# coding:utf-8
'''
	功能：
		malicious_link 表中 type 的判别 （ 0 未判断 1 赌博 2 色情 9 类型未知）

	说明：
		每100条commit一次
		2018.08.18
'''
from bs4 import BeautifulSoup
from time import sleep
import urllib2
import MySQLdb
import threading
import Queue
import chardet
import jieba.analyse
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import socket
socket.setdefaulttimeout(5)


lottery_words = open('../malicious_link/赌博words.txt', 'r').readlines()
sexy_words = open('../malicious_link/色情words.txt', 'r').readlines()
words_list = [lottery_words, sexy_words]
stop_list = ['的', '或', '是', '啦', '去' ,'也', '只', '而']

url_q = Queue.Queue()
content_q = Queue.Queue()
res_q = Queue.Queue()
thread_num = 10
counter = 0


def get_urls(conn, cur):
	global url_q
	SQL = "select url from malicious_link where type = '0';"
	cur.execute(SQL)
	result = cur.fetchall()
	print result
	for item in result:
		url_q.put(item[0])
	print "urls got !\n"


# 提前中文内容,过滤字母特殊符号
def pre_deal(string):
	string = re.sub("[\A-Za-z0-9_\s+\.\!\/_,$%^*(+\"\']".decode("utf8"), "".decode("utf8"),string)
	string = re.sub("[+——！，。？、~@#￥%……&*（）：“”;【】?―:　-]".decode("utf8"), "".decode("utf8"),string)
	string = re.sub("[\{\}<>=)«|\[\]  ]".decode("utf8"), "".decode("utf8"),string)
	return string


def cut_string(string):
	global stop_list
	words = []
	seg_list = jieba.cut(string, cut_all=False)
	temp = ",".join(seg_list)
	temp = temp.split(',')
	for i in temp:
		if i not in stop_list:
			words.append(i)
	return words


# urllib2获取响应可能存在压缩包问题，在此处理；同时处理编码问题
def pre_deal_html(req):
	info = req.info()
	content = req.read()
	encoding = info.getheader('Content-Encoding')
	if encoding == 'gzip':
		buf = StringIO(content)
		gf = gzip.GzipFile(fileobj=buf)
		content = gf.read()
	charset = chardet.detect(content)['encoding']
	if charset != 'utf-8' and charset != None:
		content = content.decode(charset, 'ignore')
	return content


def download_htmlpage():
	global url_q
	global content_q
	while True:
		if url_q.empty():
			print 'url全部跑完。。。'
			break
		url = url_q.get()
		try:
			resp = urllib2.urlopen(url)
			html = pre_deal_html(resp)
		except Exception, e:
			print url + " 未能取回网页。。。\n"
			res_q.put([url, '8'])
			print 'put \n'
			continue
		try:
			soup = BeautifulSoup(html, 'lxml')
			content = pre_deal(str(soup))
			content_q.put([url, content])
			print url + ' 获取到内容。。。\n'
		except:
			res_q.put([url, '8'])
			print 'put \n'
			print url + ' pre_deal 出现问题\n'
	print 'download over ...'


def judge_url_type():
	print 'judging ...'
	global content_q
	global res_q
	while True:
		try:
			url, content = content_q.get(timeout=500)
		except Queue.Empty:
			print '内容队列空。。。'
			break
		if content == '':
			res_q.put([url, '9'])
		temp = []
		length = len(cut_string(content))
		for i in range(len(words_list)):
			words = words_list[i]
			num = 0
			count = 0
			for item in words:
				item = item.strip()
				if item in content:
					num = num + content.count(item)
					count = count + 1
			rate = num / length
			temp.append((count, rate))
		if temp[0][0] > temp[1][0]:
			ttype = '1'
			count = temp[0][0]
			rate = temp[0][1]
		else:
			ttype = '2'
			count = temp[1][0]
			rate = temp[1][1]
		if count > 4 or rate > 0.1:
			res_q.put([url, ttype])
			print 'put \n'
			# ttype含义： 1--赌博，2--色情，8--请求错误， 9--类型未知
		else:
			res_q.put([url, '9'])
			print 'put \n'
	print 'judge over ...'


def save_result(conn, cur):
	# global conn, cur
	global res_q
	global counter
	while True:
		try:
			url, ttype = res_q.get(timeout=200)
			print "res:   " + url + "   " + ttype + '\n'
		except Queue.Empty:
			print '结果队列为空。。。'
			break
		SQL = "UPDATE malicious_link SET type =  '" + ttype + "' WHERE url = '%s'" %url
		cur.execute(SQL)
		print "counter : " + str(counter) + '\n'
		counter = counter + 1
		if counter == 100:
			conn.commit()
			print 'upset successfullly ...'
			counter = 0
	conn.commit()
	cur.close()
	conn.close()
	print 'saved over ...'


if __name__ == '__main__':
	conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'malicious_domain_sys', charset = 'utf8')
	cur = conn.cursor()
	get_urls(conn, cur)
	get_html_td = []
	for _ in range(thread_num):
	 	get_html_td.append(threading.Thread(target=download_htmlpage))
 	for td in get_html_td:
		td.start()
	print 'running ...'
	sleep(10)
	judge_type_td = threading.Thread(target=judge_url_type)
	judge_type_td.setDaemon(True)
	judge_type_td.start()
	sleep(10)
	print 'saving ...'
	SQLdb_td = threading.Thread(target=save_result, args=(conn, cur))
	SQLdb_td.start()
	SQLdb_td.join()
