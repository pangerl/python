# -*- coding: utf-8 -*-

import threading
import queue
import requests
import time
import sys
from bs4 import BeautifulSoup

# 获取所有职位信息，加入队列
def get_position(position_queue, session, pn):
    postdata = {
        'first': 'false',  # 是否为第一页，我这里全部用否，因为我只关心职位信息
        'pn': pn,       # 第几页
        'kd': '运维工程师'   # 查询关键字
    }
    url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%AD%A6%E6%B1%89&needAddtionalResult=false'
    # 拉钩有反爬机制，头部不加入cookie，爬取四页就挂了。我用了session也不行，只能加上。
    header={
    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Mobile Safari/537.36',
    'Referer':'https://www.lagou.com/jobs/list_%E8%BF%90%E7%BB%B4%E5%B7%A5%E7%A8%8B%E5%B8%88?city=%E6%AD%A6%E6%B1%89',
    'Host':'www.lagou.com',
    'Cookie': 'XXXXXXXX'
    }
    r = session.post(url, data=postdata, headers=header)
    time.sleep(4)
    #print(r.json())
    page_positions = r.json()['content']['positionResult']['result']
    for position in page_positions:
        # 用字典存放职位信息
        position_dict = {
                    'position_name': position['positionName'],
                    'work_year': position['workYear'],
                    'salary': position['salary'],
                    'city': position['city'],
                    'company_name': position['companyFullName'],
                    'position_id': position['positionId']
                }
        # 加入队列
        position_queue.put(position_dict)


# 获取对应职位的描述，写入文件
def get_detail(position_queue, session, i):
    position_dict = position_queue.get()
    # 获取ID，拼接网页链接
    position_id = position_dict['position_id']
    url = 'https://www.lagou.com/jobs/{}.html'.format(position_id)
    header={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    'Referer': url,
    'Host':'www.lagou.com',
    'Upgrade-Insecure-Requests': '1',
    'Cookie': 'XXXXXXXXX'
    }
    r = requests.get(url, headers=header)
    time.sleep(2)
    # 筛选职位信息
    soup = BeautifulSoup(r.content, 'lxml')
    tags = soup.find(class_='job_bt')
    detail = tags.text
    text = """
第-{i}-条招聘信息
-------------------------------------
公司名称：{company_name}
职位名称：{position_name}
工作年限：{work_year}
工资：{salary}
城市：{city}
职位描述：{detail}
-------------------------------------
    """.format(i=i, company_name=position_dict['company_name'], position_name=position_dict['position_name'], work_year=position_dict['work_year'], salary=position_dict['salary'], city=position_dict['city'], detail=detail)
    # 将职位信息保存到txt文件
    with open("./1.txt","ab") as fp:
        fp.write(text.encode('utf-8'))


# 线程1，生成职位信息
# 通过继承threading类，创建线程，重写run方法
class Get_position(threading.Thread):
    def __init__(self, position_queue, session):
        threading.Thread.__init__(self)
        self.position_queue = position_queue
        self.session = session

    def run(self):
        # 翻页，这里只翻六页
        for pn in range(1, 7):
            try:
                get_position(self.position_queue, self.session, pn)
                print('爬取第-{}-页成功'.format(pn))
            except Exception as e:
                print('exception:' + str(e))


# 线程2，消费职位信息
class Get_detail(threading.Thread):
    def __init__(self, position_queue, session):
        threading.Thread.__init__(self)
        self.position_queue = position_queue
        self.session = session

    def run(self):
        i = 1
        while True:
            try:
                get_detail(self.position_queue, self.session, i)
                i += 1
                #print('存入第-{}-条数据'.format(i))
            except Exception as e:
                print('exception:' + str(e))


# 线程3，队列为空时退出
class Control(threading.Thread):
    def __init__(self, position_queue):
        threading.Thread.__init__(self)
        self.position_queue = position_queue

    def run(self):
        while True:
            print('程序执行中')
            time.sleep(40)
            if self.position_queue.empty():
                print('程序执行完毕!')
                sys.exit()

# 创建一个全局的队列
position_queue = queue.Queue()
session = requests.Session()

t1 = Get_position(position_queue, session)
t2 = Get_detail(position_queue, session)
t3 = Control(position_queue)

t1.start()
t2.start()
t3.start()
