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
    'Cookie': 'JSESSIONID=ABAAABAAAFCAAEG04EC8405BCC18F64C566C833E30833EF; _ga=GA1.2.604249756.1525311743; _gid=GA1.2.249895278.1525311743; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1525311744; user_trace_token=20180503094223-3a07bf5e-4e73-11e8-bd62-5254005c3644; LGUID=20180503094223-3a07c40d-4e73-11e8-bd62-5254005c3644; X_HTTP_TOKEN=a414ce312610d84d12a1fa5423f80b68; LG_LOGIN_USER_ID=9ddc8037b6c38cdd64901f065a67ea3a73b4f7938fd9fdaa; _putrc=DA1C985ED9E706CA; login=true; unick=%E9%BB%84%E5%B0%8F%E5%86%9B; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=56; index_location_city=%E6%9D%AD%E5%B7%9E; TG-TRACK-CODE=search_code; gate_login_token=476dcdd60e32a5101e12681a1ac265ed887fb2536169a7f1; LGRID=20180503140144-74cd418e-4e97-11e8-b884-525400f775ce; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1525327304; SEARCH_ID=585676fb28734fa2bced257342d2a805'
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
