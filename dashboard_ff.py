# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 09:10:17 2024

@author: 유국현
"""

import streamlit as st
import io
import os
import zipfile
import pandas as pd
from googleapiclient.discovery import build
import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from  selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
from bs4 import BeautifulSoup
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
    col = ['comment', 'author', 'date', 'num_likes']
    df = pd.DataFrame(comments, columns=col)

    return df
    #df.to_csv(directory+'/'+path+'/'+file_name+'.csv', index=None)
    
def getNavernewsReply(url, num , path, wait_time=5, delay_time=0.1):
    def installff():
        os.system('sbase install geckodriver')
        os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

    _ = installff()
    service = Service(GeckoDriverManager().install())
    options = Options() 
    options.add_argument("--headless=new")
    #options.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'

    driver = webdriver.Firefox(options=options, service=service)
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
    return df
    #df.to_csv(directory+'/'+path+'/'+'naver_'+str(num)+'.csv')

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8-sig')
    
tab1, tab2, tab3 = st.tabs(["You tube", "Naver", "URL All"])

with tab1:
    url_you = st.text_input("Youtube Link")
    api_you = st.text_input("API Key")
    videoid = url_you.split("=")[-1]

    if st.button("Crawl Youtube"):
        with st.spinner('Wait for it...'):
            df = youtubeReplyCrawler(url_you, api_you, "youtube")
        st.success('Done!')
        csv = convert_df(df)
        st.download_button(
            "Press Download",
            csv,
            videoid + ".csv",
            key="download_csv")


with tab2:
    url_naver = st.text_input("Naver Reply Link")
    num       = st.text_input("Comment")
    
    if st.button("Crawl Naver News Reply"):
        with st.spinner('Wait for it...'):
            df = getNavernewsReply(url_naver, num, "naver", wait_time=5, delay_time=0.1)
        st.success('Done!')
        csv = convert_df(df)
        st.download_button(
            "Press Download",
            csv,
            "naver_"+str(num) + ".csv",
            key="download_csv")

with tab3:

    api_yous = st.text_input("You Tube API Key")
    uploaded_files_url =  st.file_uploader("Upload your urls",type=['csv'],accept_multiple_files=False)
    
    if st.button("Crawl All Reply"):
        urls_all = pd.read_csv(uploaded_files_url)
        
        sel_url = urls_all["urls"]
        
        buf = io.BytesIO()
        with zipfile.ZipFile(buf,"x") as csv_zip:
            progress_text = "Now calculating"
            my_bar = st.progress(0.0, text=progress_text)
            for k in range(len(sel_url)):
                time.sleep(0.02)
                my_bar.progress(100*(k)//len(sel_url))
                if "youtube" in sel_url[k]:
                    url_you = sel_url[k]
                    df = youtubeReplyCrawler(url_you, api_yous, "all")
                    videoid = url_you.split("=")[-1]
                    csv_zip.writestr(videoid + ".csv",df.to_csv(index=False).encode('utf-8-sig'))
                    
                elif "naver" in sel_url[k]:
                    url_naver = sel_url[k]
                    df = getNavernewsReply(url_naver, k, "all", wait_time=5, delay_time=0.1)
                    csv = convert_df(df)
                    csv_zip.writestr("naver_"+str(k) + ".csv",df.to_csv(index=False).encode('utf-8-sig'))



        st.download_button(
                        label = "Download zip",
                        data = buf.getvalue(),
                        file_name = "mydownload.zip"
                        )
        st.balloons()
                
                
            
            
            
            
            
