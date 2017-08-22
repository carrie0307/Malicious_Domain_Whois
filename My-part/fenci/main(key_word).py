# coding:utf-8

"""
    这是接口使用的例子。
    使用时，自己定义三个关键函数，传给我的接口。会自动开线程跑起来。
"""


from bs4 import BeautifulSoup
import SpiderEntry
import MySQLdb
import jieba.analyse
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def select_domain():
    conn=MySQLdb.connect("172.26.253.3", "root", "platform", "malicious_domain_sys")
    cur=conn.cursor()
    cur.execute("SELECT domain_index.domain FROM domain_index WHERE domain_index.ID NOT IN (SELECT malicious_info.ID FROM malicious_info) LIMIT 100;")
    result=cur.fetchall()
    domains=[]
    for item in result:
        domains.append(item[0])
    print "domains got !\n"
    print domains
    return domains
    #return ["www.baidu.com","www.qq.com"]


def parse_words_html(content):
    keywords = jieba.analyse.extract_tags(content, topK=5)
    keywords = str(','.join(keywords))
    return keywords


conn = MySQLdb.connect('172.26.253.3', 'root', 'platform', 'malicious_domain_sys', charset = 'utf8')
cur = conn.cursor()
current_times = 0
def commit_keywords(domain,keywords):
    global conn, cur, current_times
    print '*****'
    cur.execute("REPLACE INTO malicious_info(ID, key_word) VALUES('" + str(hash(domain)) + "' , '" + keywords + "')")
    conn.commit()
    print "Keywords saved succeed!"
    '''
    if current_times == 20:
        conn.commit()
        print "Keywords saved succeed!"
        current_times = 0
    else:
        current_times = current_times + 1
        print 'current_times: ' + str(current_times)
    '''
    #conn.commit()
    #cur.close()
    #conn.close()


SpiderEntry.start_evrything(select_domain, parse_words_html, commit_keywords, 5)

#最后再提交一次commit
conn.commit()
