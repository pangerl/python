# -*- coding: utf-8 -*-

import requests
import queue
import threading
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# 随机获取ua信息
def get_user_agent():
    ua = UserAgent()
    return ua.random

# 爬取网页内容
def fetch(url, proxy=None):
    s = requests.Session()
    s.headers.update({'user-agent': get_user_agent()})

    proxies = None
    if proxy is not None:
        proxies = {
            'http': proxy,
        }
    return s.get(url, timeout=5, proxies=proxies)

# 保存代理ip信息至列表
def save_proxies(url):
    proxies = []
    try:
        r = fetch(url)
    except requests.exceptions.RequestException:
        return False
    soup = BeautifulSoup(r.text, 'lxml')
    trs = soup.find_all('tr')
    for x in range(1, len(trs)):
        tds = trs[x].find_all('td')
        address = tds[1].contents[0] + ':' + tds[2].contents[0]
        proxies.append(address)
    return proxies

# 保存代理IP的列表到队列中
def save_proxies_with_queue(in_queue, out_queue):
    while True:
        url = in_queue.get()
        rs = save_proxies(url)
        out_queue.put(rs)
        in_queue.task_done()
# 将队列中的列表统一输出到result列表
def append_result(out_queue, result):
    while True:
        rs = out_queue.get()
        if rs:
            result.extend(rs)
        out_queue.task_done()

# 获取所有代理IP，返回result列表
def use_thread_with_queue():
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    url = 'http://www.xicidaili.com/nn/'
    for i in range(5):
        t = threading.Thread(target=save_proxies_with_queue, args=(in_queue, out_queue))
        t.setDaemon(True)
        t.start()
    # 爬取两页
    for i in range(1, 3):
        url_pn = url + str(i)
        in_queue.put(url_pn)
    result = []
    for i in range(5):
        t = threading.Thread(target=append_result, args=(out_queue, result))
        t.setDaemon(True)
        t.start()

    in_queue.join()
    out_queue.join()
    #print(len(result))
    return result

# 检查代理IP的可用性
def check_proxy(result_queue, check_ip):
    while True:
        p = result_queue.get()
        try:
            fetch('http://baidu.com', proxy=p)
            check_ip.append(p)
        except RequestException:
            pass
        finally:
            result_queue.task_done()

# 返回可用的代理IP
def proxy_main(n):
    result_queue = queue.Queue()
    proxy_ip = use_thread_with_queue()
    check_ip = []
    for i in set(proxy_ip):
        result_queue.put(i)
    # 手动设置并发线程的数量
    for i in range(n):
        t = threading.Thread(target=check_proxy, args=(result_queue, check_ip))
        t.setDaemon(True)
        t.start()
    result_queue.join()
    #print(len(check_ip))
    return check_ip

# 测试运行时间
def run_time(n):
    start = time.time()
    proxy_main(n)
    end = time.time()

    print(str(end-start))
