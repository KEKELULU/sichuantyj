#导入所需要的库
import re
import time
import pandas as pd
import requests
import pymysql
from langconv import *

def convert(content):
    '''繁体转简体'''
    line = Converter("zh-hans").convert(content)
    return line
#链接数据库
def sql_conn():
    '''数据库连接'''
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',
        db='sichuan_mail',             #数据库名
        charset='utf8mb4',  # 设置编码格式
        cursorclass=pymysql.cursors.DictCursor  # 设置返回格式为字典格式 返回格式为数组包含字典[{}] 默认的是集合也就是()
    )

    conn= connection.cursor()            #创建游标
    #建表
    sql= '''create table hdjl(         
        id int unique auto_increment,         
        title text,
        mailType text,
        mailDate text,
        mailContent text,
        replyDate text,
        replyContent text

    );'''
    try:                    #已经建过表的情况下或出现报错  使用try进行捕获 避免程序中断
        conn.execute(sql)
    except Exception as e:
        print('表已创建')

    connection.commit()      #向数据库提交操作
    conn.close()            #关闭游标

    return connection       #将数据库连接返回


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

    url = "http://tyj.sc.gov.cn/scstyjhd/mailbox/getPublicMailPageList"
    data = {
        "pageSize": "12",
        "pageNumber": f"{page}",     #翻页参数
        "mailNumber": ""
    }
    while True:
        try:
            response = requests.post(url, headers=headers, data=data, verify=False)
            response.encoding = response.apparent_encoding
            return response.json()               #将数据以json的格式返回
        except Exception as e:
            time.sleep(2)




def detail_analysis(page,conn):
    datas = req(page)  # 调用上面的函数
    print(datas)

    for item in datas['rows']:
        # print(item)           
        # 来信标题
        title=item['mailTitle']
        title=convert(title)
        #来信类型
        mailType=item['mailType']
        #来信时间
        mailDate=item['mailDate']
        if not int(mailDate[:4]) >=2015:#过滤时间2015年之后
            return

        #来信内容
        mailContent=item['mailContent']
        mailContent=re.sub('\r\n','',str(mailContent))
        mailContent=re.sub("\s+",'',str(mailContent))
        mailContent=re.sub('\'','\"',str(mailContent))
        mailContent=convert(mailContent)
        #回复时间
        replyDate=item['replyDate']
        #回复内容
        replyContent=item['replyContent']
        replyContent=re.sub('\r\n','',str(replyContent))#替换换行符
        replyContent=re.sub("\s+",'',str(replyContent))#替换空格
        replyContent=re.sub('\'','\"',str(replyContent))#替换单引号为双引号
        replyContent=convert(replyContent)

        #写sql语句 存入数据库
        sql='''
        insert into hdjl(title,mailType,mailDate,mailContent,replyDate,replyContent) 
        
        values("%s","%s","%s","%s","%s","%s");
        
        '''%(title,mailType,mailDate,mailContent,replyDate,replyContent)
        try:
            conn.execute(sql)
        except Exception as e:
            print('数据库写入失败')

        dic={
            'title':title,
            'mailType':mailType,
            'mailDate': mailDate,
            'mailContent':mailContent,
            'replyDate': replyDate,
            'replyContent': replyContent,
        }
        print(dic)
        dic_list.append(dic)  #添加到dic_list 列表中 为储存为csv做准备


if __name__ == '__main__':
    connection = sql_conn()  # 启动连接数据库 创建表 函数
    conn = connection.cursor()  # 创建游标

    dic_list = []
    for page in range(1,43):  # 翻页
        detail_analysis(page, conn)#逐页写入数据库
        time.sleep(1)
        # break

    df=pd.DataFrame(dic_list)
    df.to_csv('data.csv',encoding='utf_8_sig')    #保存为csv
    connection.commit()  # 提交数据
    conn.close()  # 关闭浮标
    connection.close()  # 关闭数据库连接
