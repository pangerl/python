# -*- coding: utf-8 -*-
import threading
import queue
import requests
from bs4 import BeautifulSoup

# 获取网页信息
def fetch(url, postdata=None):
    s = requests.Session()
    headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
    'Referer': 'https://www.lagou.com/jobs/list_%E8%BF%90%E7%BB%B4%E5%B7%A5%E7%A8%8B%E5%B8%88?px=default&city=%E6%AD%A6%E6%B1%89',
    'Host':'www.lagou.com',
    'Upgrade-Insecure-Requests': '1',
    'Cookie': 'xxxxx'
    }
    if postdata is not None:
        return s.post(url, timeout=5, data=postdata, headers=headers)
    return s.get(url, timeout=5, headers=headers)

# 保存到本地文件
def save_txt(text):
    with open("./2.txt","ab") as fp:
        fp.write(text.encode('utf-8'))

# 通过pn_queue获取页面数，将职位信息存入position_queue
def get_position(position_queue, pn_queue):
    while True:
        pn = pn_queue.get()
        postdata = {
            'first': 'false',
            'pn': pn,
            'kd': '运维工程师'
        }
        url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%AD%A6%E6%B1%89&needAddtionalResult=false'
        r = fetch(url, postdata=postdata)
        page_positions = r.json()['content']['positionResult']['result']
        for position in page_positions:
            # 存入字典
            position_dict = {
                        'position_name': position['positionName'],
                        'work_year': position['workYear'],
                        'salary': position['salary'],
                        'city': position['city'],
                        'company_name': position['companyFullName'],
                        'position_id': position['positionId']
                    }
            # 将职位字典存入队列
            position_queue.put(position_dict)
        pn_queue.task_done()

# 获取职位描述
def get_detail(position_queue):
    while True:
        position_dict = position_queue.get()
        position_id = position_dict['position_id']
        url = 'https://www.lagou.com/jobs/{}.html'.format(position_id)
        r = fetch(url)
        soup = BeautifulSoup(r.content, 'lxml')
        tags = soup.find(class_='job_bt')
        detail = tags.text
        text = """
-------------------------------------
公司名称：{company_name}
职位名称：{position_name}
工作年限：{work_year}
工资：{salary}
城市：{city}
职位描述：{detail}
-------------------------------------
    """.format(company_name=position_dict['company_name'], position_name=position_dict['position_name'],
               work_year=position_dict['work_year'], salary=position_dict['salary'], city=position_dict['city'], detail=detail)

        save_txt(text)
        position_queue.task_done()


def lagou_main():
    position_queue = queue.Queue()
    pn_queue = queue.Queue()
    # 一共有6页数据
    for i in range(1, 7):
        pn_queue.put(i)

    # 生成5个线程
    for i in range(5):
        t = threading.Thread(target=get_position, args=(position_queue, pn_queue))
        t.setDaemon(True)
        t.start()

    for i in range(5):
        t = threading.Thread(target=get_detail, args=(position_queue, ))
        t.setDaemon(True)
        t.start()

    position_queue.join()
    pn_queue.join()
