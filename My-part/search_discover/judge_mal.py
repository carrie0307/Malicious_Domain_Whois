# coding:utf-8
'''
	功能：
		malicious_link 表中 type 的判别 （ 0 未判断 1 赌博 2 色情 9 类型未知）

'''
from bs4 import BeautifulSoup
from time import sleep
import urllib2
import MySQLdb
import threading
import Queue
import jieba.analyse
import re
from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import socket
socket.setdefaulttimeout(10)


lottery_words = open('../search_discover/赌博words.txt', 'r').readlines()
sexy_words = open('../search_discover/色情words.txt', 'r').readlines()
words_list = [lottery_words, sexy_words]
stop_list = ['的', '或', '是', '啦', '去' ,'也', '只', '而']

url_q = Queue.Queue()
res_q = Queue.Queue()
content_q = Queue.Queue()
get_url_list = []
thread_num = 5


def get_urls():
	global url_q
	conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'keywords', charset = 'utf8')
	cur = conn.cursor()
	# SQL = "SELECT domain, malicious_info.title FROM malicious_info, domain_index WHERE malicious_info.ID = domain_index.ID AND flag LIKE %s;" %flag
	SQL = "SELECT url FROM SE_search WHERE type='0' LIMIT 5;"
	cur.execute(SQL)
	result = cur.fetchall()
	for item in result:
		url_q.put(item[0])
	print 'get domains ...'


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


def download_htmlpage():
	global url_q
	global content_q
	while True:
		if url_q.empty():
			break
		url = url_q.get()
		try:
			resp = urllib2.urlopen(url)
			html = resp.read()
			soup = BeautifulSoup(html, 'lxml')
		except Exception, e:
			continue
		content = pre_deal(str(soup))
		content_q.put([url, content])


def get_final_url(url):
	global url_q
	global get_url_list
	# 所有重新请求的url都先加入get_url_list, 以后每个都先比对，如果已经重取过一次，则不再重取
	if url in get_url_list:
		res_q.put([url, '9'])
		# 对应未分出类的i两种情况（content 为空或 未分出类别）
	else:
		# 所有重新请求的url都先加入get_url_list, 以后每个都先比对，如果已经重取过一次，则不再重取
		get_url_list.append(url)
		get_final_url(url)
	try:
		with Display(backend="xvfb", size=(1440, 900)):
			driver = webdriver.Chrome()
			driver.maximize_window()
			driver.get(url)
			url = driver.current_url
			driver.quit()
			url_q.put(url)
	except:
		print 'get_url wrong ...'


def judge_url_type():
	global content_q
	global res_q
	global get_url_list
	while True:
		url, content = content_q.get(timeout=15)
		if content == '':
			res_q.put([url, '7'])
			get_final_url(url)
			continue 
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
		else:
			if url in get_url_list:
				res_q.put([url, '9'])
			else:
				# 未分出类可能是因为存在重定向，再get_url
				res_q.put([url, '7'])
				# 假设aaa.com通过get_url得到bbb.com,之后的处理和存储是针对bbb.com的，因此则需要对aaa.com标记，在库中标志存为7
				get_final_url(url)


conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'keywords', charset= 'utf8')
cur = conn.cursor()
def save_result():
	global conn, cur
	global res_q
	while True:
		try:
			url, ttype = res_q.get(timeout=15)
			print url, ttype
		except Queue.Empty:
			break
		# SQL = "UPDATE SE_search SET type = '" + ttype + "' WHERE url = '" + url + "';"
		SQL = "REPLACE INTO SE_search (url, type) VALUES('" + url + "', '" + ttype + "');"
		cur.execute(SQL)
		conn.commit()
		print 'upset successfullly ...'
	cur.close()
	conn.close()
	print 'saved over ...'


if __name__ == '__main__':
	get_urls()
	get_html_td = []
	for _ in range(thread_num):
		get_html_td.append(threading.Thread(target=download_htmlpage))
	for td in get_html_td:
		td.start()
	sleep(10)
	judge_type_td = threading.Thread(target=judge_url_type)
	judge_type_td.start()
	SQLdb_td = threading.Thread(target=save_result)
	SQLdb_td.start()
	SQLdb_td.join()