import re
import time
import pandas as pd
import requests
import pymysql
from langconv import *
 
# 繁体转简体
def convert(content):
    line = Converter("zh-hans").convert(content)
    return line

def sql_conn():
    '''数据库连接'''
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',
        db='sichuan_mail',  # 数据库名
        charset='utf8mb4',  # 设置编码格式
        cursorclass=pymysql.cursors.DictCursor  # 设置返回格式为字典格式 返回格式为数组包含字典[{}]    默认的是集合也就是()
    )


    return connection  # 将数据库连接返回


def req(page):
    '''请求列表页'''
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://tyj.sc.gov.cn",
        "Pragma": "no-cache",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://tyj.sc.gov.cn/sctyj/gkxj/gkxx_gl.shtml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39",
        "X-Requested-With": "XMLHttpRequest"
    }

    url = "http://tyj.sc.gov.cn/scstyjhd/consult/getPublicConsultPageList"
    data = {
        "pageSize": "10",
        "pageNumber": f"{page}" #翻页用
    }
    while True:
        try:
            response = requests.post(url, headers=headers, data=data, verify=False)
            response.encoding = response.apparent_encoding
            return response.json()  # 将数据以json的格式返回
        except Exception as e:
            time.sleep(2)


def detail_analysis(page,conn):
    '''爬取小项'''
    datas = req(page)  # 调用上面的函数
    #print(datas)

    for item in datas['rows']:
        # print(item)
        #问时间
        consultDate=item['consultDate']
        if not int(consultDate[:4]) >= 2015:
            return
        #问内容
        consultTitle=item['consultTitle']
        consultTitle=re.sub('<.*?>','',consultTitle)
        consultTitle=re.sub('\r\n','',consultTitle)#替换换行
        consultTitle=re.sub('\s+','',consultTitle)#替换空格
        consultTitle=convert(consultTitle)         #繁体转简体
        #答时间
        replyDate=item['replyDate']

        #答内容
        replyContent=item['replyContent']
        replyContent=re.sub('<.*?>','',replyContent)
        replyContent=re.sub('\r\n','',replyContent)#替换换行
        replyContent=re.sub('\s+','',replyContent)#替换空格
        replyContent=convert(replyContent)         #繁体转简体
        print(consultDate)

        # 写sql语句 存入数据库
        sql = '''
        insert into hdjl(title,mailType,mailDate,mailContent,replyDate,replyContent)

        values("%s","%s","%s","%s","%s","%s");

        ''' % ('None', 'None', consultDate, consultTitle, replyDate, replyContent)
        try:
            conn.execute(sql)
        except Exception as e:
            print('数据库写入失败')

        dic={
            'title':'None',
            'mailType': 'None',
            'mailDate':consultDate,
            'mailContent': consultTitle,
            'replyDate': replyDate,
            'replyContent': replyContent,
        }
        dic_list.append(dic) #添加到dic_list 列表中 为储存为csv做准备

if __name__ == '__main__':
    connection = sql_conn()  # 启动连接数据库 创建表 函数
    conn = connection.cursor()  # 创建游标

    dic_list = [] #空列表
    for page in range(1,77):  # 遍历列表 取出文字id  进行爬取
        detail_analysis(page, conn)
        time.sleep(1)
        # break

    df = pd.DataFrame(dic_list)
    df0=pd.read_csv('data.csv')
    del df0['Unnamed: 0']#删除最后一行
    df=pd.concat((df0,df),axis=0)#将两个表连接在一起

    df.to_csv('data.csv', encoding='utf_8_sig',index=None)  # 保存为csv

    connection.commit()  # 提交数据
    conn.close()  # 关闭浮标
    connection.close()  # 关闭数据库连接