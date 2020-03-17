#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/4 14:29
# @Author  : Nelson
# @Site    : 
# @File    : scrapy_website.py
# @Software: PyCharm
'''
'''

from selenium import webdriver
import time
import pandas as pd

def switch_windows(driver):
    current_window = driver.current_window_handle
    all_window = driver.window_handles  # 返回当前会话中所有窗口的句柄。
    for window in all_window:  # 通过遍历判断要切换的窗口
        if window != current_window:
            driver.switch_to.window(window)  # 将定位焦点切换到指定的窗口，包含所有可切换焦点的选项

def compute(df):
    return str(str(df['行政区划代码'])[0:2]+'0000'),str(str(df['行政区划代码'])[:4]+'00')

def scrapy_website():
    start = time.time()
    base_url = "http://www.mca.gov.cn/article/sj/xzqh/1980/"
    driver = webdriver.Chrome()
    driver.get(base_url)
    driver.find_element_by_xpath('//*[@id="list_content"]/div[2]/div/ul/table/tbody/tr[1]/td[2]/a').click()
    switch_windows(driver)
    driver.find_element_by_xpath('//*[@id="zoom"]/p[1]/a').click()
    switch_windows(driver)
    website_detail = driver.find_element_by_xpath('/html/body').text
    number = 1
    data_dic = dict()
    for i in str(website_detail).split('\n'):
        if number==1:
            table_name = i
            number +=1
        else:
            division = str(i).split(' ')
            if '注' in division[0].strip(' '):
                break
            elif '行政区划代码' in division[0].strip(' '):
                continue
            else:
                data_dic[division[0].strip(' ')] = division[-1].strip(' ')
    df = pd.DataFrame(list(data_dic.items()))
    df = df.rename(columns={0:'行政区划代码',1:'单位名称'})
    df[['省级行政区划代码','市级行政区划代码']]= df.apply(compute, axis=1, result_type="expand")
    df_bak = df[['行政区划代码','单位名称']]
    df = df.merge(df_bak,how='left',left_on='省级行政区划代码',right_on='行政区划代码')
    df = df.merge(df_bak,how='left',left_on='市级行政区划代码',right_on='行政区划代码')
    df.columns = ['行政区划代码', '单位名称','省级行政区划代码','市级行政区划代码','省级行政区划代码_','省级行政单位','市级行政区划代码_','市级行政单位']
    df = df[['行政区划代码', '单位名称','省级行政区划代码','省级行政单位','市级行政区划代码','市级行政单位']]
    df.to_csv('{}.csv'.format(table_name),encoding='utf-8-sig',index=False)
    end = time.time()
    print('爬取耗费时间：{} s'.format(str(end - start)))

if __name__ == '__main__':
    scrapy_website()

