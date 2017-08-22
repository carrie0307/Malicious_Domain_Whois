# -*- coding: UTF-8 -*-
import MySQLdb
import Queue
import requests
import urllib
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


domain_title_q = Queue.Queue()

sites = ['bbs.', 'zhidao.baidu', 'weibo.com']

headers = {"Accept": "text/html;",
	            "Accept-Language": "zh-CN,zh;q=0.8",
	            "Referer": "http://www.baidu.com/",
	            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
	            }


def get_domains(flag):
	global domain_title_q
	flag = "'%" + str(flag) + "'"
	global keywors_q
	conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'malicious_domain_sys', charset = 'utf8')
	cur = conn.cursor()
	SQL = "SELECT domain, malicious_info.title FROM malicious_info, domain_index WHERE malicious_info.ID = domain_index.ID AND flag LIKE %s;" %flag
	cur.execute(SQL)
	result = cur.fetchall()
	for item in result:
		print item[0], item[1]
		# domain_title_q.put([item[0], item[1]])



def Baidu_get_raw_html(wd, title):
	urls = []
	exact_wd = '"' + wd + '"'
	# for wd in [exact_wd, title]:
	for wd in [exact_wd]:
		if wd == '':
			continue
		for page in range(0, 200, 10):
			# payload = {'wd': urllib.quote(wd), 'pn': str(page)}
			payload = {'wd': wd, 'pn': str(page)}
			html = requests.get('https://www.baidu.com/baidu', params=payload, headers=headers, timeout=5).text
			urls = urls + re.compile(r'<a target="_blank" href=".+?" class="c-showurl" style=".*?">([^>]+?)\/&nbsp;</a>').findall(html)
			print urls
	urls = list(set(urls))
	print len(urls)
	# print urls


def Bing_get_raw_html(wd, title):
	urls = []
	exact_wd = '"' + wd + '"'
	for wd in [exact_wd, title]:
		if wd == '':
			continue
		for page in range(0, 200, 10):
			payload = {'q': wd, 'go': 'Submit', 'first': str(page)}
			html = requests.get('http://cn.bing.com/search', params=payload, headers=headers, timeout=5).text
			urls = urls + re.compile(r'<li class="b_algo"><h2><a target="_blank" href="http://(.+?)" h=".+?"').findall(html)
	urls = list(set(urls))


if __name__ == '__main__':
	# get_domains(1)
	title = '澳门玫瑰国际娱乐城老品牌值得您信赖亚洲最具公信力第一品牌'
	domain = '433444.com'
	Baidu_get_raw_html(domain, title)
	# Bing_get_raw_html(domain, title)
