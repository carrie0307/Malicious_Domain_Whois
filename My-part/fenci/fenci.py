#encoding=utf-8
'''
	功能： 对words_n.txt 中的关键词进行验证，测试每个网友中含有几个words中的词，结果存入count_list字典

'''
from __future__ import division 
import jieba
import re
from tfidf_top import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


stop_list = ['的', '或', '是', '啦', '去' ,'也', '只', '而']


# 普通分词
def cut_string(string):
	words = []
	seg_list = jieba.cut(string, cut_all=False)
	temp = ",".join(seg_list)
	temp = temp.split(',')
	for i in temp:
		if i not in stop_list:
			words.append(i)
	return words


def read_string(filename):
	file = open('../fenci/code/words_2_' + str(filename) + '.txt', 'r')
	content = file.read()
	file.close()
	return content


def pre_deal(string):
	string = re.sub("[\A-Za-z0-9_\s+\.\!\/_,$%^*(+\"\']".decode("utf8"), "".decode("utf8"),string)
	string = re.sub("[+——！，。？、~@#￥%……&*（）：“”;【】?―:　-]".decode("utf8"), "".decode("utf8"),string)
	string = re.sub("[\{\}<>=)«|\[\]  ]".decode("utf8"), "".decode("utf8"),string)
	return string


def save_fenci(string, filename, top):
	w_file = open('../fenci/fenci_res/fenci_' + '1_71' + '_top' + str(top) +  '.txt', 'w')
	w_file.write(string)
	w_file.close()
	print 'over ... \n'



if __name__ == '__main__':
	# 赌博 色情
	words = open('../fenci/fenci_res/words/色情words.txt', 'r').readlines()
	count_list = {}
	num_list = {}
	flag1 = 0
	flag2 = 0
	for i in range(1,115):
		count = 0
		num = 0
		# string = pre_deal(read_string(i))
		string = read_string(i)
		length = len(cut_string(string))
		for word in words:
			word = word.strip()
			if word in string:
				num = num + string.count(word)
				count = count + 1
		rate = num / length
		num_list[i] = rate
		count_list[i] = count
		print str(i) + '\t\t' + str(count) + '\t\t' + str(rate)
		if rate < 0.1:
			flag1 = flag1 + 1
			# print '-----' + str(i) + '-----'
		if count < 4:
			# print '*****' + str(i) + '*****'
			flag2 = flag2 + 1
	print 'flag1   ' + str(flag1)
	print 'flag2   ' + str(flag2)
	count_list = sorted(count_list.items(), key=lambda count_list: count_list[1], reverse = True)
	num_list = sorted(num_list.items(), key=lambda num_list: num_list[1], reverse = True)
	# print count_list
	# print num_list
	

