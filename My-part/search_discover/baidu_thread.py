# -*- coding: UTF-8 -*-
import threading
from baidu_2 import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')





if __name__ == '__main__':
	# wd_list = get_domains()
	pn = 150
	wd_list = ['金冠娱乐', '博金冠', '娱乐场', '葡京']
	for wd in wd_list:
		print wd
		'''
		print 'wd: ' + wd
		threads = []
		t1 = threading.Thread(target=Baidu_get_raw_html, args=(wd, pn))
		threads.append(t1)
		t2 = threading.Thread(target=Bing_get_raw_html, args=(wd, pn))
		threads.append(t2)
		t3 = threading.Thread(target=Haoso_get_raw_html, args=(wd, pn))
		threads.append(t3)
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		'''
