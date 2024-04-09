import jieba
import pandas as pd
import pymysql
import collections # 词频统计库
import wordcloud # 词云展示库
from imageio import imread
#链接数据库
connection = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='123',db='sichuan_mail',charset='utf8mb4')
sql = "select * from hdjl"
df = pd.read_sql(sql,connection)
replyContent=df['replyContent']
cons=str(replyContent)
print(cons)
file_stop='chineseStopWords.txt'
mk=imread("pic.png")
words=jieba.lcut(cons)
text = ' '.join(words)
wc = wordcloud.WordCloud(font_path="SimHei.ttf",mask=mk,width = 1000, height = 700,background_color='white', max_words=100,stopwords=file_stop)
wc.generate(text)
wc.to_file("reply.png")