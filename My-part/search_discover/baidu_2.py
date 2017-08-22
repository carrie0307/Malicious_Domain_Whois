# -*- coding: UTF-8 -*-
import requests
import re
import time
import MySQLdb
from tld import get_tld
from log import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


headers = {"Accept": "text/html;",
	            "Accept-Language": "zh-CN,zh;q=0.8",
	            "Referer": "http://www.baidu.com/",
	            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
	            }


def save_urls(wd, info_list, source):
	wd = 'Jinguan'
	conn = MySQLdb.connect("172.26.253.3", "root", "platform", "keywords")
	cur = conn.cursor()
	for key in info_list.keys():
		try:
			cur.execute("REPLACE INTO SE(query_wd, url, domain, source) VALUES('" + wd + "', '" + key + "', '" + info_list[key] + "', '" + source + "')")
		except Exception, e:
			print '------------------------------------'
			logger.info(key + '\t' + info_list[key] + '\t' + str(e) + '\n')
	conn.commit()
	cur.close()
	conn.close()
	print "URLs saved succeed!"


def Baidu_get_raw_html(wd, pn):
	urls = []
	page = 0
	for page in range(0, pn, 10):
		payload = {'wd': wd, 'pn': str(page)}
		html = requests.get('https://www.baidu.com/s', params=payload, headers=headers, timeout=5).text
		urls = urls + re.compile(r'<a target="_blank" href=".+?" class="c-showurl" style=".*?">([^>]+?)\/&nbsp;</a>').findall(html)
		time.sleep(3)
	print 'Baidu ' + str(len(urls))
	info_list = get_domains_info(urls)
	save_urls(wd, info_list, 'Baidu')


def Bing_get_raw_html(wd, pn):
	urls = []
	page = 0
	for page in range(0, pn, 10):
		payload = {'q': wd, 'go': 'Submit', 'first': page}
		html = requests.get('http://cn.bing.com/search', params=payload, headers=headers, timeout=5).text
		urls = urls + re.compile(r'<cite>([^>]*?)</cite>').findall(html)
		# print 'Bing Sleeping ... \n'
		time.sleep(3)
	print 'Bing ' + str(len(urls))
	print urls
	info_list = get_domains_info(urls)
	save_urls(wd, info_list, 'Bing')
	# print 'Bing ends ...\n'


def Haoso_get_raw_html(wd, pn):
	urls = []
	page = 0
	for page in range(0, pn, 10):
		payload = {'q': wd, 'pn': str(page)}
		html = requests.get('https://www.so.com/s', params=payload, headers=headers, timeout=5).text
		#info = info + re.compile(r'<a href="[^>]*?" rel="noopener".*?>').findall(html)
		urls = urls + re.compile(r'''<a href="http://www\.so\.com/link\?url=http%3A%2F%2F([^>]+?)&[^>]+?" rel="noopener" data-res='{.+?}'.+?target="_blank">''').findall(html)
		time.sleep(3)
	print 'Haoso ' + str(len(urls))
	info_list = get_domains_info(urls)
	save_urls(wd, info_list, '360Haoso')
	# print 'Haosou ends ...\n'


def get_domains_info(urls):
	info_list = {}
	for item in urls:
		url = 'http://' + item
		url = url.replace('%2F', '/')
		try:
			domain = get_tld(url)
		except:
			# print item
			domain = '--'
		info_list[url] = domain
	return info_list


def get_domains():
	domains = []
	conn = MySQLdb.connect("172.26.253.3", "root", "platform", "keywords")
	cur = conn.cursor()
	# cur.execute("SELECT domain from domain_index where judge_flag != '1' order by id limit 5")
	# cur.execute("SELECT  DISTINCT source_domain FROM a_links WHERE source_domain NOT IN (SELECT query_wd FROM SE)")
	cur.execute("SELECT  DISTINCT domain FROM mal_urls")
	result = list(cur.fetchall())
	for item in result:
		domains.append(item[0])
	print "domains got !\n"
	return domains



if __name__ == '__main__':
	print get_domains()
	wd = 'hao6688'
	pn = 100
	Baidu_get_raw_html('金冠娱乐', pn)
'''
	string = ''
	print str(len(urls)) + '\n'
	for url in urls:
		string = string + 'http://' + url + '\n'
		print url + '\n'
	w_f = open('bing.txt', 'w')
	w_f.write(string)
	w_f.close()
	# print '-----------' + str(pn) + '-----------------'
	# pn = pn + 10
'''