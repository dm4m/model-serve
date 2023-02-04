import pymysql
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import matplotlib
import io
import base64
import scipy.stats as st

class mydb:#数据库操作类

    def __init__(self,host,user,password,database,port,charset):
        self.host=host
        self.user=user
        self.password=password
        self.database=database
        self.port=port
        self.charset=charset
        
    def myconnect(self):#连接数据库
        conn = pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database,port=self.port,charset = self.charset)
        return conn

    def myexecu(self,execuword):#执行查询语句并保存在data中
        self.conn=self.myconnect()
        cursor=self.conn.cursor()
        cursor.execute(execuword)        
        self.data = cursor.fetchall()
        cursor.close()


    def endconn(self):#断开数据库连接
        self.conn.close()
        print("success")

class cladata:#基类

    def __init__(self,db,title):#将data内容传递给cladata类
        self.data=db.data
        self.title=title
        self.db=db


class authoranaly(cladata):#申请人分析


    def authorpie(self,dic,title):#绘制饼状图
        plt.figure(figsize = (15,15))
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus']=False
        x = dic.values()
        plt.subplot(335)
        plt.title(title)
        mydic={}
        n=0
        for key,value in dic.items():
            n+=1
            if n<=20:
                mydic[key]=value
            else:
                break
        x=mydic.values()
        plt.pie(x,labels=mydic.keys(),labeldistance=1.2,autopct='%1.2f%%',shadow=True,startangle=90,radius=4,pctdistance=1.1)
        plt.legend()
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read())           
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output


    def authorbar(self,dic):#绘制柱状图
        plt.figure(figsize=(8,8),frameon=False)
        plt.title(self.title)
        plt.xlabel('发明人')
        plt.ylabel('数量')
        plt.xticks(fontsize=5)
        plt.grid()
        plt.rcParams['font.sans-serif'] = ['Kaitt', 'SimHei']
        X, Y = [], []
        n=0
        for key,value in dic.items():
            n+=1
            if n<=20:
                X.append(key)
                Y.append(int(value))
            else:
                break
        plt.bar(X , Y)                 
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read())           
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output
        
    def authorlist(self):#将数据中所有作者解析
        dic={}
        for i in self.data:
            mystr=i[1]
            list=str(mystr).split(";")
            for h in list:
                if h[0]==' ':
                    h=h[1:]
                dic[h]=0
        return dic
    
    def listsort(self,dic,id):#给字典赋值并排序
        total=0
        for i in dic.keys():
            i=str(i)
            self.db.myexecu("select count(inventor_list) as cnt from( select inventor_list from patent.patent where  (inventor_list like'%; "+i+"'"+" or inventor_list like'%"+i+";%'"+" or inventor_list like '%;"+i+"'"+" or inventor_list ="+"'"+i+"'"+") and id in"+id+" ) as ccc")
            num=str(self.db.data)
            num=num[2:-4]
            num=int(num)
            dic[i]=num
        for i in dic.values():
            total+=i
        self.total=total
        a1=sorted(dic.items(),key=lambda x:x[1],reverse = True)
        dic=dict(a1)
        self.dic=dic
        return dic

  
class areaanaly(cladata):#地域分析
    

    def certainarea(self,name,id):#某个省份的信息
        self.db.myexecu("SELECT  * FROM patent.patent where id in "+id+" and ( substring(applicant_area,1,INSTR(applicant_area,'(')-1)='"+name+"' or substring(applicant_area,1,INSTR(applicant_area,';')-1)='"+name+"')")
        return self.db.data
        
    def newdic(self):#创建一个字典
        dic={}
        for i in self.data:
            dic[i[1]]=i[0]
        return dic

    def areabar(self,dic):#绘制柱状图
        plt.title(self.title)
        plt.xlabel('地区')
        plt.ylabel('数量')
        plt.xticks(fontsize=5)
        plt.grid()
        plt.rcParams['font.sans-serif'] = ['Kaitt', 'SimHei']
        X, Y = [], []
        n=0
        for key,value in dic.items():
                X.append(key)
                Y.append(int(value))
        plt.bar(X , Y)             
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read()) 
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output    

    def areapie(self,dic):#绘制饼状图
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus']=False
        x = dic.values()
        plt.subplot(335)
        plt.title(self.title)
        plt.pie(x,labels=dic.keys(),labeldistance=1.2,autopct='%10.1f%%',shadow=True,startangle=90,radius=4,pctdistance=0.7)
        plt.legend()
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read())
        print(my_base64_jpgData)
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output  


class trendanaly(cladata):#趋势分析


            
    def opendic(self,stime,etime):#每遇到一个新类型就新建一个新字典
        dic={}
        i=stime
        while i<=etime:
            dic[i]=0
            i+=1
        return dic
    
    def newdic(self,stime,etime):#创建值为字典的字典对
        updic={}
        for h in self.data:
            updic[h[0]]=self.opendic(stime,etime)               
        for h in self.data:
            updic[h[0]][float(h[1])]=h[2]    
        return updic
               
    def trendpie(self,dic):#绘制每个类别的饼状图
        output=[]
        for key,value in dic.items():
            output.append(self.pietrend(value,key))
        return output
            

    def pietrend(self,dic,title):#绘制饼状图
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus']=False
        x = dic.values()
        plt.subplot(335)
        plt.title(title)
        plt.pie(x,labels=dic.keys(),labeldistance=1.2,autopct='%10.1f%%',shadow=True,startangle=90,radius=4,pctdistance=0.7)
        plt.legend()
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read())
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output
                
    def trendline(self,dic,stime,etime):#绘制折线图
        plt.figure(2)
        n=0
        plt.title(self.title)
        plt.xlabel('年份')
        plt.ylabel('数量')
        plt.rcParams['font.sans-serif'] = ['Kaitt', 'SimHei']
        plt.grid()
        for i in dic.keys():
            n+=1     
        for upkey,upvalue in dic.items():
            X, Y = [], []
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
            for value in upvalue.values():
                Y.append(float(value))
            X=np.arange(stime,etime+1)   
            plt.plot(X , Y,label=upkey,marker='o')           
        plt.legend()
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read())           
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output

                
    def trendbar(self,dic,stime,etime):#绘制时间趋势柱状图     
        wid=0
        n=0
        plt.figure(1)
        plt.title(self.title)
        plt.xlabel('年份')
        plt.ylabel('数量')
        plt.grid()
        for i in dic.keys():
            n+=1
        plt.rcParams['font.sans-serif'] = ['Kaitt', 'SimHei']
        for upkey,upvalue in dic.items():
            X, Y = [], []
            plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
            for value in upvalue.values():
                Y.append(float(value))
            X=np.arange(stime,etime+1)
            total_width = 0.8
            width = total_width / n
            X = X - (total_width - width) / 2      
            plt.bar(X + wid*width, Y,width=width,label=upkey)           
            for i, j in zip(X + wid*width, Y):
                plt.text(i, j + 0.01, "%.2f" % j, ha="center", va="bottom", fontsize=7)
            wid+=1
        plt.legend()          
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, format='jpg',dpi=800)
        plt.close()
        my_stringIObytes.seek(0,0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read())          
        output=str(my_base64_jpgData,encoding='utf-8')           
        return output

    
def myinput(list): #将系统的输入转换成sql语句中所要的格式
    mystr='('
    for i in list:
        mystr+=str(i)
        mystr+=','
    mystr=mystr[0:-1]
    mystr+=')'
    return mystr


def trendsql(stime,etime,list):#趋势分析sql语句
    sqlstr="SELECT substring(main_class_list,1,INSTR(main_class_list,'/')-1) as clss_type, substring(publication_date,1,4) as pub_year,count(patent_type) as cnt FROM patent.patent where substring(publication_date,1,4)<="+str(etime)+" "+"and substring(publication_date,1,4)>="+str(stime)+" "+"and id in"+myinput(list)+" "+"group by substring(main_class_list,1,INSTR(main_class_list,'/')-1),pub_year"      
    return sqlstr


def authorsql(list):#发明人分析sql语句
    sqlstr="select id,inventor_list from patent.patent where id in "+myinput(list)
    return sqlstr


def areasql(list):#地域分析sql语句
    sqlstr="select count(c2),c2 from(SELECT  applicant_area,CONCAT(substring(applicant_area,1,INSTR(applicant_area,';')-1) ,substring(applicant_area,1,INSTR(applicant_area,'(')-1))  as c2 FROM patent.patent where id in "+myinput(list)+" ) as ttt group by c2"
    return sqlstr


def timecal(data):#时间置信区间计算
    num=[]
    for i in data:
        num.append(int(i[1]))
    result=st.norm.interval(alpha=0.99,loc=np.mean(num),scale=st.sem(num))
    output=[]
    if int(result[0]) == int(result[1]):
        output.append(int(result[0])-1)
        output.append(int(result[1])+1)
    else:
        output.append(int(result[0]))
        output.append(int(result[1]))
    return output
    
    
def timesql(list):#置信区间计算SQL语句
    sqlstr="SELECT  id,substring(publication_date,1,4) as pub_year FROM patent.patent where id in "+myinput(list)
    return sqlstr

# #申请人分析
def author(list,type):
    db = mydb('152.136.114.189','zym','zym','patent',6336,'utf8')
    output=[]    
    sqls=authorsql(list)
    db.myexecu(sqls)
    dd=authoranaly(db,'234')
    dic=dd.authorlist()
    dic=dd.listsort(dic,myinput(list))
    if type == "bar":
       output.append(dd.authorbar(dic))
       db.endconn()
       return output     
    output.append(dd.authorpie(dic,'234'))
    db.endconn() 
    return output

# #趋势分析
def trend(list,type):
    db = mydb('152.136.114.189','zym','zym','patent',6336,'utf8')
    sqls=timesql(list)
    db.myexecu(sqls)
    timeblock=timecal(db.data)
    output=[]
    sqls=trendsql(timeblock[0],timeblock[1],list)
    db.myexecu(sqls)
    dd=trendanaly(db,"234")
    dic=dd.newdic(timeblock[0],timeblock[1])
    if type == "bar":
        output.append(dd.trendbar(dic,timeblock[0],timeblock[1]))
        return output
    if type == "line":
        output.append(dd.trendline(dic,timeblock[0],timeblock[1]))
        return output    
    for i in dd.trendpie(dic):
        output.append(i)
    db.endconn()
    return output
  
# #地域分析
def area(list,type):
    db = mydb('152.136.114.189','zym','zym','patent',6336,'utf8')
    output=[]
    sqls=areasql(list)
    db.myexecu(sqls)
    dd=areaanaly(db,'234')
    dic=dd.newdic()
    if type == "pie":
        output.append(dd.areapie(dic))
        db.endconn()
        return output
    output.append(dd.areabar(dic))
    db.endconn()
    return output

def analyze_by_list(patentIds, figType, anaType):#三个功能封装在一起
    if anaType == 'author':
        return author(patentIds,figType)
    if anaType == 'area':
        return area(patentIds,figType)
    return trend(patentIds,figType)








