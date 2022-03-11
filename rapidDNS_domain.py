import sys
import requests
from concurrent.futures import ThreadPoolExecutor
import re
import pymysql
import queue
from queue import Empty
from multiprocessing import Queue
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import multiprocessing
import argparse
import tldextract


num = 0
# con = pymysql.connect(host='127.0.0.1',port=3306,database='src_data',user='root',password='root')
# cur = con.cursor()
# cur.execute("select domain from company_info")

domain_queue = queue.Queue()

parse = argparse.ArgumentParser(prog='subdomain.txt is generated in the current directory',epilog='Thank you for using,author [y3ff18]')
parse.add_argument('-u','--url',help='Input a URL')
parse.add_argument('-f','--file',help='Input a File')
parse.add_argument('-t','--thread',help='Set Thread,defaule 50',default=50)
args = parse.parse_args()

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'Referer':'https://rapiddns.io'
}
def get_queue():
    with open(args.file,'r',encoding='utf-8') as f:
        for i in f:
            domain_queue.put(tldextract.extract(i).registered_domain)
    print('current file amount >> ',domain_queue.qsize())



f = open(r'subdomain.txt','a',encoding='utf-8')

def get_subdomain(domain):
    global num,f,done_domain
    if domain != '' and domain not in done_domain:
        resp = requests.get('https://rapiddns.io/subdomain/{}?full=1'.format(domain),headers=headers,timeout=30,verify=False,stream=True)
        results = re.findall(r'<th scope="row ">\d+</th>.*?<td>(.*?)</td>',resp.text,re.DOTALL)

        if len(results) == 0:
            f.write(str(domain)+' | '+str(domain)+'\n')
        elif len(results) == 1:
            num += 1
            f.write(str(domain)+' | '+str(results[0]+'\n'))
        else:
            for res in range(len(results)):
                num += 1
                # 第一个
                if str(domain) in str(tldextract.extract(results[res]).registered_domain):
                    if res == 0:
                        f.write(str(domain) + ' | ' + str(results[res] + ','))
                    # 最后一个
                    elif res == (len(results) - 1):
                        f.write(str(results[res] + '\n'))
                    # 其他处于之间的子域名
                    else:
                        f.write(str(results[res] + ','))
                    # print(i)
                else:
                    pass
        print(domain,num,end='\n')
        num = 0
    done_domain.append(domain)

if __name__ == '__main__':
    # sql_res()
    done_domain = multiprocessing.Manager().list()

    if args.url != None:
        get_subdomain(domain=tldextract.extract(args.url).registered_domain)

    if args.file != None:
        get_queue()
        with ThreadPoolExecutor(max_workers=args.thread) as pool:
            try:
                for i in range(domain_queue.qsize()):
                    pool.map(get_subdomain, [str(domain_queue.get(timeout=3))])
            except Empty:
                print('Done', end='\n')
                sys.exit(0)

    if args.file == None and args.url == None:
        print('''
[+] usage:
        python3 rapidDNS_domain.py -h
        ''')
