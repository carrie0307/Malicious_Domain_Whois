# coding:utf-8
from bs4 import BeautifulSoup
import urllib2
from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
from tld import get_tld
import MySQLdb
import socket
import threading
socket.setdefaulttimeout(10)
import Queue


# lottery_words = open('../fenci/fenci_res/words/赌博words.txt', 'r').readlines()
# sexy_words = open('../fenci/fenci_res/words/色情words.txt', 'r').readlines()
# words_list = [lottery_words, sexy_words]


def get_whitelist():
	file = open('white_list', 'r')
	whitelist = file.read().split('\n')
	file.close()
	return whitelist


def get_blacklist():
	conn = MySQLdb.connect("172.26.253.3", "root", "platform", "malicious_domain_sys")
	cur = conn.cursor()
	SQL = "SELECT DISTINCT url_domain FROM malicious_link;"
	cur.execute(SQL)
	result = cur.fetchall()
	blacklist = []
	for item in result:
		blacklist.append(item[0])
	return blacklist

white_list = get_whitelist()
black_list = get_blacklist()


def get_domains():
	conn = MySQLdb.connect("172.26.253.3", "root", "platform", "malicious_domain_sys")
	cur = conn.cursor()
	SQL = "select domain from domain_index, malicious_info where domain_index.ID = malicious_info.ID and state = '1';"
	cur.execute(SQL)
	result = cur.fetchall()
	domains = []
	for item in result:
		domains.append(item[0])
	print "domains got !\n"
	print domains
	return domains

domains = get_domains()
q = Queue.Queue()
for domain in domains:
	q.put(domain)


def get_final_url(url):
	with Display(backend="xvfb", size=(1440, 900)):
		driver = webdriver.Chrome()
		driver.maximize_window()
		driver.get(url)
		url = driver.current_url
		driver.quit()
		return url


def get_html(domain):
	url = 'http://' + domain
	try:
		html = urllib2.urlopen(url).read()
		soup = BeautifulSoup(html)
		return soup
	except Exception, e:
		return None


def get_a_links(domain, soup):
	global white_list
	a_links = {}
	for a in soup.find_all('a'):
		try:
			u = a['href']
			url_domain = get_tld(a['href'])
			if url_domain not in white_list and url_domain != domain:
				if url_domain not in a_links.keys():
					a_links[url_domain] = []
					if '.png' not in u and '.jpg' not in u:
						a_links[url_domain].append(u)
				else:
					if '.png' not in u and '.jpg' not in u:
						a_links[u].append(u)
		except Exception, e:
			a_links = {}
	return a_links


def check_black_list(domain, url_domain):
	global balck_list
	if url_domain in black_list:
		return True
	else:
		return False


'''
def check_malicious_word():
	res = []
	# 这里的content是soup,提取title后转化为str
	content = str(content)
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
		malicious_keywords = ','.join(theme_words)
		res.append((count, rate, malicious_keywords))
	# 赌博 0/色情 1, res[][0]: count, res[][1]: rate, res[][2]: malicious_keywords
	if res[0][0] > res[1][0]:
		return 0
	else:
		return 1
'''



def judge_link_urls(a_links):
	# while True:
		# try:
			# a_links = ***_q.get()
	for key in a_links:
		# 如果domain在黑名单或者通过关键词检测为恶意，则加入存储结果队列
		# if check_black_list(domain, key) == True or malicious_words(domain, key, a_links[key][0]) == True:
		if check_black_list(domain, key) == True :
			print 'ok'
		else:
			print '==============='
			# for item in a_links[key]:
				# res_q.put(domain, key, item)
		# except Queue.Empty:
			# return

def run():
	string = ''
	global q
	global white_list
	while True:
		domain = q.get()
		soup = get_html(domain)
		if soup != None:
			links = get_a_links(domain, soup)
			if links != {}:
				for key in links.keys():
					print key
					if key not in white_list:
						string = string + key + '\n'
		if q.empty():
			break
	w_file = open('links.txt', 'a')
	w_file.write(string)
	w_file.close()



if __name__ == '__main__':
	run_td = []
	for _ in range(10):
		run_td.append(threading.Thread(target=run))
	for td in run_td:
		td.start()
	for td in run_td:
		td.join()
	'''
	string = ''
	for domain in domains:
		soup = get_html(domain)
		if soup != None:
			links = get_a_links(domain, soup)
			if links != {}:
				print domain
				print links
				string = string + domain + '\n' + str(links) + '\n\n'
	w_file = open('links.txt', 'w')
	w_file.write(string)
	w_file.close()
	'''