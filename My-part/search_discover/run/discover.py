# -*- coding: UTF-8 -*-
import Queue
import requests
import urllib2
from time import sleep
from log import *
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


def Baidu_get_raw_html(wd, title):
	urls = []
	exact_wd = '"' + wd + '"'
	for wd in [exact_wd, title]:
		print wd
		if wd == '':
			continue
		sleep(1)
		for page in range(0, 200, 10):
			payload = {'wd': wd, 'pn': str(page)}
			for i in range(10):
				try:
					html = requests.get('https://www.baidu.com/baidu', params=payload, headers=headers, timeout=5).text
					break
				except:
					if i == 9:
						logger.info(wd)
					else:
						sleep(0.5)
			urls = urls + re.compile(r'<a target="_blank" href=".+?" class="c-showurl" style=".*?">([^>]+?)\/&nbsp;</a>').findall(html)
	urls = list(set(urls))
	print len(urls)
	print 'Baidu--------------------'
	return urls


def Bing_get_raw_html(wd, title):
	urls = []
	exact_wd = '"' + wd + '"'
	for wd in [exact_wd, title]:
		sleep(1)
		if wd == '':
			continue
		for page in range(0, 200, 10):
			payload = {'q': wd, 'go': 'Submit', 'first': str(page)}
			for i in range(10):
				try:
					html = requests.get('http://cn.bing.com/search', params=payload, headers=headers, timeout=5).text
					break
				except:
					if i == 9:
						logger.info(wd)
					sleep(0.5)
			urls = urls + re.compile(r'<li class="b_algo"><h2><a target="_blank" href="http://(.+?)" h=".+?"').findall(html)
	urls = list(set(urls))
	print 'Bing--------------------'
	return urls


if __name__ == '__main__':
	# get_domains(1)
	title = '澳门玫瑰国际娱乐城老品牌值得您信赖亚洲最具公信力第一品牌'
	domain = '433444.com'
	Baidu_get_raw_html(domain, title)
	# Bing_get_raw_html(domain, title)
