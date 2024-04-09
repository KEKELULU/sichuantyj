#导入所需要的库
import pymysql
import pandas as pd
import pyecharts.options as opts
from pyecharts import options as opts
from pyecharts.charts import Bar
#连接数据库
connection = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='123',db='sichuan_mail',charset='utf8mb4')
sql = "select * from emotion"
df = pd.read_sql(sql,connection)
#统计积极来信，消极来信数量
mpos = 0
mneg = 0
for i in df['mailemotion']:
    if i >= 0.5:
        mpos += 1
    else:
        mneg += 1
        
print('来信正向，负向数目分别为：',mpos,mneg)
rpos = 0
rneg = 0
for i in df['replyemotion']:
    if i >= 0.5:
        rpos += 1
    else:
        rneg += 1
        
print('回信正向，负向数目分别为：',rpos,rneg)
coloums=["来信","回信"]
data1=[mpos,rpos]
data2=[mneg,rneg]

bar = Bar()
bar.add_xaxis(coloums)
bar.add_yaxis('正向',data1,stack='stack')
bar.add_yaxis('负向',data2,stack='stack')
# set_global_opts全局
bar.set_global_opts(title_opts=opts.TitleOpts(title="堆叠图"))
# set_series_opts系列，删除数字
bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

stack_bar = (
    Bar(init_opts=opts.InitOpts(width="900px", height="500px"))#设置图表画布宽度
    .add_xaxis(coloums)
    .add_yaxis('正向',data1,stack='stack',bar_min_width=1,bar_max_width=50,color="#a834a8")
    .add_yaxis('负向',data2,stack='stack',color="#42b7bd", bar_min_width=11,is_selected=True)
    #设置标签属性
    .set_series_opts(
        label_opts=opts.LabelOpts(position="inside", color="white", font_size=18,font_style="normal",font_weight='normal',font_family='Times New Roman', formatter="{c}"))     
    .set_global_opts(
        legend_opts=opts.LegendOpts(textstyle_opts=opts.LabelOpts(font_size=18,font_family='Times New Roman',font_weight='bold')),#设置图例属性
        #设置横纵坐标属性
        xaxis_opts=opts.AxisOpts(name_textstyle_opts=opts.TextStyleOpts(font_weight='bold',font_size=17,font_family='Times New Roman'),name="Type",axislabel_opts=opts.LabelOpts(font_size=18,font_family='Times New Roman',font_weight="normal" ),interval=115,boundary_gap=['50%', '80%']),
        yaxis_opts=opts.AxisOpts(name_textstyle_opts=opts.TextStyleOpts(font_weight='bold',font_size=17,font_family='Times New Roman'),name="Count",axislabel_opts=opts.LabelOpts(font_size=18,font_style="normal",font_weight="normal" ,font_family='Times New Romanrial',formatter="{value}"))
    )
)
stack_bar.render("stack_bar.html")