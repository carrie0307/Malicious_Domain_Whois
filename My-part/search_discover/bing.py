# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup


headers = {"Accept": "text/html;",
	            "Accept-Language": "zh-CN,zh;q=0.8",
	            "Referer": "http://cn.bing.com/search?q=hao6688&pn=0",
	            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
	            }


url = 'http://bbs.cntv.cn/thread-8017613630-1-1.html'
r = requests.get(url, headers=headers)
print r.status_code
