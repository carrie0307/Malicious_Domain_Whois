# -*- coding: UTF-8 -*-
# from mysql import get_domains
# from tfidf import get_top_words
from bs4 import BeautifulSoup
import urllib2
from StringIO import StringIO
import jieba.analyse
import chardet
import gzip
import word
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


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
	# charset = info.getparam('charset')
	# print charset
		content = content.decode(charset, 'ignore')
	return content


if __name__ == '__main__':
	# domains = get_domains()
	# words_list = open('../fenci/fenci_res/words/words.txt', 'r').readlines()
	domains = ['00x240660.geujqj.cn']
	for domain in domains:
		url = 'http://' + domain
		# try:
		req = urllib2.urlopen(url)
		# info = req.info()
		# charset = info.getparam('charset')
		# encoding = info.getheader('Content-Encoding')
		# content = req.read()
		# if encoding == 'gzip':
			# buf = StringIO(content)
			# gf = gzip.GzipFile(fileobj=buf)
			# content = gf.read()
			# print content
			# print ';---'
		content = pre_deal_html(req)
		# soup = BeautifulSoup(content, 'lxml')
		content = word.pre_deal(content)
		# print content
		# print str(soup)
		 # except Exception, e:
			# print str(e)
			# break
		keywords = jieba.analyse.extract_tags(content, topK=5)
		keywords = str(','.join(keywords))
		print keywords
		# print type(keywords)
		'''
		count, rate = detecte_type(string, words_list)
		print count
		print rate
		key_words = jieba.analyse.extract_tags(string, topK=5)
		print str(key_words).replace('u\'', '\'').decode("unicode-escape")
		'''