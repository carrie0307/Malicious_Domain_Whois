# coding:utf-8
'''
	功能：
		填充 malicious_info 表中 malicious_link 内容以及 malicious_link 表中内容

		2017.08.18

	最终运行
'''
from bs4 import BeautifulSoup
from time import sleep
from tld import get_tld
from log import *
import urllib2
import MySQLdb
from timeout import timeout
import chardet
import threading
import socket
socket.setdefaulttimeout(5)
import Queue
import db_operation
from time import sleep
from log import *


white_list = db_operation.white_list
black_list = db_operation.black_list  # 关于黑名单的问题是，如果日后黑名单量较大，在黑名单中比对效率问题
domain_q = db_operation.domain_q
soup_q = Queue.Queue()
res_q = Queue.Queue()
thread_num = 15


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


def get_html():
	global url_q
	global soup_q
	while True:
		if domain_q.empty():
			break
		domain = domain_q.get()
		url = 'http://' + domain
		try:
			print domain + "   trying ..."
			resp = urllib2.urlopen(url)
			html = pre_deal_html(resp)
		except Exception, e:
			res_q.put([domain, []])
			continue
		try:
			soup = BeautifulSoup(html, 'lxml')
			soup_q.put([domain, soup])
		except:
			pass
	print 'download over ...'


def judge_a_links():
	global white_list
	global balck_list
	global soup_q
	global res_q
	while True:
		try:
			domain, soup = soup_q.get(timeout=600)
		except Queue.Empty:
			break
		mal_urls = []
		for a in soup.find_all('a'):
			try:
				url = a['href']
				url_domain = get_tld(url)
				if url_domain != domain:  # 获取除本网站站内连接之外的链接
					if url_domain in black_list or url_domain not in white_list:
					# 目前先将不在白名单中域名url都放入malicious_link表内，待以后malicious_link表足够完全后，再只用黑名单
						mal_urls.append((url, url_domain))
			except Exception, e:
				# logger.info(domain + '   GET LINKS WRONG ...')
				continue
		res_q.put([domain, mal_urls])
	print 'links over ...'



def save_db(conn, cur):
	print 'saving ...'
	global res_q
	# global conn, cur
	global counter
	while True:
		try:
			domain, mal_urls = res_q.get(timeout=150)
			print 'get ' + domain, mal_urls
		except Queue.Empty:
			break
		if mal_urls != []:
			string = ''
			for item in mal_urls:
				try:
					SQL_malicious_links = "REPLACE INTO malicious_link(url_id, url, url_domain) VALUES('" + str(hash(item[0])) + "', '" + item[0] + "' , '" + item[1] + "')"
					cur.execute(SQL_malicious_links)
					string = string + str(hash(item[0])) + ','
				except:
					print 'error---'
					print SQL_malicious_links
					continue
			string = string[:len(string) - 1]
			try:
				SQL = "UPDATE malicious_info SET malicious_link =  '" + string + "' WHERE ID = %s" %hash(str(domain))
				cur.execute(SQL)
				SQL = "UPDATE malicious_info SET flag =  flag + 10 WHERE ID = %s" %hash(str(domain))
				cur.execute(SQL)
				conn.commit()
				print domain + '  saved successfully ...\n'
			except:
				print 'error--'
				print SQL
		else:  # 初始提取链接为空的情况
			try:
				SQL = "UPDATE malicious_info SET malicious_link =  '' WHERE ID = %s" %hash(str(domain))
				cur.execute(SQL)
				SQL = "UPDATE malicious_info SET flag =  flag + 20 WHERE ID = %s" %hash(str(domain))
				cur.execute(SQL)
				conn.commit()
				print domain + '  saved successfully ...\n'
			except:
				print 'error'
				print SQL
	cur.close()
	conn.close()
	print 'db over ...'


def run():
	global white_list
	global balck_list
	global domain_q
	while True:
		get_html_td = []
		for _ in range(thread_num):
			get_html_td.append(threading.Thread(target=get_html))
		for td in get_html_td:
			td.start()
		sleep(10)
		judge_td = threading.Thread(target=judge_a_links)
		judge_td.setDaemon(True)
		judge_td.start()
		conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'malicious_domain_sys', charset = 'utf8')
		cur = conn.cursor()
		SQLdb_td = threading.Thread(target=save_db, args=(conn, cur))
		SQLdb_td.start()
		SQLdb_td.join() # 以上完成一次的运行
		print 'run over and sleeping ...'
		sleep(600)
		print 'running again ...'
		white_list = db_operation.white_list # 下一轮运行之前，重新获取香港队列和列表中内容
		black_list = db_operation.black_list  # 关于黑名单的问题是，如果日后黑名单量较大，在黑名单中比对效率问题
		domain_q = db_operation.domain_q





if __name__ == '__main__':
	# run()
	get_html_td = []
	for _ in range(thread_num):
		get_html_td.append(threading.Thread(target=get_html))
	for td in get_html_td:
		td.start()
	sleep(10)
	judge_td = threading.Thread(target=judge_a_links)
	judge_td.start()
	conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'malicious_domain_sys', charset = 'utf8')
	cur = conn.cursor()
	SQLdb_td = threading.Thread(target=save_db, args=(conn, cur))
	SQLdb_td.start()
	SQLdb_td.join() # 以上完成一次的运行
