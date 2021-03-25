#-*- coding:utf-8 -*-


import csv
import time
from math import exp
from math import log

import os
import bs4
import sys
import urllib.request

import pandas as pd
import requests
import math
from selenium import webdriver

import re

from IPython.display import display

from collections import Counter
import pymysql
import requests
import json
import threading

import datetime


def Crawling_analyze(word_input, now_time):
    coloumn_meta = ["meta_keywords", "meta_description", "review_count", "buy_count",
                    "registration_date", "dib_count", "link"]
    df = pd.DataFrame(index=range(1, 30), columns=coloumn_meta)
    word = word_input
    n = 0
    n_div = 1
    p = 0
    now = datetime.datetime.now().date()

    sql_input = "INSERT INTO seo_keyword (keyword, search_date) VALUES (%s, %s)"
    cursor.execute('set names utf8mb4')
    cursor.execute(sql_input, (inputword, now_time))
    connection.commit()
    rank = 0
    for i in range(1):
        p = p + 1
        url = "https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={0}&pagingIndex={1}&pagingSize=40&productSet=total&query={2}&sort=rel&timestamp=&viewType=lists".format(
            str(word), str(p), str(word))

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('lang=ko_KR')
        prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'plugins': 2, 'popups': 2,
                                                            'geolocation': 2, 'notifications': 2,
                                                            'auto_select_certificate': 2, 'fullscreen': 2,
                                                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                            'media_stream_mic': 2, 'media_stream_camera': 2,
                                                            'protocol_handlers': 2, 'ppapi_broker': 2,
                                                            'automatic_downloads': 2, 'midi_sysex': 2,
                                                            'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                            'metro_switch_to_desktop': 2,
                                                            'protected_media_identifier': 2, 'app_banner': 2,
                                                            'site_engagement': 2, 'durable_storage': 2}}
        chrome_options.add_experimental_option('prefs', prefs)
        browser = webdriver.Chrome('chromedriver', options=chrome_options)
        browser.implicitly_wait(1)
        browser.get(url)

        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(0.5)

            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        r = browser.page_source
        browser.close()

        bs4_r = bs4.BeautifulSoup(r, "lxml")

        div_select = bs4_r.select('ul.list_basis > div > div')

        for J in range(len(div_select)):

            div_inner = div_select[J]
            a_href = div_inner.select('li > div > div:nth-of-type(2) > div:nth-of-type(1) > a ')
            a_href = a_href[0]

            temp_url = a_href.attrs['href']

            if 'adcr.naver.com' in temp_url:
                n_div = n_div + 1
                continue
            else:
                pass

            r_temp = requests.get(temp_url)
            r_temp_status = str(r_temp.status_code)

            if int(r_temp_status[0]) == 2:
                pass
            else:
                n = n + 1
                continue

            bs4_r_temp = bs4.BeautifulSoup(r_temp.text, "lxml")

            n = n + 1

            if 'search.shopping.naver.com' in requests.get(temp_url).url:
                div_inner_temp = bs4_r_temp.find('div', class_='buyButton_compare_wrap__7LRui')
                if div_inner_temp == None:
                    n = n + 1
                    continue
                else:
                    pass

                div_inner_temp = div_inner_temp.select('a')
                temp_url = div_inner_temp[0].attrs['href']

            else:
                temp_url = a_href.attrs['href']
                pass

            browser = webdriver.Chrome('chromedriver', options=chrome_options)
            browser.get(temp_url)

            temp_url = browser.current_url
            temp_html = browser.page_source
            browser.close()

            bs4_r_temp = bs4.BeautifulSoup(temp_html, "lxml")
            print(type(bs4_r_temp))

            redirect_method = bs4_r_temp.select('p')
            if '선택하신 상품은 일시 품절이거나' in str(redirect_method):
                continue
            else:
                if '동시에 접속하는 이용자' in str(redirect_method):
                    continue
                else:
                    pass
                pass

            ## 이부분은 리다이렉션 페이지로 넘어가기 위한 URL추출 작업이 필요한 곳입니다 확인하여 주십시오
            ## 확인 필수
            ## 확인 필수 targetUrl 부분 특히
            if '해당 쇼핑몰로 이동중입니다.' in str(redirect_method):
                bs4_r_temp.find('targetUrl')
                temp_url = bs4_r_temp.select_one('script')
                match = re.search(r'targetUrl = \"(.+?)\"', str(temp_url)).group(1)
                temp_url = match
                browser = webdriver.Chrome('chromedriver', options=chrome_options)
                browser.implicitly_wait(1)
                browser.get(temp_url)

                try:
                    result = browser.switch_to_alert()
                    print(result.text)
                    result.accept()
                    result.dismiss()
                    pass

                except:
                    pass

                temp_url = browser.current_url
                temp_html = browser.page_source
                bs4_r_temp = bs4.BeautifulSoup(temp_html, "lxml")
                browser.close()
            else:
                pass

            temp_review = None
            temp_keyword = None
            temp_day = None
            temp_dib = None
            temp_buy = None
            temp_description = None

            meta_inner_keywords = bs4_r_temp.find('meta', {'name': 'keywords'})
            meta_inner_title = bs4_r_temp.find('meta', {'name': 'title'})
            if meta_inner_keywords is None:
                if bs4_r_temp.find('meta', {'property': 'og:keywords'}) is None:
                    if meta_inner_title is None:
                        if bs4_r_temp.find('meta', {'property': 'og:title'}) is None:
                            pass
                        else:
                            meta_inner_title = bs4_r_temp.find('meta', {'property': 'og:title'})
                            temp_keyword = meta_inner_title.get('content')
                            pass
                    else:
                        temp_keyword = meta_inner_title.get('content')
                    pass
                else:
                    meta_inner_keywords = bs4_r_temp.find('meta', {'property': 'og:keywords'})
                    temp_keyword = meta_inner_keywords.get('content')
                pass
            else:
                temp_keyword = meta_inner_keywords.get('content')

            meta_inner_description = bs4_r_temp.find('meta', {'name': 'description'})
            if meta_inner_description is None:
                if bs4_r_temp.find('meta', {'property': 'og:description'}) is None:
                    pass
                else:
                    meta_inner_description = bs4_r_temp.find('meta', {'property': 'og:description'})
                    temp_description = meta_inner_description.get('content')
                pass
            else:
                temp_description = meta_inner_description.get('content')

            if temp_keyword is None:
                meta_inner_keywords = bs4_r_temp.find('meta', {'property': 'og:title'})
                if meta_inner_keywords is None:
                    pass
                else:
                    meta_inner_keywords = bs4_r_temp.find('meta', {'property': 'og:title'})
                    temp_keyword = meta_inner_keywords.get('content')
            else:
                pass

            div_metas_many = div_inner.select('li > div > div:nth-of-type(2) > div:nth-of-type(5)')

            a_inner_div_review = div_metas_many[0].select('a:nth-of-type(1) > em')
            if a_inner_div_review == []:
                temp_review = 0
            else:
                a_inner_review = a_inner_div_review[0]
                temp_review = a_inner_review.text
            temp_review = re.findall('[0-9\,]+', str(temp_review))

            a_inner_div_buy = div_metas_many[0].select('a:nth-of-type(2) > em')
            if a_inner_div_buy == []:
                temp_buy = 0
            else:
                a_inner_buy = a_inner_div_buy[0]
                temp_buy = a_inner_buy.text
            temp_buy = re.findall('[0-9\,]+', str(temp_buy))

            # span_inner_day = div_metas_many[0].select('div > span:nth-of-type(1)')
            span_inner_day = div_metas_many[0].select('span.basicList_etc__2uAYO')
            if span_inner_day[0] == []:
                temp_day = '0000.00.'
            else:
                temp_day = span_inner_day[0].text
            temp_day = re.findall('[0-9\.]+', str(temp_day))

            em_inner_dib = div_metas_many[0].select(
                'button > span > em')
            if em_inner_dib == []:
                temp_dib = 0
            else:
                temp_dib = em_inner_dib[0].text
                temp_dib = re.findall('[0-9\,]+', str(temp_dib))

            df.loc[n, 'link'] = temp_url
            df.loc[n, 'meta_keywords'] = temp_keyword
            df.loc[n, 'meta_description'] = temp_description
            df.loc[n, 'review_count'] = temp_review
            df.loc[n, 'dib_count'] = temp_dib
            df.loc[n, 'buy_count'] = temp_buy
            df.loc[n, 'registration_date'] = temp_day
            print(temp_url)
            print(df.loc[n])

            rank = rank + 1

            try:
                sql_input = "INSERT INTO seo_keyword_table (created_date, main_keyword, meta_keyword, meta_description, review_count, buy_count, registration_date, dib_count, link, rank) \
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute('set names utf8mb4')
                cursor.execute(sql_input, (
                    now_time, inputword, temp_keyword, temp_description, temp_review, temp_buy, temp_day, temp_dib,
                    temp_url, rank))
                connection.commit()
            except:
                error = 'error'
                sql_input = "INSERT INTO seo_keyword_table (created_date, main_keyword, meta_keyword, meta_description, review_count, buy_count, registration_date, dib_count, link, rank) \
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute('set names utf8mb4')
                cursor.execute(sql_input, (
                    now_time, error, error, error, error, error, error, error, error, error))
                connection.commit()

            n_div = n_div + 1

    browser.quit()

    return df


def calc(df, input_word, now_time):
    def tf(t, d):
        return d.count(t)

    def idf(t):
        df = 0
        for doc in docs:
            if type(doc) == float:
                pass
            elif doc is None:
                pass
            else:
                df += t in doc
        return log(N / (df + 1))

    def tfidf(t, d):
        return tf(t, d) * idf(t)

    import numpy as np

    docs = []
    df = df.dropna(axis=0)
    docs = list(np.array(df["meta_keywords"].tolist()))
    docs_sep = []

    docs_range = str(len(docs))

    for k in range(len(docs)):
        n = 0
        sep_data = docs[k]
        if sep_data is None:
            pass
        elif sep_data == '':
            pass
        else:
            if sep_data.find(",") == -1:
                sep_data = list(sep_data.split(" "))
            else:
                sep_data = list(sep_data.split(","))

        print('############')
        print(docs[k])
        print(sep_data)

        n = n + 1
        if sep_data is None:
            pass
        else:
            for a in range(len(sep_data)):
                docs_sep.append(sep_data[a])


    count = Counter(docs_sep)
    count = count.most_common()

    count_list = count
    try:
        os.remove("tf_idf_value_" + input_word + ".csv")
    except:
        pass

    csvfile = open("tf_idf_value_" + input_word + ".csv", 'w', newline='', encoding="utf-8-sig")

    csvwriter = csv.writer(csvfile)
    for row in count:
        if '' in row:
            pass
        else:
            csvwriter.writerow(row)

    csvfile.close()

    csvfile = pd.read_csv("tf_idf_value_" + input_word + ".csv", encoding="utf-8-sig")

    count_list = [x[0] for x in count_list]
    for a in range(0, len(count_list) - 1):
        if count_list[a] == '':
            del count_list[a]
        else:
            pass

    df = docs

    N = len(docs)

    result = []
    for j in range(len(count_list)):
        t = count_list[j]
        result.append(idf(t))

    idf_output = pd.DataFrame(result, index=count_list, columns=["IDF"])
    display(idf_output)

    result = []
    for i in range(N):
        result.append([])
        d = docs[i]
        for j in range(len(count_list)):
            t = count_list[j]

            result[-1].append(tfidf(t, d))

    tfidf_output = pd.DataFrame(result, columns=count_list)
    display(tfidf_output)

    result = []
    for i in range(N):  # 각 문서에 대해서 아래 명령을 수행
        result.append([])
        d = docs[i]
        for j in range(len(count_list)):
            t = count_list[j]
            result[-1].append(tf(t, d))

    tf_ = pd.DataFrame(result, columns=count_list)
    m = tf_ > 1
    tf_[m] = 1

    display(tf_)

    idf_output.sort_values(by=['IDF'], axis=0)
    df_example = tf_.values

    result = []
    for i in range(N):
        result.append([])
        d = docs[i]
        for j in range(len(count_list)):
            t = count_list[j]

            result[-1].append(tfidf(t, d))

    tfidf_output = pd.DataFrame(result, columns=count_list)

    AR_IIF_RESULT = []
    for a in range(len(idf_output)):
        index_words = idf_output.loc[:].index.values
        iif_word = index_words[a]

        index_val = tf_.loc[tf_.loc[:, iif_word] == 1, :].index.values

        AR = 0
        add_val = 0
        for i in range(len(index_val)):
            if index_val[i] <= len(docs) / 2:
                add_val = add_val + (len(docs) / 2) - int(index_val[i])
            else:
                add_val = add_val + (round(exp((len(docs) / 2) - index_val[i]), 2) - 1)

        ##AR = index_val.size / add_val
        AR = add_val / index_val.size
        AR_IIF = (idf_output.loc[iif_word] * AR)
        AR_IIF = re.findall('[0-9]+\.+[0-9]', str(AR_IIF))

        AR_IIF = AR_IIF[0]
        AR_IIF_RESULT.append((iif_word, int(float(AR_IIF))))

    ##sorted(AR_IIF_RESULT)
    AR_IIF_RESULT = pd.DataFrame(AR_IIF_RESULT)
    AR_IIF_RESULT.columns = ['keyword', 'AR_IIF']

    AR_IIF_RESULT.sort_values(by=['AR_IIF'], axis=0, ascending=False, inplace=True)
    ##AR_IIF_RESULT.sort_values(by='AR_IIF', axis=0
    # AR_IIF_RESULT = AR_IIF_RESULT.head(n=30)

    send_keyword_x = list(AR_IIF_RESULT.index.values)
    send_values_y = []

    for i in range(len(AR_IIF_RESULT)):
        send_values_y.append(AR_IIF_RESULT['AR_IIF'].iloc[i])

    rank = 0
    print(AR_IIF_RESULT)
    sql_input = "INSERT INTO seo_iif (keyword, search_date, iif, main_keyword) \
                 VALUES (%s, %s, %s, %s)"

    for i in range(len(AR_IIF_RESULT)):
        rank = rank + 1
        cursor.execute('set names utf8mb4')
        cursor.execute(sql_input, (AR_IIF_RESULT.iloc[i, 0], now_time, AR_IIF_RESULT.iloc[i, 1], inputword))
        connection.commit()

    return AR_IIF_RESULT

def naverapi():
    client_id = "2vkLtRkXlOPYXN6e8QIY"
    client_secret = "2_IrnPBJGE"
    url = "https://openapi.naver.com/v1/datalab/search";
    body = "{\"startDate\":\"2017-01-01\",\"endDate\":\"2017-04-30\",\"timeUnit\":\"month\",\"keywordGroups\":[{\"groupName\":\"한글\",\"keywords\":[\"한글\",\"korean\"]},{\"groupName\":\"영어\",\"keywords\":[\"영어\",\"english\"]}],\"device\":\"pc\",\"ages\":[\"1\",\"2\"],\"gender\":\"f\"}";

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)

if __name__ == '__main__':
    connection = pymysql.connect(
        host='',
        user='',
        password='',
        db='',
        charset='utf8',
    )

    cursor = connection.cursor()

    print("Write word you want to find")
    naverapi_word= naverapi()
    inputword = input()
    now_time = datetime.datetime.now()

    Crawling_data = Crawling_analyze(inputword, now_time)
    Calc_data = calc(Crawling_data, inputword, now_time)
