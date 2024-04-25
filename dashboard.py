# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:04:22 2024

@author: 유국현
"""

import streamlit as st
import os
import pandas as pd
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from  selenium.webdriver.common.by  import  By
import time
from bs4 import BeautifulSoup

st.title("Reply Crawler")

def youtubeReplyCrawler(url, api_key, path):
    comments = list()
    api_obj = build('youtube', 'v3', developerKey=api_key)
    
    videoid = url.split("=")[-1]
    
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=videoid,maxResults=10000).execute()
    
    
    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([comment['textDisplay'], comment['authorDisplayName'], comment['publishedAt'], comment['likeCount']])
     
            if item['snippet']['totalReplyCount'] > 0:
                for reply_item in item['replies']['comments']:
                    reply = reply_item['snippet']
                    comments.append([reply['textDisplay'], reply['authorDisplayName'], reply['publishedAt'], reply['likeCount']])
     
        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=videoid, pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            break
    
    df = pd.DataFrame(comments)
    file_name = url_you.split("=")[-1]
    #return df
    df.to_excel('./'+path+'/'+file_name+'.xlsx', header=['comment', 'author', 'date', 'num_likes'], index=None)
    
def getNavernewsReply(url, num , path, wait_time=5, delay_time=0.1):

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(wait_time)
    driver.get(url)

    while True:
        try:
            more  =  driver.find_element(By.CLASS_NAME,  'u_cbox_btn_more')
            more.click()
            time.sleep(delay_time)

        except:
            break
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    nicknames = soup.select('span.u_cbox_nick')
    list_nicknames = [nickname.text for nickname in nicknames]

    datetimes = soup.select('span.u_cbox_date')
    list_datetimes = [datetime.text for datetime in datetimes]

    contents = soup.select('span.u_cbox_contents') 
    list_contents = [content.text for content in contents]


    list_sum = list(zip(list_nicknames,list_datetimes,list_contents))

    driver.quit()
    col = ['작성자','시간','내용']

    df = pd.DataFrame(list_sum, columns=col)
    df.to_excel('./'+path+'/'+'naver_'+str(num)+'.xlsx', sheet_name='뉴스 기사 제목')

def domainFinder(sel_url_unit):
    domain = sel_url_unit.split(".")[1]
    return domain
    
    
tab1, tab2, tab3 = st.tabs(["You tube", "Naver", "URL All"])

with tab1:
    directory = os.getcwd()
    print(directory)
    url_you = st.text_input("Youtube Link")
    api_you = st.text_input("API Key")
    if st.button("Change Youtube Directory"):
        #os.chdir(directory)
        if 'youtube' not in os.listdir(directory):
            os.mkdir(directory+"/youtube/")

    if st.button("Crawl Youtube"):
        with st.spinner('Wait for it...'):
            df = youtubeReplyCrawler(url_you, api_you, "youtube")
        st.success('Done!')

with tab2:
    directory = os.getcwd()
    print(directory)
    url_naver = st.text_input("Naver Reply Link")
    num       = st.text_input("Comment")
    
    if st.button("Change Naver Directory"):
        #os.chdir(directory)
        if 'naver' not in os.listdir(directory):
            os.mkdir(directory+"/naver/")
        
    if st.button("Crawl Naver News Reply"):
        with st.spinner('Wait for it...'):
            df = getNavernewsReply(url_naver, num, "naver", wait_time=5, delay_time=0.1)
        st.success('Done!')

with tab3:
    directory = os.getcwd()
    print(directory)
    api_yous = st.text_input("You Tube API Key")
    uploaded_files_url =  st.file_uploader("Upload your urls",type=['csv'],accept_multiple_files=False)
    
    if st.button("Change Directory"):
        #os.chdir(directory)
        if 'all' not in os.listdir(directory):
            os.mkdir(directory+"/all/")
        
    if st.button("Crawl All Reply"):
        urls_all = pd.read_csv(uploaded_files_url)
        
        sel_url = urls_all["urls"]
        progress_text = "Doing some heavy computations..."
        my_bar = st.progress(0.0, text=progress_text)
        for k in range(len(sel_url)):
            time.sleep(0.02)
            my_bar.progress(100*(k)//len(sel_url))
            if "youtube" in sel_url[k]:
                url_you = sel_url[k]
                df = youtubeReplyCrawler(url_you, api_yous, "all")
            elif "naver" in sel_url[k]:
                url_naver = sel_url[k]
                df = getNavernewsReply(url_naver, k, "all", wait_time=5, delay_time=0.1)
        st.balloons()
                
                
            
            
            
            
            
