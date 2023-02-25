
from bs4 import BeautifulSoup
import requests
import re
import datetime
import pandas as pd
from tqdm import tqdm

def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num + 1
    else:
        return num + 9 * (num - 1)

def makeUrl(search, start_pg, end_pg):
    if start_pg == end_pg:
        start_page = makePgNum(start_pg)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(
            start_page)
        print("생성url: ", url)
        return url
    else:
        urls = []
        for i in range(start_pg, end_pg + 1):
            page = makePgNum(i)
            url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page)
            urls.append(url)
        print("생성url: ", urls)
        return urls

def news_attrs_crawler(articles, attrs):
    attrs_content = []
    for i in articles:
        attrs_content.append(i.attrs[attrs])
    return attrs_content

# ConnectionError방지
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}


# html생성해서 기사크롤링하는 함수 만들기(url): 링크를 반환
def articles_crawler(url):
    # html 불러오기
    original_html = requests.get(i, headers=headers)
    html = BeautifulSoup(original_html.text, "html.parser")

    url_naver = html.select(
        "div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
    url = news_attrs_crawler(url_naver, 'href')
    return url


search ="삼쩜삼"
page = 1
page2 = 3


# naver url 생성
url = makeUrl(search, page, page2)

# 뉴스 크롤러 실행
news_titles = []
news_url = []
news_contents = []
news_dates = []
for i in url:
    url = articles_crawler(url)
    news_url.append(url)


# 제목, 링크, 내용 1차원 리스트로 꺼내는 함수 생성
def makeList(newlist, content):
    for i in content:
        for j in i:
            newlist.append(j)
    return newlist


# 제목, 링크, 내용 담을 리스트 생성
news_url_1 = []

# 1차원 리스트로 만들기(내용 제외)
makeList(news_url_1, news_url)

# NAVER 뉴스만 남기기
final_urls = []
for i in tqdm(range(len(news_url_1))):
    #20개까지만 목록 노출
    if len(final_urls) >= 20:
        break

    if "news.naver.com" in news_url_1[i]:
        final_urls.append(news_url_1[i])
    else:
        pass

# 뉴스 내용 크롤링

for i in tqdm(final_urls):
    # 각 기사 html get하기
    news = requests.get(i, headers=headers)
    news_html = BeautifulSoup(news.text, "html.parser")

    # 뉴스 제목 가져오기
    title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
    if title == None:
        title = news_html.select_one("#content > div.end_ct > div > h2")

    # html태그제거 및 텍스트 다듬기
    pattern1 = '<[^>]*>'
    title = re.sub(pattern=pattern1, repl='', string=str(title))
    pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""


    news_titles.append(title)


    try:
        html_date = news_html.select_one(
            "div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
        news_date = html_date.attrs['data-date-time']
    except AttributeError:
        news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
        news_date = re.sub(pattern=pattern1, repl='', string=str(news_date))
    # 날짜 가져오기
    news_dates.append(news_date)

print("검색된 기사 갯수: 총 ", (page2 + 1 - page) * 10, '개')
print("\n[뉴스 제목]")
print(news_titles)
print("\n[뉴스 링크]")
print(final_urls)


print('news_title: ', len(news_titles))
print('news_url: ', len(final_urls))
print('news_dates: ', len(news_dates))

# 데이터 프레임 만들기
news_df = pd.DataFrame({'date': news_dates, 'title': news_titles, 'link': final_urls})

# 데이터 프레임 저장
now = datetime.datetime.now()
news_df.to_csv('{}_{}.csv'.format(search, now.strftime('%Y%m%d_%H시%M분%S초')), encoding='utf-8-sig', index=False)