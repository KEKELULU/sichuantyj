import jieba
import pymysql
import pandas as pd
import collections
#链接数据库
conn = pymysql.connect(host='localhost',user='root',password='123456',db='sichuan_mail',charset='utf8mb4')
sql = "select * from hdjl"
df = pd.read_sql(sql,conn)
con = df["mailContent"].tolist() 
cons=str(con)

#导入停用词表
stopwords = [line.rstrip() for line in open('chineseStopWords.txt', 'r', encoding='utf-8')]
#jieba分词
words=jieba.lcut(cons)
#print(words)
meaninful_words = []
for word in words:
    #忽略单个字，忽略11位手机号
   if len(word)==1 or len(word)>10:
        continue
   else:
        if word not in stopwords:
            meaninful_words.append(word)
#计算词频
word_counts = collections.Counter(meaninful_words) # 对分词做词频统计
word_counts_common= word_counts.most_common()#返回出现频率最高的值和他们相应的频率
res=dict(word_counts_common)#转化为词典
#print(res)
items =list(res.items())
items.sort(key=lambda x:x[1],reverse=True)
for i in range(100):#选择前100个高频词
     word,count = items[i]
     #导入数据库table为gaopin
     cursor = conn.cursor()  # 创建游标
     sql = '''
     insert into gaopin(word,num) values("%s","%s");''' % (word,count)
     cursor.execute(sql)
     cursor.close()
#导入csv
df = pd.DataFrame.from_dict(res, orient='index',columns=['num'])
df = df.reset_index().rename(columns = {'index':'word'})
df.to_csv("高频词统计.csv",encoding='utf_8_sig') 
conn.commit()
conn.close()  # 关闭浮标
print('插入成功')
print('保存成功')