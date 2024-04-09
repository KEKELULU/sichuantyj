#导入所需要的库
import pymysql
import pandas as pd
from snownlp import SnowNLP
#连接数据库
connection = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='123',db='sichuan_mail',charset='utf8mb4')
sql = "select * from hdjl"
df = pd.read_sql(sql,connection)

#情感分析
df['mailemotion'] = df['mailContent'].apply(lambda x:SnowNLP(x).sentiments)
df['replyemotion'] = df['replyContent'].apply(lambda x:SnowNLP(x).sentiments)
dic_list = []
for i in range(0,933):
    dd = df['mailDate'][i]
    mc = df['mailContent'][i]
    me = df['mailemotion'][i]
    rc = df['replyContent'][i]
    re = df['replyemotion'][i]
#导入数据库
    cursor = connection.cursor()
    try:
        sql = '''insert into emotion(mailDate,mailContent,mailemotion,replyContent,replyemotion) values("%s","%s","%s","%s","%s");''' % (dd,mc,me,rc,re)
        cursor.execute(sql)
        print(sql)
        cursor.close()
        print('插入成功')
    except:
        pass
#创建词典
    dic={
            'mailDate': dd,
            'mailContent':mc,
            'mailemotion':me,
            'replyContent': rc,
            'replyemotion': re,
        }
    dic_list.append(dic) #添加到dic_list 列表中 为储存为csv做准备
 #导入csv   
df=pd.DataFrame(dic_list)
df.to_csv('情感分析情绪值.csv',encoding='utf_8_sig')    #保存为csv
connection.commit()
connection.close()
