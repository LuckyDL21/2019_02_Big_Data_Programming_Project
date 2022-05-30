#!/usr/bin/env python
# coding: utf-8

# In[5]:


from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import pandas as pd

import time
import threading

import matplotlib.pyplot as plt 
#import seaborn as sns
from selenium import webdriver

#from collections import Counter

import webbrowser
from datetime import datetime
import numpy as np
import folium
import json
import warnings
warnings.filterwarnings('ignore')


# In[6]:


window=Tk()


class startDust:
    
    def __init__(self,window):
        self.window=window
        
        self.window.title('전국 실시간 미세먼지')
        self.window.geometry('800x640')
        
        self.display()
        
    def display(self):
        
        self.label1=Label(self.window,text='우리 동네 미세먼지 검색',font=('함초롬돋움',10))
        self.label1.place(x=10,y=10)
        
        self.entry1=Entry(self.window,width=30)
        self.entry1.place(x=170,y=12)
        
        self.button1=Button(self.window,text='검색',command=self.click1)
        self.button1.place(x=400,y=12)
        
        
        info=Label(self.window,text='OO시 OO구 형식으로 입력해주세요 ex> 서울시 강남구 압구정동 ~~',font=('함초롬돋움',7),fg='blue')
        info.place(x=12,y=40)
        
        self.var2=StringVar()
        self.txt=Label(self.window,textvariable=self.var2)
        self.txt.place(x=15,y=80)
        
        
        
        self.now=datetime.now()
        self.time='%s시 %s분 기준'%(self.now.hour,self.now.minute)
        self.now_time=Label(self.window,text=self.time,font=('함초롬돋움',10))
        self.now_time.place(x=700,y=12)
        
        
        
        pic=PhotoImage(file='korea map.gif')
        picture=Label(self.window,image=pic)
        picture.image=pic
        picture.place(x=510,y=50)
        
        
        self.button2=Button(self.window,text='실시간 전국 미세먼지 지도',command=self.html1)
        self.button2.place(x=620,y=50)
        
        self.button3=Button(self.window,text='측정소별 미세먼지 지도',command=self.html2)
        self.button3.place(x=620,y=80)
        
        self.button4=Button(self.window,text='전국 미세먼지 측정소 위치',command=self.html3)
        self.button4.place(x=620,y=110)
        
        
        self.label2=Label(self.window,text='행정구역별 미세먼지 차이가 가장 큰지역 두곳 찾기',font=('함초롬돋움',10))
        self.label2.place(x=10,y=300)
        
        self.var=StringVar()
        self.txt=Label(self.window,textvariable=self.var,font=('함초롬돋움',12),fg='red')#행정구역별 차이 결과표시
        self.txt.place(x=15,y=360)
          
        self.str=StringVar()
        combo=ttk.Combobox(self.window,width=20,textvariable=self.str)
        combo['value']=('충남','경기','경북','충북','서울','전북','강원','대전','전남','인천','광주','경남','울산','세종','대구','제주','부산')
        
        combo.place(x=20,y=330)
        combo.current(0)
        
        action=ttk.Button(self.window,text='검색',command=self.action)
        action.place(x=200,y=330)
        
        
        self.topL=Label(self.window)
        self.topL.place(x=490,y=210)
        
        
        self.topL2=Label(self.window)
        self.topL2.place(x=490,y=405)
        

        self.get_info()
        
        
        
        
        
    def click1(self):# 우리동네 입력하면 찾아주는 기능 
        string=self.entry1.get()
        b=string.split(' ')[1]
        if len(b)>=3:
            if b[2]=='시' or  b[2]=='군' or  b[2]=='구':
                b=b[0]+b[1]
        if len(b)>=4:
            if b[3]=='시' or  b[3]=='군' or  b[3]=='구':
                b=b[0]+b[1]+b[2]
        
        
        dust_info=[[],[],[]]
        for n in self.df3.index:
            if b in self.df3.loc[n,'시군']:
                dust_info[0].append(self.df3.loc[n,'address'])
                dust_info[1].append(self.df3.loc[n,'fine dust'])
                dust_info[2].append(self.df3.loc[n,'dust value 1'])
        
        string=''
        for i in range(len(dust_info[0])):
            string=string+'\n'+dust_info[0][i]+'-'+dust_info[1][i]+':'+str(dust_info[2][i])

        self.var2.set(string)
                
        

    
    def action(self): #결과 알려주기 
        
        ax=[[],[]]
        for n in self.df3.index:
            if self.df3.loc[n,'지역']==self.str.get():
                ax[0].append(self.df3.loc[n,'dust value 1'])
                ax[1].append(self.df3.loc[n,'시군'])
        result='' 
        max_value=0
        min_value=200
        for i in range(len(ax[0])):
            if max_value<=ax[0][i]:
                max_value=ax[0][i]
                max_local=ax[1][i]
            if min_value>=ax[0][i]:
                min_value=ax[0][i]
                min_local=ax[1][i]
        result='최대:'+max_local+'-'+str(max_value)+'\n'+'최소:'+min_local+'-'+str(min_value)      
        self.var.set(result)
                

        
    def html1(self):
        webbrowser.open('dust_colormap.html')
        
    def html2(self):
        webbrowser.open('dust_mark.html')
    
    def html3(self):
        webbrowser.open('dust_station.html')
        


        
    def get_info(self): #미세먼지 데이터 실시간으로 불러오기 
        addr_list=[] #주소 저장 리스트 
        dust_list=[] #대기 정보 저장 리스트 
        for i in range(46):# 455개 정보 가져옴 (한페이지당 10개의 대기정보가 저장되어 있음)
            #url='https://dustfeel.com/station?c=205648&p='+str(i+1)
            url='https://dustfeel.com/station?p='+str(i+1)
            page=urlopen(url)
            #print(url)
            soup=BeautifulSoup(page,'html.parser')
            addr_text=soup.find_all('p','addr')
            dust_text=soup.find_all('div','dust_wrap')
            for j in range(len(addr_text)):
                addr_text[j]=addr_text[j].text#주소 문자열만 따옴(10개)
                dust_text[j]=dust_text[j].text
        
                #대기정보 문자열 전처리 
                dust_text[j]=dust_text[j].replace('\n','').replace('\xa0 ','').replace('미세먼지','').replace('-','').replace('초','').replace('㎍/㎥','')
                #이차원 리스트로 저장   [[미세분류,미세수치,초미세 분류,초미세 수치],.....]
                dust_list.append(dust_text[j].split())
        
  
            addr_list.extend(addr_text)#주소가 저장된 리스트 
        
        #주소 전처리 
        for i in range(len(addr_list)):
            if '도시대기' in addr_list[i]:
                addr_list[i]=addr_list[i].replace('도시대기','')
            elif '도로변대기' in addr_list[i]:
                addr_list[i]=addr_list[i].replace('도로변대기','')
            elif '옥상' in addr_list[i]:
                addr_list[i]=addr_list[i].replace('옥상','')
            elif '교외대기' in addr_list[i]:
                addr_list[i]=addr_list[i].replace('교외대기','')
                
        for i in range(len(dust_list)):
            if dust_list[i][0]=='정보없음' and dust_list[i][1]=='정보없음':
                dust_list[i].insert(1,-1) # 빈값에 -1대입 농도가 0보다 작은값을 가질 수 없다
                dust_list[i].insert(3,-1) # 초미세먼지
            elif dust_list[i][0]=='정보없음' and dust_list[i][1]!='정보없음' and dust_list[i][1]!=-1:
                dust_list[i].insert(1,-1) # 미세먼지
            elif dust_list[i][0]!='정보없음' and dust_list[i][2]=='정보없음':
                dust_list[i].insert(3,-1)#초미세먼지 
        
        for i in range(len(dust_list)):
            dust_list[i][1]=int(dust_list[i][1])
            dust_list[i][3]=int(dust_list[i][3])
            
        
        fine_dust_name,fine_dust=[],[]
        
        for i in range(len(dust_list)):
            fine_dust_name.append(dust_list[i][0])
            fine_dust.append(dust_list[i][1])
            
        
        dust_info={'address':addr_list,'fine dust':fine_dust_name,'dust value 1':fine_dust}
        
        self.df1=pd.DataFrame(dust_info)
        
        
        self.getcsv()
        
    def getcsv(self):
        #주소,위도,경도,지역,시군,ID 저장된 csv파일 불러오기
        self.df2=pd.read_csv('plus ID.csv',sep=',',encoding='cp949')
        #print(self.df2.head())
        #데이터 병합 열:주소,위도,경도,지역,시군,ID,미세먼지 class,미세먼지 
        self.df3=pd.merge(self.df1,self.df2,left_on='address',right_on='주소')
        del self.df3['주소']
        self.df3=self.df3[self.df3['dust value 1']!=-1]#정보없는 데이터 전처리 
        
        self.get_allpic()
        
        
    def get_allpic(self): #실시간 미세먼지 전국 지도 그리기  
        self.loc_data=pd.pivot_table(self.df3,index=['ID'],values=['dust value 1'],aggfunc=np.mean) 
        
        geo_path='05. skorea_municipalities_geo_simple.json'
        geo_str=json.load(open(geo_path,encoding='utf-8'))
        map=folium.Map(location=[36.2002,127.054],zoom_start=7)
        map.choropleth(geo_data=geo_str,
              data=self.loc_data['dust value 1'],
               columns=[self.loc_data.index,self.loc_data['dust value 1']],
               fill_color='PuRd',
               key_on='feature.id'
              )
        map.save('dust_colormap.html')
        
        self.get_markpic()
        
    def get_markpic(self):
        map1=folium.Map(location=[36.2002,127.054],zoom_start=7)
        
        for n in self.df3.index:
            dust_value=self.df3.loc[n,'dust value 1']
            
            if self.df3.loc[n,'fine dust']=='좋음':
                icon_color='blue'
            elif self.df3.loc[n,'fine dust']=='보통':
                icon_color='green'
            elif self.df3.loc[n,'fine dust']=='나쁨':
                icon_color='yellow'
            elif self.df3.loc[n,'fine dust']=='매우나쁨':
                icon_color='red'
                
            
            folium.CircleMarker(
                location=[self.df3.loc[n,'위도'],self.df3.loc[n,'경도']],
                radius=10,
                popup=dust_value,
                color=icon_color,
                fill=True,
                fill_color=icon_color
                
            ).add_to(map1)
            
        map1.save('dust_mark.html')
        
        self.top_bad()
        
        
    def top_bad(self): #가장 안좋은 지역 
        df4=self.df3.head()
        plt.rc('font', family='Malgun Gothic')
        plt.rc('xtick', labelsize=11)
        plt.title('미세먼지가 가장 안좋은 지역 TOP5')
        plt.ylabel('미세먼지 수치')
        plt.bar(df4['ID'],df4['dust value 1'],color='red')
        
        fig1=plt.gcf()
        fig1.savefig('bad_area.png',dpi=50)
        
        plt.clf()
        
        self.top_good()
        
        
    def top_good(self):#가장 좋은 지역 
        df5=self.df3.tail()
        df5=df5.sort_values(by=['dust value 1'],axis=0)
        plt.rc('font', family='Malgun Gothic')
        plt.title('미세먼지가 가장 좋은 지역 TOP5')
        plt.ylabel('미세먼지 수치')
        plt.bar(df5['ID'],df5['dust value 1'])
        
        fig2=plt.gcf()
        fig2.savefig('good_area.png',dpi=50)
        
        plt.clf()
        
        self.threadfunc()

    def threadfunc(self):
        toppic=PhotoImage(file='bad_area.png')
        self.topL.config(image=toppic)
        self.topL.image=toppic
        
        topgood=PhotoImage(file='good_area.png')
        self.topL2.config(image=topgood)
        self.topL2.image=topgood
        

        self.now=datetime.now()
        self.nowtime='%s시 %s분 기준'%(self.now.hour,self.now.minute)
        self.now_time.configure(text=self.nowtime)
        
        
        
        
        threading.Timer(3600,self.get_info).start() # 1시간 뒤 업데이트 

        
        



startDust(window)
window.mainloop()


# In[ ]:




