#导入所需要的库
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#连接数据库
connection = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='123',db='sichuan_mail',charset='utf8mb4')
sql = "select * from emotion"
df = pd.read_sql(sql,connection)

#做直方图
plt.figure(figsize=(9, 6), dpi=100)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False

bins=np.arange(0,1.1,0.1)#分成10个bin
plt.hist(df['mailemotion'],bins,color='#b7968f',edgecolor='#a56d60',alpha=0.9)
plt.xlim(0,1)
plt.xlabel('情绪值')
plt.ylabel('频数')
plt.title('来信内容情感分析直方图')
plt.savefig('来信情绪值分布直方图.jpg')