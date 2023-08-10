import numpy as np
from models.recognize import Recognize
from django.db import connection
import fasttext
import fasttext.util

#加载fasttext
ft = fasttext.load_model('C:/Users/eStar.LAPTOP-T8EJFERU/Desktop/fasttext/wiki.zh/wiki.zh.bin')

class Recommendation:
    def __init__(self,first_n=1000,third_n=100):
        #当前用户ID
        self.userId=0
        #第一次过滤人数
        self.first_n=first_n
        #最终过滤人数
        self.third_n=third_n
        #最终返回实体数量
        self.num=0
        #所有用户信息
        self.User={}
        '''
        最终
        '''

    #连接数据库
    def connectDB(self):
        with connection.cursor()as cursor:
            sql = "select *from browsing_history"
            cursor.execute(sql)
            all = cursor.fetchall()
            return all
    #获取所有用户数据
    def getAllUser(self):
        all=self.connectDB()
        self.User={}
        #初步获得数据
        for row in all:
            #初始化
            if row[1] not in self.User:
                self.User[row[1]]={}
                #向量
                self.User[row[1]]['vector']=[row[3]]
                #最早时间
                self.User[row[1]]['earlyTime']=[row[2]]
                #最晚时间
                self.User[row[1]]['lateTime']=[]
                #处理分词
                for key in Recognize.recognize(row[4])['cut_dict']:
                    word=Recognize.recognize(row[4])['cut_dict'][key]['name']
                    self.User[row[1]]['data']=[[row[2],word,word]]
                #用户特征向量
                self.User[row[1]]['userVector']=[]
            else:
                #向量
                self.User[row[1]]['vector'].append(row[3])
                #最早时间
                self.User[row[1]]['earlyTime'].append(row[2])
                #处理分词
                for key in Recognize.recognize(row[4])['cut_dict']:
                    word=Recognize.recognize(row[4])['cut_dict'][key]['name']
                    self.User[row[1]]['data'].append([row[2],word,word])
        #数据化标签向量和最早最晚时间
        for key in self.User:
            self.User[key]['vector']=self.labelVector(self.User[key]['vector'])
            self.User[key]['earlyTime'],self.User[key]['lateTime']=self.userTime(self.User[key]['earlyTime'])
        #分词向量化
        for key in self.User:
            for d in self.User[key]['data']:
                d[2]=ft.get_word_vector(d[2])
        #赋值用户特征向量
        for key in self.User:
            self.User[key]['userVector']=self.userVector(self.User[key]['earlyTime'],self.User[key]['lateTime'],self.User[key]['data'])

    
    #标签向量函数
    def labelVector(self,label):
        #实体查询
        a=0
        #大学专业智能查询
        b=0
        #关系查询
        c=0
        for l in label:
            if l=='实体查询':
                a+=1
            elif l=='大学专业智能查询':
                b+=1
            elif l=='查关系':
                c+=1
        vector=np.array([a,b,c])
        return vector
    
    #获取最早和最晚时间
    def userTime(self,Time):
        earlyTime=Time[0]
        lateTime=Time[0]
        for t in Time:
            if t < earlyTime:
                earlyTime=t
            if t>lateTime:
                lateTime=t
        return earlyTime,lateTime
    
    #计算时间系数
    def timeFactor(self,earlyTime,lateTime,time):
        #转换为时间戳
        earlyTime=earlyTime.timestamp()
        lateTime=lateTime.timestamp()
        time=time.timestamp()
        #计算权重
        factor=(time-earlyTime)/(lateTime-earlyTime)
        return factor
    
    #计算用户特征向量
    def userVector(self,earlyTime,lateTime,data):
        vector=np.zeros(300)
        for d in data:
            vector+=(d[2]*self.timeFactor(earlyTime,lateTime,d[0]))
        return vector
    
    #计算欧氏距离
    def ouDistance(self,x,y):
        return np.sqrt(((x-y)**2).sum())
    
    #计算余弦相似度
    def costSimilar(self,x,y):
        dot_product = np.dot(x, y)
        norm1 = np.linalg.norm(x)
        norm2 = np.linalg.norm(y)
        similarity = dot_product / (norm1 * norm2)
        return similarity

    #初步过滤
    def first(self):
        firstUser=[]
        for key in self.User:
            if key!=self.userId:
                score=self.ouDistance(self.User[self.userId]['vector'],self.User[key]['vector'])*self.costSimilar(self.User[self.userId]['vector'],self.User[key]['vector'])
                firstUser.append([score,key])
        firstUser.sort(reverse=True)
        #取前1000个
        firstUser=firstUser[:self.first_n]
        return firstUser
    
    #二次过滤
    def second(self):
        secondUser=[]
        firstUser=self.first()
        for i in firstUser:
            item=[]
            for j in self.User[i[1]]['data']:
                #获取每个用户的浏览过的实体
                item.append(j[1])
            for key in self.User[self.userId]['data']:
                if key[1] in item:
                    secondUser.append(i[1])
                    break
        return secondUser
    
    #三次过滤
    def third(self):
        thirdUser=[]
        secondUser=self.second()
        for key in secondUser:
            score=self.ouDistance(self.User[self.userId]['userVector'],self.User[key]['userVector'])*self.costSimilar(self.User[self.userId]['userVector'],self.User[key]['userVector'])
            thirdUser.append([score,key])
        thirdUser.sort(reverse=True)
        #取前1000个
        thirdUser=thirdUser[:self.third_n]
        return thirdUser

    def recommendation(self,userId,num):
        self.userId=userId
        self.num=num
        #获取所用用户浏览记录
        self.getAllUser()
        #进行推荐
        thirdUser=self.third()
        #创建推荐字典
        recDict={}
        for t in thirdUser:
            #数据
            item=self.User[t[1]]['data']
            for i in item:
                if i[1] not in recDict:
                    recDict[i[1]]=t[0]
                else:
                    recDict[i[1]]+=t[0]
        #创建推荐列表
        reclist=[]
        for key in recDict:
            reclist.append([recDict[key],key])
        reclist.sort(reverse=True)
        reclist=reclist[:self.num]
        return reclist
    
# if __name__=="__main__":
#     R=Recommendation(1)
#     print(R.recommendation())
